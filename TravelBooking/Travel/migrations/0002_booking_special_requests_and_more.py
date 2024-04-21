# Generated by Django 5.0.3 on 2024-04-20 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='special_requests',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('published', 'Published'), ('disabled', 'Disabled'), ('draft', 'Draft'), ('rejected', 'Rejected'), ('in_review', 'In Review')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(5, '★★★★★'), (1, '★☆☆☆☆'), (2, '★★☆☆☆'), (4, '★★★★☆'), (3, '★★★☆☆')], default=None),
        ),
    ]
