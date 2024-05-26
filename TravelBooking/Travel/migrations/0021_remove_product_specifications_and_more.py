# Generated by Django 5.0.3 on 2024-05-17 22:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0020_otp_verified_alter_product_product_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='specifications',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('disabled', 'Disabled'), ('in_review', 'In Review'), ('draft', 'Draft'), ('rejected', 'Rejected'), ('published', 'Published')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(4, '★★★★☆'), (2, '★★☆☆☆'), (5, '★★★★★'), (1, '★☆☆☆☆'), (3, '★★★☆☆')], default=None),
        ),
    ]