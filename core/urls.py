# Core URLs

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('prescription/<int:record_id>/', views.prescription, name='prescription'),
    path('history/', views.history, name='history'),
    path('download-pdf/<int:record_id>/', views.download_pdf, name='download_pdf'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('health-advice/', views.health_advice, name='health_advice'),
]
