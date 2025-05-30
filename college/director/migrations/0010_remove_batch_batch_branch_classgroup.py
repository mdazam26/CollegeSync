# Generated by Django 5.1.8 on 2025-05-04 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('director', '0009_rename_teacher_phone_number_teacher_teacher_phone_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch',
            name='batch_branch',
        ),
        migrations.CreateModel(
            name='ClassGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='class_groups', to='director.batch')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='class_groups', to='director.branch')),
            ],
            options={
                'unique_together': {('batch', 'branch')},
            },
        ),
    ]
