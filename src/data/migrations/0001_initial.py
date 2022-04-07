# Generated by Django 3.2.12 on 2022-04-01 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, max_length=8)),
                ('task_id', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=15)),
                ('continent_name', models.CharField(max_length=255)),
                ('country_name', models.CharField(max_length=255)),
                ('region_name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('latitude', models.CharField(max_length=255)),
                ('longitude', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'geodata',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='FailedWorkerResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(blank=True, max_length=255, null=True)),
                ('worker_name', models.CharField(max_length=255)),
                ('worker_error', models.TextField()),
                ('worker_result', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]