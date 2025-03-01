# Generated by Django 5.1.6 on 2025-03-01 22:16

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0002_alter_user_email_alter_user_password_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='название')),
                ('members', models.ManyToManyField(related_name='team_members', to='user.user', verbose_name='участники')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='владелец')),
            ],
            options={
                'verbose_name': 'команда',
                'verbose_name_plural': 'команды',
            },
        ),
    ]
