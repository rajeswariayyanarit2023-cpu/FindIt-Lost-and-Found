from django.contrib import admin
from .models import Category, Item, Claim, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'status', 'user', 'category', 'date_lost_found', 'location', 'created_at')
    list_filter = ('item_type', 'status', 'category', 'created_at')
    search_fields = ('name', 'description', 'location', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimant', 'status', 'contact_info', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('item__name', 'claimant__username', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
