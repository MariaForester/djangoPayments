from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from rest_framework.permissions import IsAuthenticated
import logging
import random
import string

from rest_framework import viewsets, views

from .models import Wallets, Transactions
from .serializers import WalletSerializer, TransactionSerializer

DEFAULT_SUM = 100


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    queryset = Wallets.objects.all()


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transactions.objects.all()


class UserPersonalUseView(views.APIView):
    """
    0 - all good, return list of wallets belonging to the user;
    1 - wrong user name.
    """

    def get(self, request):
        wallets = Wallets.objects.filter(user_id_id=request.user.id).values('wallet_num', 'wallet_sum')
        if not wallets:
            return JsonResponse({
                'code': 1,
                'message': 'Check your user name.'
            })
        else:
            wallet_serializer = WalletSerializer(data=wallets, many=True)
            return JsonResponse({
                'code': 0,
                'message': list(wallet_serializer.initial_data)
            })


class WalletView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        0 - all good, return list of all wallets in system;
        1 - no wallets in system yet.
        """
        wallets = Wallets.objects.select_related().values('wallet_num', 'user_id__username')
        wallets_serializer = WalletSerializer(data=wallets, many=True)
        wallets_retrieved = list(wallets_serializer.initial_data)
        if wallets_retrieved:
            return JsonResponse({
                'code': 0,
                'message': wallets_retrieved
            })
        else:
            return JsonResponse({
                'code': 1,
                'message': 'Not a single user has create a wallet yet.'
            })

    def post(self, request):
        """
        0 - all good, a wallet has been added for the user.
        """
        current_user = request.user
        current_user_id = current_user.id
        current_user_name = current_user.username

        wallet_num = ''.join(random.choices(string.digits, k=16))
        wallet_serializer = WalletSerializer(data={
            'wallet_num': wallet_num,
            'wallet_sum': DEFAULT_SUM,
            'user_id': current_user_id
        })
        if wallet_serializer.is_valid(raise_exception=True):
            wallet_saved = wallet_serializer.save()
            return JsonResponse({
                'code': 0,
                'message': "Wallet with No.[{}] has been added for user {}. Sum on the account: {}".
                    format(wallet_saved.wallet_num, current_user_name, wallet_saved.wallet_sum),
                'user_name': current_user_name,
                'wallet_num': wallet_num,
                'wallet_sum': DEFAULT_SUM
            })
        return HttpResponseServerError()


class TransactionView(views.APIView):
    def put(self, request):
        """ we get a number of source and destination wallet
        by a numbers get ids of wallets
        subtract from source wallet sum
        add to destination wallet sum
        save transaction object
        get money left by source wallet id
        return Success  + money left

        0 - all gut, return transaction info;
        1 - sum is non positive number;
        2 - wrong wallet num
        3 - sum is bigger than balance;
        """
        current_user = request.user

        request_data = request.data
        source_wallet_num = request_data['source_wallet_num']
        destination_wallet_num = request_data['destination_wallet_num']
        sum_to_transfer = request_data['sum']

        """
        Sum to transfer must be positive integer ()
        """
        if sum_to_transfer <= 0:
            return JsonResponse({
                'code': 1,
                'message': 'Enter correct sum'
            })

        source = Wallets.objects.get(wallet_num=source_wallet_num)
        destination = Wallets.objects.get(wallet_num=destination_wallet_num)

        """
        check if valid wallet number (belongs to logged in user)
        """
        user_id_of_wallet = source.user_id_id
        if current_user.id != user_id_of_wallet:
            return JsonResponse({
                'code': 2,
                'message': 'Source wallet does not belong to you.'
            })

        """
        Perform transaction
        """
        source.wallet_sum = source.wallet_sum - sum_to_transfer
        destination.wallet_sum = destination.wallet_sum + sum_to_transfer

        """
        Check if we did not transfer more money than we could
        """
        try:
            source.full_clean()
        except ValidationError as e:
            logging.error(e)
            return JsonResponse({
                'code': 3,
                'message': 'Check your balance.'
            })

        """
        Saving transaction
        """
        source.save()
        destination.save()

        transaction_serializer = TransactionSerializer(data={
            'sum': sum_to_transfer,
            'source_wallet_id': source.id,
            'destination_wallet_id': destination.id
        })

        if transaction_serializer.is_valid(raise_exception=True):
            transaction_serializer.save()

        return JsonResponse({
            'code': 0,
            'message': "Transferred {} to {}. Your balance: {}".format(sum_to_transfer,
                                                                       destination_wallet_num,
                                                                       source.wallet_sum),
            'sum_transferred': sum_to_transfer,
            'dest_wallet_num': destination_wallet_num,
            'src_wallet_num': source.wallet_num
        })
