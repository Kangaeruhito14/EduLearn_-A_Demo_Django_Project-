# Generated by Django 5.1.5 on 2025-04-08 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_course_thumbnail_course_thumbnail_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='thumbnail_url',
        ),
        migrations.AddField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='course_thumbnail/'),
        ),
    ]
