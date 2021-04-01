from django.contrib import admin

# Register your models here.
from payments.models import Wallets, Transactions

admin.site.register(Transactions)
admin.site.register(Wallets)
