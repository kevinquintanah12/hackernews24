# Generated by Django 4.2.13 on 2024-11-20 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
