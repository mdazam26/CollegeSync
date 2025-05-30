# Generated by Django 5.1.8 on 2025-04-30 19:33

import django.db.models.deletion
import django_tenants.postgresql_backend.base
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(db_index=True, max_length=63, unique=True, validators=[django_tenants.postgresql_backend.base._check_schema_name])),
                ('name', models.CharField(max_length=100)),
                ('created_on', models.DateField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TenantDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_primary', models.BooleanField(db_index=True, default=True)),
                ('domain', models.CharField(max_length=253)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
