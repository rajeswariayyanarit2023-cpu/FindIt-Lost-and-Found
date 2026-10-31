from django import forms
from .models import Category, Item, Claim


class ItemForm(forms.ModelForm):
    """Form for creating and editing lost/found item reports."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by('name'),
        required=False,
        empty_label='Select Category',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    date_lost_found = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
        ),
        label='Date Lost/Found'
    )

    class Meta:
        model = Item
        fields = ['name', 'item_type', 'category', 'description', 'date_lost_found', 'location', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Blue Backpack, iPhone 14, Keys...'
            }),
            'item_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide a detailed description including color, brand, distinguishing features...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Library 2nd Floor, Main Gate, Cafeteria...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
        labels = {
            'item_type': 'Report Type',
            'name': 'Item Name',
            'description': 'Description',
            'category': 'Category',
            'location': 'Location',
            'image': 'Photo (optional)',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError('Item name must be at least 3 characters long.')
        return name

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 10:
            raise forms.ValidationError('Please provide a more detailed description (at least 10 characters).')
        return desc


class ItemEditForm(forms.ModelForm):
    """Form for editing item reports (allows status change for owners)."""

    date_lost_found = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
        ),
        label='Date Lost/Found'
    )

    class Meta:
        model = Item
        fields = ['name', 'category', 'description', 'date_lost_found', 'location', 'image', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ClaimForm(forms.ModelForm):
    """Form for submitting a claim on an item."""

    class Meta:
        model = Claim
        fields = ['description', 'proof_image', 'contact_info']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain how you can verify ownership or how you found this item...'
            }),
            'proof_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number or email address'
            }),
        }
        labels = {
            'description': 'Claim Description',
            'proof_image': 'Proof Image (optional)',
            'contact_info': 'Contact Information',
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 20:
            raise forms.ValidationError('Please provide a detailed explanation (at least 20 characters).')
        return desc

    def clean_contact_info(self):
        info = self.cleaned_data.get('contact_info', '').strip()
        if len(info) < 5:
            raise forms.ValidationError('Please provide valid contact information.')
        return info


class ItemSearchForm(forms.Form):
    """Form for searching and filtering items."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search items...',
        })
    )
    item_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types'), ('lost', 'Lost'), ('found', 'Found')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by('name'),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses'), ('lost', 'Lost'), ('found', 'Found'),
                 ('claim_pending', 'Claim Pending'), ('returned', 'Returned')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
