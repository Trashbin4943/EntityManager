from django.urls import path
from . import views

urlpatterns = [
    path('',               views.main_view,      name='main'),
    path('seed/',          views.seed_view,       name='seed'),
    path('qs/<str:qs_key>/', views.qs_result_view, name='qs_result'),
]
