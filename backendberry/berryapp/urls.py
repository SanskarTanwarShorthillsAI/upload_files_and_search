# fileupload/urls.py
from django.urls import path
from .views import upload_file

urlpatterns = [
    path('api/uploadfile', upload_file, name='upload_file'),
]
