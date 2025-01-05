import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Dataset
from .serializers import DatasetSerializer
from django.http import JsonResponse
from django.views import View
from .models import Dataset, Prompt, EvaluationResult
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from .utils import parse_csv, evaluate_row, calculate_scores, score_responses_with_openai
import asyncio
from asgiref.sync import sync_to_async



class FileUploadView(APIView):

    def post(self, request):
        # Get the uploaded CSV file from the request
        file = request.FILES['csv']
        
        # Check if a file is provided
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Read the CSV file using pandas
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

        # Save the dataset object to the database (optional)
        dataset = Dataset.objects.create(name=file.name, file=file)

        
        # Return the table data in the response
        return Response({
            "dataset": DatasetSerializer(dataset).data,
        }, status=status.HTTP_201_CREATED)


class DatasetDetailView(View):

    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id)

            # Access the dataset file
            dataset_file_path = dataset.file.path

            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(dataset_file_path)

            # Convert DataFrame to JSON format (each row as a dictionary)
            dataset_rows = df.to_dict(orient='records')  # Convert each row to a dictionary

            # Fetch prompts for the dataset
            prompts = Prompt.objects.all()

            # Prepare response data
            prompts_data = [{"prompt_id": prompt.id, "prompt_template": prompt.template} for prompt in prompts]

            response = {
                "dataset_name": dataset.name,
                "dataset_rows": dataset_rows,  # List of rows in dataset
                "prompts": prompts_data,
            }

            return JsonResponse(response, status=200)

        except Dataset.DoesNotExist:
            return JsonResponse({"error": "Dataset not found."}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    def post(self, request, dataset_id):
        data = json.loads(request.body)
        prompt_text = data.get("prompt").strip()

        try:
            dataset = Dataset.objects.get(id=dataset_id)

            # Check if the prompt already exists (using 'template' field)
            existing_prompt = Prompt.objects.filter(template=prompt_text).first()

            if existing_prompt:
                # If it exists, return the ID of the existing prompt
                return JsonResponse({"message": "Prompt already exists.", "prompt_id": existing_prompt.id}, status=200)

            # If the prompt doesn't exist, create a new one
            new_prompt = Prompt.objects.create(template=prompt_text)
            return JsonResponse({"message": "Prompt added successfully.", "prompt_id": new_prompt.id}, status=201)

        except Dataset.DoesNotExist:
            return JsonResponse({"error": "Dataset not found."}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)


class EvaluateDatasetView(APIView):
    def get(self, request, dataset_id, prompt_id):
        prompt = get_object_or_404(Prompt, id=prompt_id)
        dataset = get_object_or_404(Dataset, id=dataset_id)

        EvaluationResult.objects.filter(dataset=dataset, prompt=prompt).delete()

        # Parse the CSV file
        file_path = dataset.file.path
        rows = parse_csv(file_path)

        # Wrap database calls with sync_to_async
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


                # groq_correctness, groq_faithfulness = await score_responses_with_openai(
                #     prompt_text, groq_response, output
                # )

                # gemini_correctness, gemini_faithfulness = await score_responses_with_openai(
                #     prompt_text, gemini_response, output
                # )


                # Prepare the result data
                result_data = {
                    'dataset': dataset,
                    'prompt': prompt,
                    'output': output,
                    'groq_llm_response': groq_response,
                    'gemini_llm_response': gemini_response,
                    # 'groq_correctness_score': groq_correctness,
                    # 'groq_faithfulness_score': groq_faithfulness,
                    # 'gemini_correctness_score': gemini_correctness,
                    # 'gemini_faithfulness_score': gemini_faithfulness,
                    'prompt_text': prompt_text_formatted,
                }

                # Create evaluation result asynchronously
                result = await create_evaluation_result(result_data)
                evaluation_results.append(result)

            return evaluation_results

        # Run the asynchronous processing
        asyncio.run(process_rows())

        # Return all evaluation results for the given prompt and dataset
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