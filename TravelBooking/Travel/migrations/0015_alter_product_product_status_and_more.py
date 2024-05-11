# Generated by Django 5.0.3 on 2024-05-06 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0014_product_sku_alter_product_product_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('published', 'Published'), ('rejected', 'Rejected'), ('draft', 'Draft'), ('disabled', 'Disabled'), ('in_review', 'In Review')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(4, '★★★★☆'), (1, '★☆☆☆☆'), (5, '★★★★★'), (3, '★★★☆☆'), (2, '★★☆☆☆')], default=None),
        ),
    ]