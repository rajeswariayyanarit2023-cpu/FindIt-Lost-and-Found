from django.test import TestCase
from .forms import ItemForm


class CategoryFormTests(TestCase):
    def test_default_categories_are_available_in_item_form(self):
        form = ItemForm()
        category_names = list(
            form.fields['category'].queryset.values_list('name', flat=True)
        )

        self.assertEqual(category_names, [
            'Accessories',
            'Bags',
            'Books',
            'Clothing',
            'Documents',
            'Electronics',
            'Others',
        ])
