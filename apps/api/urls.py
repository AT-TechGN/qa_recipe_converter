from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('upload/', views.UploadAPIView.as_view(), name='upload'),
    path('jobs/', views.JobListAPIView.as_view(), name='jobs'),
    path('jobs/<uuid:job_id>/', views.JobDetailAPIView.as_view(), name='job-detail'),
    path('jobs/<uuid:job_id>/generate/', views.GenerateExcelAPIView.as_view(), name='generate'),
    path('jobs/<uuid:job_id>/use-cases/<uuid:uc_id>/', views.UseCaseUpdateAPIView.as_view(), name='uc-update'),
    path('files/search/', views.FileSearchAPIView.as_view(), name='file-search'),
]
