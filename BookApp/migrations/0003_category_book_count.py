# Generated by Django 5.1.2 on 2024-11-24 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookApp', '0002_remove_category_book_count_alter_book_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='book_count',
            field=models.IntegerField(default=0),
        ),
    ]
