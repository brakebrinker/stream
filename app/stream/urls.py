from django.urls import path, include

from .views import *

app_name = 'stream'

urlpatterns = [
    path('', index, name='stream')
]