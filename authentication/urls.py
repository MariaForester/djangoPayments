from django.urls import path
from .views import RegistrationAPIView

from rest_framework_simplejwt import views as jwt_views

app_name = 'authentication'
urlpatterns = [
    path('reg/', RegistrationAPIView.as_view()),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
