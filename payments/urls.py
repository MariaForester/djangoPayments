from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserViewSet, UserView, UserPersonalUseView, WalletViewSet, WalletView, TransactionViewSet, \
    TransactionView

app_name = 'payments'

router = DefaultRouter()

router.register(r'usersViewSet', UserViewSet)
router.register(f'walletsViewSet', WalletViewSet)
router.register(f'transactionViewSet', TransactionViewSet)

urlpatterns = router.urls + [
    path('users/', UserView.as_view()),
    path('account/', UserPersonalUseView.as_view()),
    path('wallets/', WalletView.as_view()),
    path('transactions/', TransactionView.as_view()),
]
