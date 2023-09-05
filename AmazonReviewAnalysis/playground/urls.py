from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('getURL/', views.getURL),
    path('getURL/showResults/', views.showResults)
]
