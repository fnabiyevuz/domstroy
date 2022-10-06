from django.db import models
from django.contrib.auth.models import User


class Filial(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '2) Filial'


class UserProfile(models.Model):
    staffs = [
        (1, 'director'),
        (2, 'manager'),
        (3, 'saler'),
        (4, 'warehouse')
    ]
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    staff = models.IntegerField(choices=staffs, default=3)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = '1) User'


class Groups(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.1) Group'

class Deliver(models.Model):
    name = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.1) Deliver'

class DebtDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Deliver Qarzi'


class DeliverPayHistory(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    som = models.FloatField()
    dollar = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Deliver Tolov Tarixi'


class Product(models.Model):
    measure = [
        ('dona', 'dona'),
        ('kg', 'kg'),
        ('litr', 'litr'),
        ('metr', 'metr')
    ]
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    preparer = models.CharField(max_length=255, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    kurs = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    min_count = models.FloatField(default=0)
    measurement = models.CharField(choices=measure, default='dona', max_length=4)
    barcode = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.2) Product'


class ProductFilial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '3.1) Product Filial'


class Recieve(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    status = models.IntegerField(default=0)
    # difference = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '4) Recieve'


class RecieveItem(models.Model):
    recieve = models.ForeignKey(Recieve, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    kurs = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '4.1) RecieveItem'


class Faktura(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    difference_som = models.IntegerField(default=0)
    difference_dollar = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '6) Faktura'


class FakturaItem(models.Model):
    name = models.CharField(max_length=255)
    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, blank=True, null=True)
    body_som = models.FloatField(default=0)
    body_dollar = models.FloatField(default=0)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '6.1) FakturaItem'

class Course(models.Model):
    som = models.IntegerField()

    def __str__(self):
        return str(self.som)

    class Meta:
        verbose_name_plural = "Dollar kursi"

class Shop(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    naqd_som = models.FloatField(default=0)
    naqd_dollar = models.FloatField(default=0)
    plastik = models.FloatField(default=0)
    nasiya_som = models.FloatField(default=0)
    nasiya_dollar = models.FloatField(default=0)
    transfer = models.FloatField(default=0)
    skidka_dollar = models.FloatField(default=0)
    skidka_som = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    saler = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '5) Shop'


class Cart(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.FloatField()
    total = models.FloatField(blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     self.total = int(self.quantity) * self.product.price
    #     super().save(*args, **kwargs)

    def __str__(self):
        try:
            return self.product.product.name
        except:
            return 'Deleted Product'

    class Meta:
        verbose_name_plural = '5.1) Cart'


class Debtor(models.Model):
    fio = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name_plural = '7) Nasiyachilar'

#
# class DebtHistory(models.Model):
#     debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
#     product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     price = models.IntegerField(default=0)
#     debt_quan = models.IntegerField(default=0)
#     pay_quan = models.IntegerField(default=0)
#     debt = models.IntegerField(default=0)
#     pay = models.IntegerField(default=0)
#     difference = models.IntegerField(default=0)
#
#     class Meta:
#         verbose_name_plural = '8) Nasiya Tarixi'


class Debt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    status = models.IntegerField(default=0)
    return_date = models.DateField()

    def __str__(self):
        return self.debtor.fio

    class Meta:
        verbose_name_plural = 'Qarz Tarixi'


class PayHistory(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField()
    dollar = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.debtor.fio

    class Meta:
        verbose_name_plural = '9) Tolov Tarixi'


class CartDebt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    given_quan = models.FloatField(default=0)
    total = models.FloatField(default=0)
    return_quan = models.FloatField(default=0)
    return_sum = models.IntegerField(default=0)
    debt_quan = models.FloatField(default=0)
    debt_sum = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.debtor.fio + " / " + self.product.product.name

    class Meta:
        verbose_name_plural = 'CartDebt'


class ReturnProduct(models.Model):
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    return_quan = models.FloatField(default=0)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.product.product.name

    class Meta:
        verbose_name_plural = 'Return Product'


class Pereotsenka(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'Pereotsenka'

class ChangePrice(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'ChangePrice'

class ChangePriceItem(models.Model):
    changeprice = models.ForeignKey(ChangePrice, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    old_som = models.FloatField(default=0)
    old_dollar = models.FloatField(default=0)
    new_som = models.FloatField(default=0)
    new_dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return self.product.product.name

    class Meta:
        verbose_name_plural = 'ChangePriceIten'

class ReturnProductToDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    kurs = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Return Product To Deliver'

class ReturnProductToDeliverItem(models.Model):
    returnproduct = models.ForeignKey(ReturnProductToDeliver, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return str(self.returnproduct.id)

    class Meta:
        verbose_name_plural = 'Return Product To Deliver Item'