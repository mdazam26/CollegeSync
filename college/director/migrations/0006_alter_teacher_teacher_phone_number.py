# Generated by Django 5.1.8 on 2025-05-03 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('director', '0005_teacher_alter_branch_hod_delete_hod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='teacher_phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
