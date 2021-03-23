from rest_framework import serializers

from payments.models import Users, Wallets, Transactions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'user_name', 'user_password', 'wallets')


class WalletSerializer(serializers.ModelSerializer):
    user_name = serializers.RelatedField(many=False, read_only=True)

    class Meta:
        model = Wallets
        fields = ('id', 'wallet_num', 'wallet_sum', 'user_id', 'user_name')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ('id', 'sum', 'source_wallet_id', 'destination_wallet_id')
