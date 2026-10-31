from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Item, Claim, Notification
from .forms import ItemForm, ItemEditForm, ClaimForm, ItemSearchForm


def home(request):
    """Landing page with recent items and stats."""
    recent_lost = Item.objects.filter(item_type='lost').exclude(status='returned')[:6]
    recent_found = Item.objects.filter(item_type='found').exclude(status='returned')[:6]
    total_lost = Item.objects.filter(item_type='lost').count()
    total_found = Item.objects.filter(item_type='found').count()
    total_returned = Item.objects.filter(status='returned').count()
    total_users = Item.objects.values('user').distinct().count()

    context = {
        'recent_lost': recent_lost,
        'recent_found': recent_found,
        'total_lost': total_lost,
        'total_found': total_found,
        'total_returned': total_returned,
        'total_users': total_users,
    }
    return render(request, 'items/home.html', context)


def item_list(request):
    """List all items with search and filtering."""
    items = Item.objects.select_related('user', 'category').all()
    form = ItemSearchForm(request.GET)
    form.is_valid()

    query = request.GET.get('query', '').strip()
    item_type = request.GET.get('item_type', '').strip()
    category = form.cleaned_data.get('category')
    category_id = str(category.pk) if category else ''
    status = request.GET.get('status', '').strip()

    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    if item_type:
        items = items.filter(item_type=item_type)
    if category:
        items = items.filter(category=category)
    if status:
        items = items.filter(status=status)

    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
        'query': query,
        'selected_type': item_type,
        'selected_category': category_id,
        'selected_status': status,
        'total_results': paginator.count,
    }
    return render(request, 'items/item_list.html', context)


def item_detail(request, pk):
    """View a single item with its claims."""
    item = get_object_or_404(Item.objects.select_related('user', 'category'), pk=pk)
    claims = item.claims.select_related('claimant').all() if request.user == item.user or request.user.is_staff else None
    user_has_claimed = False
    if request.user.is_authenticated:
        user_has_claimed = Claim.objects.filter(item=item, claimant=request.user).exists()

    context = {
        'item': item,
        'claims': claims,
        'user_has_claimed': user_has_claimed,
    }
    return render(request, 'items/item_detail.html', context)


@login_required
def report_item(request):
    """Report a lost or found item."""
    item_type = request.GET.get('type', 'lost')
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'Your {item.get_item_type_display().lower()} item report has been submitted successfully!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(initial={'item_type': item_type})

    context = {
        'form': form,
        'item_type': item_type,
    }
    return render(request, 'items/report_item.html', context)


@login_required
def edit_item(request, pk):
    """Edit an existing item report. Only the owner can edit."""
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ItemEditForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item report updated successfully!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemEditForm(instance=item)

    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'items/edit_item.html', context)


@login_required
def delete_item(request, pk):
    """Delete an item report. Only the owner can delete."""
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item report deleted successfully.')
        return redirect('dashboard')

    return render(request, 'items/delete_item.html', {'item': item})


@login_required
def submit_claim(request, item_pk):
    """Submit a claim on an item."""
    item = get_object_or_404(Item, pk=item_pk)

    # Prevent claiming own item
    if item.user == request.user:
        messages.error(request, 'You cannot claim your own item.')
        return redirect('item_detail', pk=item.pk)

    # Prevent duplicate claims
    if Claim.objects.filter(item=item, claimant=request.user).exists():
        messages.warning(request, 'You have already submitted a claim for this item.')
        return redirect('item_detail', pk=item.pk)

    # Prevent claiming returned items
    if item.status == 'returned':
        messages.warning(request, 'This item has already been returned.')
        return redirect('item_detail', pk=item.pk)

    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimant = request.user
            claim.save()
            # Update item status
            item.status = 'claim_pending'
            item.save()
            # Notify item owner
            Notification.objects.create(
                user=item.user,
                title='New Claim on Your Item',
                message=f'{request.user.get_full_name() or request.user.username} has submitted a claim on your item "{item.name}".',
                link=f'/items/{item.pk}/'
            )
            messages.success(request, 'Your claim has been submitted successfully! An admin will review it.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ClaimForm()

    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'items/submit_claim.html', context)


@login_required
def dashboard(request):
    """User dashboard showing personal items and claims."""
    user_items = Item.objects.filter(user=request.user)
    user_claims = Claim.objects.filter(claimant=request.user).select_related('item')

    # Stats
    total_items = user_items.count()
    lost_count = user_items.filter(item_type='lost').count()
    found_count = user_items.filter(item_type='found').count()
    pending_claims = user_claims.filter(status='pending').count()
    approved_claims = user_claims.filter(status='approved').count()

    context = {
        'user_items': user_items,
        'user_claims': user_claims,
        'total_items': total_items,
        'lost_count': lost_count,
        'found_count': found_count,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
    }
    return render(request, 'items/dashboard.html', context)


