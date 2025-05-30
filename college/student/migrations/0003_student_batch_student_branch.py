# Generated by Django 5.1.8 on 2025-05-07 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('director', '0010_remove_batch_batch_branch_classgroup'),
        ('student', '0002_student_student_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='director.batch'),
        ),
        migrations.AddField(
            model_name='student',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='director.branch'),
        ),
    ]
