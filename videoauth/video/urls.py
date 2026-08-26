from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('upload/', views.video_upload, name='video_upload'),
    path('<int:pk>/', views.video_detail, name='video_detail'),
    path('<int:pk>/delete/', views.video_delete, name='video_delete'),
    path('<int:pk>/export/', views.export_report, name='export_report'),
    path('register/', views.register, name='register'),
]