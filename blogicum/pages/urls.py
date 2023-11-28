from django.shortcuts import redirect
from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    path('', lambda request: redirect('pages:about'), name='pages_default'),
]
