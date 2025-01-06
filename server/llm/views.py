import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DatasetSerializer
from django.http import JsonResponse
from django.views import View
from .models import Dataset, Prompt, EvaluationResult
import json
from django.shortcuts import get_object_or_404
from .utils import parse_csv, evaluate_row,score_responses_with_openai
import asyncio
from asgiref.sync import sync_to_async



class FileUploadView(APIView):

    def post(self, request):

        file = request.FILES['csv']
        
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return Response({"error": f"Failed to read CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ['Input', 'Output', 'Meta']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        dataset = Dataset.objects.create(name=file.name, file=file)

        
        return Response({
            "dataset": DatasetSerializer(dataset).data,
        }, status=status.HTTP_201_CREATED)

class DatasetDetailView(APIView):

    def get(self, request, dataset_id, *args, **kwargs):
        try:
            dataset = Dataset.objects.get(id=dataset_id)

            dataset_file_path = dataset.file.path
            df = pd.read_csv(dataset_file_path)

            dataset_rows = df.to_dict(orient='records')

            prompts = Prompt.objects.all()
            prompts_data = [{"prompt_id": prompt.id, "prompt_template": prompt.template} for prompt in prompts]

            response = {
                "dataset_name": dataset.name,
                "dataset_rows": dataset_rows, 
                "prompts": prompts_data,
            }

            return Response(response, status=status.HTTP_200_OK)

        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, dataset_id, *args, **kwargs):
        data = request.data
        prompt_text = data.get("prompt", "").strip()

        try:
            existing_prompt = Prompt.objects.filter(template=prompt_text).first()

            if existing_prompt:
                return Response({"message": "Prompt already exists.", "prompt_id": existing_prompt.id}, status=status.HTTP_200_OK)

            new_prompt = Prompt.objects.create(template=prompt_text)
            return Response({"message": "Prompt added successfully.", "prompt_id": new_prompt.id}, status=status.HTTP_201_CREATED)

        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EvaluateDatasetView(APIView):
    def get(self, request, dataset_id, prompt_id):
        prompt = get_object_or_404(Prompt, id=prompt_id)
        dataset = get_object_or_404(Dataset, id=dataset_id)

        EvaluationResult.objects.filter(dataset=dataset, prompt=prompt).delete()

        file_path = dataset.file.path
        rows = parse_csv(file_path)

        @sync_to_async
        def create_evaluation_result(data):
            return EvaluationResult.objects.create(**data)

        async def process_rows():
            evaluation_results = []
            for row in rows:
                meta = row.get("Meta", "")
                output = row.get("Output", "")

                prompt_text = prompt.template
                prompt_text_formatted = prompt_text.format(Meta=meta) + ' Please provide a short answer.'

                responses = await evaluate_row(prompt_text_formatted, ["groq", "gemini"])
        

                groq_response = responses[0]['groq']
                gemini_response = responses[1].strip()


                groq_correctness, groq_faithfulness = await score_responses_with_openai(
                    prompt_text_formatted, groq_response, output
                )

                gemini_correctness, gemini_faithfulness = await score_responses_with_openai(
                    prompt_text_formatted, gemini_response, output
                )


                result_data = {
                    'dataset': dataset,
                    'prompt': prompt,
                    'output': output,
                    'groq_llm_response': groq_response,
                    'gemini_llm_response': gemini_response,
                    'groq_correctness_score': groq_correctness,
                    'groq_faithfulness_score': groq_faithfulness,
                    'gemini_correctness_score': gemini_correctness,
                    'gemini_faithfulness_score': gemini_faithfulness,
                    'prompt_text': prompt_text_formatted,
                }

                result = await create_evaluation_result(result_data)
                evaluation_results.append(result)

            return evaluation_results

        asyncio.run(process_rows())

        evaluations = EvaluationResult.objects.filter(prompt=prompt, dataset=dataset)
        response_data = [
            {
                "groq_response": evaluation.groq_llm_response,
                "gemini_response": evaluation.gemini_llm_response,
                "groq_correctness": evaluation.groq_correctness_score,
                "groq_faithfulness": evaluation.groq_faithfulness_score,
                "gemini_correctness": evaluation.gemini_correctness_score,
                "gemini_faithfulness": evaluation.gemini_faithfulness_score,
                "expected_answer": evaluation.output,
                "prompt": evaluation.prompt_text,
            }
            for evaluation in evaluations
        ]
        return JsonResponse(response_data, safe=False)