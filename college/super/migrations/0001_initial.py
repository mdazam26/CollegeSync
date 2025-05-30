# Generated by Django 5.1.8 on 2025-05-01 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('domain', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('institute_name', models.CharField(max_length=100)),
                ('institute_address', models.TextField(blank=True, null=True)),
                ('institute_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('institute_number', models.CharField(blank=True, max_length=15, null=True)),
                ('admin_name', models.CharField(max_length=50)),
                ('admin_number', models.CharField(blank=True, max_length=15, null=True)),
                ('admin_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('admin_username', models.CharField(max_length=11, unique=True)),
                ('admin_password', models.CharField(max_length=150)),
            ],
        ),
    ]
