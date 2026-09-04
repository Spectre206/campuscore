from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken import views as auth_token_views
from rest_framework.routers import DefaultRouter

from accounts import views as accounts_views
from accounts.api_views import UserViewSet

from .views import health_check

router = DefaultRouter()
router.register(r'api/v1/users', UserViewSet, basename='user')

urlpatterns = [
    path('', accounts_views.landing, name='landing'),
    path('admin/', admin.site.urls),
    path('', include('academics.urls')),
    path('accounts/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('ai/', include('ai_service.urls')),
    path('health/', health_check, name='health-check'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/auth/token/', auth_token_views.obtain_auth_token, name='api-token-auth'),
]

urlpatterns += router.urls
