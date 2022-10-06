from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'staff', 'filial']


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'


class DeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliver
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class Product1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'measurement', 'preparer', 'min_count']

class ProductFilialSerializer(serializers.ModelSerializer):
    product = Product1Serializer(read_only=True)
    class Meta:
        model = ProductFilial
        fields = '__all__'


class RecieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recieve
        fields = '__all__'


class RecieveItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecieveItem
        fields = '__all__'


class FakturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faktura
        fields = '__all__'


class FakturaItemSerializer(serializers.ModelSerializer):
    product = Product1Serializer(read_only=True)
    class Meta:
        model = FakturaItem
        fields = '__all__'


class FakturaItemReadSerializer(serializers.ModelSerializer):
    product = Product1Serializer(read_only=True)
    class Meta:
        model = FakturaItem
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        fields = '__all__'


# class DebtHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DebtHistory
#         fields = '__all__'


class DebtSerializer(serializers.ModelSerializer):
    debtor = DebtorSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    class Meta:
        model = Debt
        fields = '__all__'


class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = '__all__'


class CartDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartDebt
        fields = '__all__'


class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = '__all__'

class ChangePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePrice
        fields = '__all__'


class ChangePriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePriceItem
        fields = '__all__'

class ReturnProductToDeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliver
        fields = '__all__'

class ReturnProductToDeliverItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliverItem
        fields = '__all__'