# Generated by Django 5.1.6 on 2025-02-28 23:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_competition_participants'),
        ('user', '0003_alter_user_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('state', models.CharField(choices=[('not_started', 'Not Started'), ('started', 'Started'), ('finished', 'Finished')], max_length=11)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competition.competition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
