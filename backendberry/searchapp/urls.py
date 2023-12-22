from django.urls import path
from .views import search_api

urlpatterns = [
    path('api/search', search_api, name='search-api'),
    # other urlpatterns...
]