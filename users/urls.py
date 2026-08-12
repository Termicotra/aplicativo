from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView

from .views import ChangePasswordAPIView, LoginView, RegisterAPIView, UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = router.urls

urlpatterns += [
	path('auth/login/', LoginView.as_view(), name='api_login'),
	path('auth/login/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
	path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
	path('auth/change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
]
