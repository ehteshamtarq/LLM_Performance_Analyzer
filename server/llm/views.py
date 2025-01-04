# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# from .models import Dataset, Prompt, EvaluationResult
# from .serializers import DatasetSerializer, PromptSerializer, EvaluationResultSerializer
# # import pandas as pd

# # class DatasetUploadView(APIView):
# #     def post(self, request):
# #         file = request.FILES['file']
# #         dataset = Dataset.objects.create(name=file.name, file=file)
# #         return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)

# # class PromptView(APIView):
# #     def post(self, request):
# #         serializer = PromptSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # class EvaluateView(APIView):
# #     def post(self, request):
# #         prompt = request.data.get("prompt")
# #         dataset_id = request.data.get("dataset_id")
# #         dataset = Dataset.objects.get(id=dataset_id)
# #         df = pd.read_csv(dataset.file)
# #         llm_response = "Sample Response" 
# #         result = EvaluationResult.objects.create(
# #             dataset=dataset,
# #             prompt=Prompt.objects.get(id=prompt),
# #             llm_response=llm_response,
# #             correctness_score=8.5,
# #             faithfulness_score=9.0,
# #         )
# #         return Response(EvaluationResultSerializer(result).data)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils.datastructures import MultiValueDictKeyError

# class FileUploadView(APIView):

#     def post(self, request):
#         file = request.FILES['csv']
#         dataset = Dataset.objects.create(name=file.name, file=file)
#         return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)


import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Dataset
from .serializers import DatasetSerializer
from django.http import JsonResponse
from django.views import View
from .models import Dataset, Prompt
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator



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


@method_decorator(ensure_csrf_cookie, name='post')
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