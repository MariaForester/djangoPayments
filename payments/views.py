from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
import logging
import random

from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework.response import Response
import string

from .models import Users, Wallets, Transactions
from .serializers import UserSerializer, WalletSerializer, TransactionSerializer
from .forms import UserRegistrationForm
from .forms import LoginForm

DEFAULT_SUM = 100


'''def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False) #не сохраняем автоматически данные формы
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return HttpResponseRedirect('http://127.0.0.1:9091/')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('http://127.0.0.1:9091/')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})'''


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = Users.objects.all()


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    queryset = Wallets.objects.all()


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transactions.objects.all()


class UserView(views.APIView):
    def get(self, request):
        users = Users.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)

    # def post(self, request):
    #     request_data = request.data
    #     user_serializer = UserSerializer(data=request_data)
    #     if user_serializer.is_valid(raise_exception=True):
    #         user_saved = user_serializer.save()
    #     return HttpResponse("User {} ({}) has been added".format(user_saved.user_name,
    #                                                              user_saved.user_password))


class UserPersonalUseView(views.APIView):
    def get(self, request):
        wallets = Wallets.objects.filter(user_id__user_name=request.data['user_name']).values('wallet_num',
                                                                                              'wallet_sum')
        if not wallets:
            return HttpResponseBadRequest("Check your user name")
        else:
            wallet_serializer = WalletSerializer(data=wallets, many=True)
            return Response(wallet_serializer.initial_data)


class WalletView(views.APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        '''if not request.user.is_authenticated:
            return HttpResponseBadRequest("Permission is restricted to logged-in users")'''
        wallets = Wallets.objects.select_related().values('wallet_num', 'user_id__user_name')
        wallets_serializer = WalletSerializer(data=wallets, many=True)
        return Response(wallets_serializer.initial_data)

    def post(self, request):
        user_name = request.data['user_name']
        try:
            user_id = Users.objects.get(user_name=user_name).id
        except ObjectDoesNotExist as e:
            logging.error(e)
            return HttpResponseBadRequest("Check your user name")
        wallet_num = ''.join(random.choices(string.digits, k=16))
        wallet_serializer = WalletSerializer(data={
            'wallet_num': wallet_num,
            'wallet_sum': DEFAULT_SUM,
            'user_id': user_id
        })
        if wallet_serializer.is_valid(raise_exception=True):
            wallet_saved = wallet_serializer.save()
        return HttpResponse("Wallet with No.[{}] has been added for user {}. Sum on the account: {}".
                            format(wallet_saved.wallet_num, user_name, wallet_saved.wallet_sum))


class TransactionView(views.APIView):
    def put(self, request):
        """ we get a number of source and destination wallet
        by a numbers get ids of wallets
        subtract from source wallet sum
        add to destination wallet sum
        save transaction object
        get money left by source wallet id
        return Success  + money left
        """
        request_data = request.data
        source_wallet_num = request_data['source_wallet_num']
        destination_wallet_num = request_data['destination_wallet_num']
        sum_to_transfer = request_data['sum']

        if sum_to_transfer <= 0:
            return HttpResponseBadRequest("Enter correct sum")

        source = Wallets.objects.get(wallet_num=source_wallet_num)
        destination = Wallets.objects.get(wallet_num=destination_wallet_num)

        source.wallet_sum = source.wallet_sum - sum_to_transfer
        destination.wallet_sum = destination.wallet_sum + sum_to_transfer

        try:
            source.full_clean()
        except ValidationError as e:
            logging.error(e)
            return HttpResponseBadRequest("Check your balance")

        source.save()
        destination.save()

        transaction_serializer = TransactionSerializer(data={
            'sum': sum_to_transfer,
            'source_wallet_id': source.id,
            'destination_wallet_id': destination.id
        })

        if transaction_serializer.is_valid(raise_exception=True):
            transaction_serializer.save()

        return HttpResponse("Transferred {} to {}. Your balance: {}".format(sum_to_transfer,
                                                                            destination_wallet_num,
                                                                            source.wallet_sum))

