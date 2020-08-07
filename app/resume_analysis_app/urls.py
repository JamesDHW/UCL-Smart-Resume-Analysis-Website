from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('job/', views.job_view, name='job_view'),
    path('dashboard/', views.applicant_dash, name='dash'),
    path('add_job/', views.add_job, name='add_job'),
    path('search/', views.search_results, name='search'),
]