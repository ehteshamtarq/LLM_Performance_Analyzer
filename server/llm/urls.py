from django.urls import path
from .views import FileUploadView, DatasetDetailView
urlpatterns = [
    path('upload', FileUploadView.as_view(), name='upload'),
    path('dataset/<int:dataset_id>/', DatasetDetailView.as_view(), name='dataset_detail'),
]
