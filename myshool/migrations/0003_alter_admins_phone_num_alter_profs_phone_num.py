# Generated by Django 5.1.1 on 2024-09-18 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshool', '0002_profs_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admins',
            name='phone_num',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='profs',
            name='phone_num',
            field=models.CharField(max_length=15),
        ),
    ]
