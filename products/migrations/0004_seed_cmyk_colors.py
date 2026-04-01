# Generated manually to seed CMYK

from django.db import migrations

def seed_cmyk(apps, schema_editor):
    Color = apps.get_model('products', 'Color')
    colors = ['Cyan', 'Magenta', 'Amarillo', 'Negro']
    for c in colors:
        Color.objects.get_or_create(name=c, defaults={'is_standard': True})

def reverse_cmyk(apps, schema_editor):
    Color = apps.get_model('products', 'Color')
    Color.objects.filter(name__in=['Cyan', 'Magenta', 'Amarillo', 'Negro']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_add_notes_front_back'),
    ]

    operations = [
        migrations.RunPython(seed_cmyk, reverse_cmyk),
    ]
