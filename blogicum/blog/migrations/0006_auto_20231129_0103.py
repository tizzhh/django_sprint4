# Generated by Django 3.2.16 on 2023-11-29 01:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_post_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'default_related_name': 'comments', 'ordering': ['-created_at']},
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='pub_date',
            new_name='created_at',
        ),
    ]
