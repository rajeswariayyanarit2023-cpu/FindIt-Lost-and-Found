from django.db import migrations


DEFAULT_CATEGORIES = [
    'Mobile Phone',
    'ID Card',
    'Books',
    'Wallet',
    'Laptop',
    'Keys',
    'Bags',
    'Documents',
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
        ('items', '0002_seed_default_categories'),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, migrations.RunPython.noop),
    ]
