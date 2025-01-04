# Generated by Django 5.1.3 on 2025-01-04 11:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='datasets/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groq_llm_response', models.TextField()),
                ('gemini_llm_response', models.TextField()),
                ('groq_correctness_score', models.FloatField()),
                ('groq_faithfulness_score', models.FloatField()),
                ('gemini_correctness_score', models.FloatField()),
                ('gemini_faithfulness_score', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='llm.dataset')),
            ],
        ),
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('template', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Evaluation',
        ),
        migrations.AddField(
            model_name='evaluationresult',
            name='prompt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='llm.prompt'),
        ),
    ]