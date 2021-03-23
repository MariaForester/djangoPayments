from django.urls import path
from .views import LoginAPIView, RegistrationAPIView

app_name = 'authentication'
urlpatterns = [
    path('reg/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
]
