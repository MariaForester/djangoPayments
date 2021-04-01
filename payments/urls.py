from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserPersonalUseView, WalletViewSet, WalletView, TransactionViewSet, \
    TransactionView

app_name = 'payments'

router = DefaultRouter()

router.register(f'walletsViewSet', WalletViewSet)
router.register(f'transactionViewSet', TransactionViewSet)

urlpatterns = router.urls + [
    path('account/', UserPersonalUseView.as_view()),
    path('wallets/', WalletView.as_view()),
    path('transactions/', TransactionView.as_view()),
]
