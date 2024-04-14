# Generated by Django 5.0.3 on 2024-04-11 09:25

import Travel.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0016_alter_product_product_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='product.jpg', upload_to=Travel.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default='5.00', max_digits=8),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default='1.00', max_digits=8),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('rejected', 'Rejected'), ('published', 'Published'), ('disabled', 'Disabled'), ('draft', 'Draft'), ('in_review', 'In Review')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(2, '★★☆☆☆'), (4, '★★★★☆'), (1, '★☆☆☆☆'), (3, '★★★☆☆'), (5, '★★★★★')], default=None),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='image',
            field=models.ImageField(blank=True, default=None, upload_to=Travel.models.user_directory_path),
        ),
    ]
