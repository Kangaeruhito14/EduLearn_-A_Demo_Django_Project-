# Generated by Django 5.1.5 on 2025-03-12 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_thumbnail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='emalil',
            new_name='email',
        ),
    ]