@login_required
def notifications(request):
    """View user notifications."""
    user_notifications = Notification.objects.filter(user=request.user)

    context = {
        'notifications': user_notifications,
    }
    return render(request, 'items/notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


# ---- Admin Views ----

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard for reviewing claims and managing the platform."""
    pending_claims = Claim.objects.filter(status='pending').select_related('item', 'claimant')
    all_claims = Claim.objects.select_related('item', 'claimant').all()

    # Stats
    total_items = Item.objects.count()
    total_lost = Item.objects.filter(item_type='lost').count()
    total_found = Item.objects.filter(item_type='found').count()
    total_returned = Item.objects.filter(status='returned').count()
    total_claims = all_claims.count()
    pending_count = pending_claims.count()
    approved_count = Claim.objects.filter(status='approved').count()
    rejected_count = Claim.objects.filter(status='rejected').count()

    # Category breakdown
    category_stats = Item.objects.values('category__name').annotate(count=Count('id')).order_by('-count')[:10]

    context = {
        'pending_claims': pending_claims,
        'all_claims': all_claims,
        'total_items': total_items,
        'total_lost': total_lost,
        'total_found': total_found,
        'total_returned': total_returned,
        'total_claims': total_claims,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'category_stats': category_stats,
    }
    return render(request, 'items/admin_dashboard.html', context)


@staff_member_required
def review_claim(request, pk):
    """Admin view to review and approve/reject a claim."""
    claim = get_object_or_404(Claim.objects.select_related('item', 'claimant'), pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')

        if action == 'approve':
            claim.status = 'approved'
            claim.admin_notes = admin_notes
            claim.save()
            # Update item status to returned
            claim.item.status = 'returned'
            claim.item.save()
            # Reject other pending claims for this item
            other_claims = Claim.objects.filter(item=claim.item, status='pending').exclude(pk=claim.pk)
            for other_claim in other_claims:
                other_claim.status = 'rejected'
                other_claim.admin_notes = 'Another claim was approved for this item.'
                other_claim.save()
                Notification.objects.create(
                    user=other_claim.claimant,
                    title='Claim Rejected',
                    message=f'Your claim on "{claim.item.name}" has been rejected. Another claim was approved.',
                    link=f'/items/{claim.item.pk}/'
                )
            # Notify claimant
            Notification.objects.create(
                user=claim.claimant,
                title='Claim Approved! 🎉',
                message=f'Your claim on "{claim.item.name}" has been approved! Please coordinate with the item reporter to recover it. Admin notes: {admin_notes}' if admin_notes else f'Your claim on "{claim.item.name}" has been approved! Please coordinate with the item reporter to recover it.',
                link=f'/items/{claim.item.pk}/'
            )
            # Notify item owner
            Notification.objects.create(
                user=claim.item.user,
                title='Claim Approved on Your Item',
                message=f'A claim by {claim.claimant.get_full_name() or claim.claimant.username} on "{claim.item.name}" has been approved. Contact: {claim.contact_info}',
                link=f'/items/{claim.item.pk}/'
            )
            messages.success(request, 'Claim approved and notifications sent!')

        elif action == 'reject':
            claim.status = 'rejected'
            claim.admin_notes = admin_notes
            claim.save()
            # Check if any pending claims remain
            remaining = Claim.objects.filter(item=claim.item, status='pending').count()
            if remaining == 0 and claim.item.status == 'claim_pending':
                claim.item.status = claim.item.item_type
                claim.item.save()
            # Notify claimant
            Notification.objects.create(
                user=claim.claimant,
                title='Claim Rejected',
                message=f'Your claim on "{claim.item.name}" has been rejected. {("Reason: " + admin_notes) if admin_notes else ""}',
                link=f'/items/{claim.item.pk}/'
            )
            messages.success(request, 'Claim rejected and claimant notified.')

        return redirect('admin_dashboard')

    context = {
        'claim': claim,
    }
    return render(request, 'items/review_claim.html', context)


@staff_member_required
def admin_update_item_status(request, pk):
    """Admin can update any item's status."""
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Item.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            old_status = item.get_status_display()
            item.status = new_status
            item.save()
            new_status_display = item.get_status_display()
            # Notify item owner
            Notification.objects.create(
                user=item.user,
                title='Item Status Updated',
                message=f'Your item "{item.name}" status has been changed from {old_status} to {new_status_display} by an admin.',
                link=f'/items/{item.pk}/'
            )
            messages.success(request, f'Item status updated to {new_status_display}.')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('item_detail', pk=item.pk)
