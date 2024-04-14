# Generated by Django 5.0.3 on 2024-04-12 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0019_alter_product_product_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='date',
            new_name='startDate',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('in_review', 'In Review'), ('disabled', 'Disabled'), ('published', 'Published'), ('rejected', 'Rejected'), ('draft', 'Draft')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(3, '★★★☆☆'), (5, '★★★★★'), (1, '★☆☆☆☆'), (2, '★★☆☆☆'), (4, '★★★★☆')], default=None),
        ),
    ]
