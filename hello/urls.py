from django.urls import path
from hello import views

app_name = 'teacher_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Quick action routes (TODO: implement these views)
    path('unit/new/', views.new_unit_outline, name='new_unit_outline'),
    path('unit/clone/', views.clone_unit_outline, name='clone_unit_outline'),
    
    # TODO: Add more URL patterns as needed
    # path('unit/<int:pk>/', views.unit_detail, name='unit_detail'),
    # path('unit/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    # path('markbooks/', views.markbooks, name='markbooks'),
    # path('calendar/', views.calendar_view, name='calendar'),
]
