# Generated by Django 5.0.3 on 2024-04-10 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0014_remove_product_tags_product_vendor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='product.jpg', upload_to='product_thumbnail'),
        ),
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.IntegerField(default='Rs.10000'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(default='Rs.5000'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('disabled', 'Disabled'), ('published', 'Published'), ('rejected', 'Rejected'), ('draft', 'Draft'), ('in_review', 'In Review')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(1, '★☆☆☆☆'), (4, '★★★★☆'), (5, '★★★★★'), (2, '★★☆☆☆'), (3, '★★★☆☆')], default=None),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='image',
            field=models.ImageField(blank=True, default=None, upload_to='vendor_profile'),
        ),
    ]
