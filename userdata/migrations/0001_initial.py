# Generated by Django 3.1.1 on 2021-01-21 15:22

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
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('short_code', models.CharField(max_length=10)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('employee_code', models.CharField(max_length=20, unique=True)),
                ('branch', models.CharField(choices=[('branch1', 'branch1'), ('branch2', 'branch2'), ('branch3', 'branch3')], max_length=10)),
                ('department', models.CharField(choices=[('dept_1', 'control'), ('dept_2', 'kitchen'), ('dept_3', 'store')], max_length=10)),
                ('phone_number', models.CharField(max_length=13)),
                ('email_address', models.EmailField(max_length=254)),
                ('details', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
