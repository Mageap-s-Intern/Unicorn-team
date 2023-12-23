from django.contrib import admin
from django.urls import path
from .views import convert_xml

urlpatterns = [
    path('', convert_xml)
]
