# Generated by Django 5.2 on 2025-04-07 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='evaluation',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='оценка'),
        ),
    ]
