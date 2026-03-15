from django.urls import path
from . import views

app_name = 'teacher_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('unit-outline/', views.unit_outline, name='unit_outline'),
    path('markbook/', views.markbook, name='markbook'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('unit/new/', views.new_unit_outline, name='new_unit_outline'),
    path('unit/clone/', views.clone_unit_action, name='clone_unit_action'),
    path('markbook/update-grade/', views.update_grade, name='update_grade'),
]
