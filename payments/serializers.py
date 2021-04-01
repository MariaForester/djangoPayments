from rest_framework import serializers

from payments.models import Wallets, Transactions


class WalletSerializer(serializers.ModelSerializer):
    username = serializers.RelatedField(many=False, read_only=True)

    class Meta:
        model = Wallets
        fields = ('id', 'wallet_num', 'wallet_sum', 'user_id', 'username')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ('id', 'sum', 'source_wallet_id', 'destination_wallet_id')
