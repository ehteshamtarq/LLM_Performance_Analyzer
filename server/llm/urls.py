from django.urls import path
from .views import FileUploadView, DatasetDetailView, EvaluateDatasetView
urlpatterns = [
    path('upload', FileUploadView.as_view(), name='upload'),
    path('dataset/<int:dataset_id>/', DatasetDetailView.as_view(), name='dataset_detail'),
    path('result/<int:dataset_id>/<int:prompt_id>', EvaluateDatasetView.as_view(), name='result_details'),

]
