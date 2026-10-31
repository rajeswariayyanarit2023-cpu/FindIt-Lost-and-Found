from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import ItemForm
from .models import Category, Item


class CategoryFormTests(TestCase):
    DEFAULT_CATEGORIES = {
        'Mobile Phone',
        'ID Card',
        'Books',
        'Wallet',
        'Laptop',
        'Keys',
        'Bags',
        'Documents',
        'Others',
    }

    def test_default_categories_are_available_in_item_form(self):
        form = ItemForm()
        category_names = list(
            form.fields['category'].queryset.values_list('name', flat=True)
        )

        self.assertTrue(self.DEFAULT_CATEGORIES.issubset(category_names))
        self.assertEqual(form.fields['category'].empty_label, 'Select Category')

    def test_lost_and_found_report_forms_render_categories(self):
        user = User.objects.create_user(username='reporter', password='test-password')
        self.client.force_login(user)

        for item_type in ('lost', 'found'):
            with self.subTest(item_type=item_type):
                response = self.client.get(
                    reverse('report_item'),
                    {'type': item_type},
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    '<option value="" selected>Select Category</option>',
                    html=True,
                )
                for category_name in self.DEFAULT_CATEGORIES:
                    self.assertContains(response, category_name)

    def test_category_filter_returns_items_in_selected_category(self):
        user = User.objects.create_user(username='finder', password='test-password')
        category = Category.objects.get(name='Mobile Phone')
        matching_item = Item.objects.create(
            user=user,
            item_type='lost',
            name='Missing phone',
            description='A phone with a blue case.',
            category=category,
            date_lost_found='2026-10-30',
            location='Library',
        )
        Item.objects.create(
            user=user,
            item_type='found',
            name='Found wallet',
            description='A brown leather wallet.',
            category=Category.objects.get(name='Wallet'),
            date_lost_found='2026-10-30',
            location='Cafeteria',
        )

        response = self.client.get(
            reverse('item_list'),
            {'category': str(category.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_results'], 1)
        self.assertContains(response, matching_item.name)
        self.assertContains(
            response,
            f'<option value="{category.pk}" selected>{category.name}</option>',
            html=True,
        )
