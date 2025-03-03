# Generated by Django 5.1.6 on 2025-03-03 07:20

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('achievement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='почта')),
                ('username', models.SlugField(unique=True, verbose_name='юзернейм')),
                ('password', models.TextField(verbose_name='пароль')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('student', 'Student'), ('metodist', 'Metodist')], default='student', max_length=10)),
                ('achievements', models.ManyToManyField(blank=True, to='achievement.achievement', verbose_name='ачивки пользователя')),
            ],
            options={
                'verbose_name': 'пользователь',
                'verbose_name_plural': 'пользователи',
            },
        ),
    ]
