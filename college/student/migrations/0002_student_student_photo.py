# Generated by Django 5.1.8 on 2025-05-06 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='student_photo',
            field=models.ImageField(blank=True, null=True, upload_to='student_photos/'),
        ),
    ]
