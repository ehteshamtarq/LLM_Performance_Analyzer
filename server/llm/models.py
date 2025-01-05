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
    output = models.TextField(null=True, blank=True)
    groq_llm_response = models.TextField(null=True, blank=True)  
    gemini_llm_response = models.TextField(null=True, blank=True)
    groq_correctness_score = models.FloatField(null=True, blank=True)
    groq_faithfulness_score = models.FloatField(null=True, blank=True)
    gemini_correctness_score = models.FloatField(null=True, blank=True)
    gemini_faithfulness_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    prompt_text = models.TextField(null=True, blank=True)
