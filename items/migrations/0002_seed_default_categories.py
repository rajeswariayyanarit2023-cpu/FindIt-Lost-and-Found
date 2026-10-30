from django.db import migrations


DEFAULT_CATEGORIES = [
    'Electronics',
    'Documents',
    'Bags',
    'Accessories',
    'Books',
    'Clothing',
    'Others',
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model('items', 'Category')
    database = schema_editor.connection.alias

    for name in DEFAULT_CATEGORIES:
        Category.objects.using(database).get_or_create(
            name=name,
            defaults={'icon': 'bi-tag'},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, migrations.RunPython.noop),
    ]