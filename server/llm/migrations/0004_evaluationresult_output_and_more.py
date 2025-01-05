# Generated by Django 5.1.3 on 2025-01-05 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llm', '0003_remove_prompt_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationresult',
            name='output',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='gemini_correctness_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='gemini_faithfulness_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='gemini_llm_response',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='groq_correctness_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='groq_faithfulness_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evaluationresult',
            name='groq_llm_response',
            field=models.TextField(blank=True, null=True),
        ),
    ]
