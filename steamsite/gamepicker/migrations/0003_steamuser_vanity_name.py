# Generated by Django 2.1.5 on 2019-02-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamepicker', '0002_switch_to_utf8mb4_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamuser',
            name='vanity_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]