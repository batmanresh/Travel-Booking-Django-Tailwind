# Generated by Django 5.0.3 on 2024-05-06 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0013_remove_contactmessage_subject_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('rejected', 'Rejected'), ('disabled', 'Disabled'), ('published', 'Published'), ('in_review', 'In Review'), ('draft', 'Draft')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='rating',
            field=models.IntegerField(choices=[(3, '★★★☆☆'), (2, '★★☆☆☆'), (5, '★★★★★'), (4, '★★★★☆'), (1, '★☆☆☆☆')], default=None),
        ),
    ]