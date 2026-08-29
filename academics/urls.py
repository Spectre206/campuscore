from django.urls import path
from . import views
from .api_views import DepartmentListCreateAPIView

urlpatterns = [
    path('departments/', views.department_list, name='department-list'),
    path('api/departments/', DepartmentListCreateAPIView.as_view(), name='api-department-list'),
]