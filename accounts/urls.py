from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Authentication and dashboard pages
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
]