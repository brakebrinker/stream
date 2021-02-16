from django.urls import path, include

from .views import *

app_name = 'stream'

urlpatterns = [
    path('', index, name='stream'),
    path('run/', run, name='run'),
    path('stop/', stop, name='stop'),
]