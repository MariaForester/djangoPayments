from django.urls import path
from .views import LoginAPIView, RegistrationAPIView
from rest_framework_jwt.views import obtain_jwt_token

app_name = 'authentication'
urlpatterns = [
    path('reg/', RegistrationAPIView.as_view()),
    path('login/', obtain_jwt_token),
]
