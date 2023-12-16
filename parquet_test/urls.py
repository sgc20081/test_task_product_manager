from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path('get', views.parquet_get_test, name='parquet-get'),
]