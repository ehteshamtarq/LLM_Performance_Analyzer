# Generated by Django 5.1.3 on 2025-01-03 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input', models.TextField()),
                ('meta', models.TextField()),
                ('output', models.TextField()),
                ('is_published', models.BooleanField(default=False)),
            ],
        ),
    ]
