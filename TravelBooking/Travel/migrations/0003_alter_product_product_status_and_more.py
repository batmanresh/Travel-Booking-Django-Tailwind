# Generated by Django 5.0.3 on 2024-04-21 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0002_booking_special_requests_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('disabled', 'Disabled'), ('in_review', 'In Review'), ('published', 'Published'), ('draft', 'Draft'), ('rejected', 'Rejected')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(2, '★★☆☆☆'), (1, '★☆☆☆☆'), (5, '★★★★★'), (3, '★★★☆☆'), (4, '★★★★☆')], default=None),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='image',
            field=models.ImageField(default='vendor.jpg', upload_to='vendor-images'),
        ),
    ]
