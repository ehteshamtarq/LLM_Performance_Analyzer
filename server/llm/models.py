from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Prompt(models.Model):
    template = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class EvaluationResult(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    groq_llm_response = models.TextField()
    gemini_llm_response = models.TextField()
    groq_correctness_score = models.FloatField()
    groq_faithfulness_score = models.FloatField()
    gemini_correctness_score = models.FloatField()
    gemini_faithfulness_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)