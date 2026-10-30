from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Categories for lost and found items."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-tag')  # Bootstrap icon class

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    """Model representing a lost or found item report."""

    TYPE_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
    ]

    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('claim_pending', 'Claim Pending'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date_lost_found = models.DateField(help_text='Date the item was lost or found')
    location = models.CharField(max_length=300)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_item_type_display()}: {self.name}"

    def save(self, *args, **kwargs):
        # Auto-set initial status based on type
        if not self.pk:
            self.status = self.item_type
        super().save(*args, **kwargs)


class Claim(models.Model):
    """Model representing a claim on a lost or found item."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    description = models.TextField(help_text='Describe why you believe this item is yours or how you found it')
    proof_image = models.ImageField(upload_to='claim_proofs/', blank=True, null=True)
    contact_info = models.CharField(max_length=200, help_text='Phone number or email for contact')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Prevent duplicate claims
        unique_together = ['item', 'claimant']

    def __str__(self):
        return f"Claim by {self.claimant.username} on {self.item.name}"


class Notification(models.Model):
    """Notification model for claim status updates and other alerts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
