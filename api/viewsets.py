from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import tablib
from django.db.models import Q, Sum
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


def month():
    date = datetime.today()
    year = date.year
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year, date.month + 1, 1, 0, 0, 0)

    return gte, lte


class TokenViewset(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer


class UserProfileViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(methods=['post'], detail=False)
    def login(self, request):
        r = request.data
        password = r['password']
        try:
            user = UserProfile.objects.get(password=password)
            s = self.get_serializer_class()(user).data
            token = Token.objects.first()
            return Response({
                'user': s,
                'token': token.key
            })
        except:
            return Response({'message': 'Bunday foydalanuvchi yo`q'}, status=401)

    @action(methods=['get'], detail=False)
    def hodim(self, request):
        emp = UserProfile.objects.filter(staff__gt=1)
        data = []
        for e in emp:
            if e.staff == 2:
                st = 'manager'
            elif e.staff == 3:
                st = 'saler'
            else:
                st = 'warehaouse'
            t = {
                'first_name': e.first_name,
                'last_name': e.last_name,
                'phone': e.phone,
                'staff': st,
                'filial': e.filial.name,
            }
            data.append(t)

        return Response(data)

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        f = request.GET.get('f')
        emp = UserProfile.objects.filter(staff__gt=1, filial_id=f)
        data = []
        for e in emp:
            if e.staff == 2:
                st = 'manager'
            elif e.staff == 3:
                st = 'saler'
            else:
                st = 'warehaouse'
            t = {
                'id': e.id,
                'first_name': e.first_name,
                'last_name': e.last_name,
                'phone': e.phone,
                'staff': st,
                'filial': e.filial.name,
            }
            data.append(t)

        return Response(data)


class FilialViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer


class GroupsViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class DeliverViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Deliver.objects.all()
    serializer_class = DeliverSerializer


class ProductViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    search_fields = ['name', ]

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        recieve = r['recieve']
        re = Recieve.objects.get(id=recieve)

        recieves = RecieveItem.objects.filter(recieve=re)
        for r in recieves:
            product = Product.objects.filter(barcode=r.product.barcode)
            try:
                p = Product.objects.get(name=r.product.name, preparer=r.product.preparer, som=r.som, dollar=r.dollar,
                                        kurs=r.kurs)
                p.quantity += r.quantity
                p.save()
            except:
                Product.objects.create(name=r.product.name, group=r.product.group, preparer=r.product.preparer,
                                       quantity=r.quantity, barcode=r.product.barcode, som=r.som, dollar=r.dollar,
                                       kurs=r.kurs)
            for p in product:
                if p.quantity == 0:
                    p.delete()
        re.status = 1
        re.deliver.som -= re.som
        re.deliver.dollar -= re.dollar
        re.deliver.save()
        re.save()
        DebtDeliver.objects.create(deliver=re.deliver, som=-re.som, dollar=-re.dollar)

        return Response({'message': 'done'}, status=200)

    @action(methods=['post'], detail=False)
    def xlsx(self, request):
        file = request.FILES['file']

        data = tablib.Dataset().load(file, format='xlsx')
        for d in data:
            p = Product.objects.filter(barcode=d[7]).first()
            if p:
                pass
            else:
                if d[2]:
                    Product.objects.create(
                        name=d[0],
                        group_id=d[6],
                        dollar=d[2],
                        kurs=10500,
                        quantity=d[1],
                        barcode=d[7]
                    )
                elif d[3]:
                    Product.objects.create(
                        name=d[0],
                        group_id=d[6],
                        som=d[3],
                        kurs=10500,
                        quantity=d[1],
                        barcode=d[7]
                    )

        return Response({'message': 'done'})

    @action(methods=['post'], detail=False)
    def product_add_from_xlsx(self, request):
        file = request.FILES['file']

        data = tablib.Dataset().load(file, format='xlsx')
        for d in data:
            print(d[1])
            print(d[3])
            Product.objects.create(
                    name=d[1],
                    group_id=d[3]
            )
        return Response({'message': 'done'})

class ProductFilialViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductFilial.objects.all()
    serializer_class = ProductFilialSerializer
    pagination_class = StandardResultsSetPagination

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        id = request.GET.get('f')
        d = ProductFilial.objects.filter(filial_id=id)

        page = self.paginate_queryset(d)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(d, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        filial = int(r['filial'])
        faktura = int(r['faktura'])
        # difference = float(r['difference'])
        fakturaitems = FakturaItem.objects.filter(faktura_id=faktura)
        dif_som = 0
        dif_dollar = 0
        for fakturaitem in fakturaitems:
            product = ProductFilial.objects.filter(filial=filial, product=fakturaitem.product)
            if len(product) > 0:
                product = product.first()
                if product.som != fakturaitem.som:
                    dif_som += (fakturaitem.som - product.som) * product.quantity
                    product.som = fakturaitem.som
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
                elif product.dollar != fakturaitem.dollar:
                    dif_dollar += (fakturaitem.dollar - product.dollar) * product.quantity
                    product.dollar = fakturaitem.dollar
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
                else:
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
            else:
                ProductFilial.objects.create(product=fakturaitem.product, som=fakturaitem.som, dollar=fakturaitem.dollar,
                                             quantity=fakturaitem.quantity, filial_id=filial,
                                             barcode=fakturaitem.barcode)
        faktur = Faktura.objects.get(id=faktura)
        faktur.difference_som = dif_som
        faktur.difference_dollar = dif_dollar
        faktur.status = 2
        faktur.save()

        return Response({'message': 'done'}, status=200)

    @action(methods=['get'], detail=False)
    def search(self, request):
        f = request.GET.get('f')
        q = request.GET.get('q')
        query = ProductFilial.objects.filter(Q(filial_id=f) & Q(product__name__icontains=q) | Q(product__barcode=q))
        d = self.get_serializer_class()(query, many=True).data

        return Response(d)

    @action(methods=['post'], detail=False)
    def xlsx(self, request):
        file = request.FILES['file']

        data = tablib.Dataset().load(file, format='xlsx')
        for d in data:
            p = Product.objects.get(barcode=d[7])
            pro = ProductFilial.objects.filter(barcode=d[7])
            if len(pro) == 0:
                ProductFilial.objects.create(
                    product=p,
                    som=d[5],
                    dollar=d[6],
                    quantity=d[1],
                    filial_id=1,
                    barcode=p.barcode
                )
            else:
                pass

        return Response({'message': 'done'})

    @action(methods=['post'], detail=False)
    def up(self, request):
        if request.method == "POST":
            bar = request.data['barcode']
            filial = request.data['filial']
            som = float(request.data['som'])
            dollar = float(request.data['dollar'])
            p = ProductFilial.objects.filter(barcode=bar, filial_id=filial)
            for i in p:
                print(i.som, som)
                if i.som == som:
                    if i.dollar == dollar:
                        print('11')
                        pass
                    else:
                        dollar1 = (dollar - i.dollar) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, dollar=dollar1)
                        i.dollar = dollar
                        i.save()
                        print('222')
                else:
                    if i.dollar == dollar:
                        som1 = (som - i.som) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, som=som1)
                        i.som = som
                        i.save()
                        print('333')
                    else:
                        som1 = (som - i.som) * i.quantity
                        dollar1 = (dollar - i.dollar) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, som=som1, dollar=dollar1)
                        i.som = som
                        i.dollar = dollar
                        i.save()
                        print('444')
        return Response({'message': 'done'}, status=200)


class RecieveViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recieve.objects.all()
    serializer_class = RecieveSerializer

    @action(methods=['get'], detail=False)
    def recieve0(self, request):
        recieve = Recieve.objects.filter(status=0)

        s = self.get_serializer_class()(recieve, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def recieve1(self, request):
        id = request.GET.get('id')
        r = Recieve.objects.get(id=id)
        r.status = 1
        r.save()

        return Response({'message': 'done'}, status=200)


class RecieveItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RecieveItem.objects.all()
    serializer_class = RecieveItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        recieve = int(r['recieve'])
        product = int(r['product'])
        som = float(r['som'])
        dollar = float(r['dollar'])
        kurs = float(r['kurs'])
        quantity = float(r['quantity'])
        rec = Recieve.objects.get(id=recieve)
        try:
            r = RecieveItem.objects.create(recieve=rec, product_id=product, som=som, dollar=dollar, kurs=kurs,
                                           quantity=quantity)
            if som == 0:
                rec.dollar += dollar * quantity
                rec.save()
            else:
                rec.som += som * quantity
                rec.save()
            s = self.get_serializer_class()(r)
            return Response(s.data, status=201)
        except:
            return Response({'message': 'error'}, status=401)

    @action(methods=['get'], detail=False)
    def rv1(self, request):
        rec = request.GET.get('rec')
        revieve = RecieveItem.objects.filter(recieve_id=rec)

        s = self.get_serializer_class()(revieve, many=True)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def up(self, request):
        r = request.data
        item = int(r['item'])
        dollar = float(r['dollar'])
        kurs = float(r['kurs'])
        som = float(r['som'])
        try:
            quantity = float(r['quantity'])
        except:
            pass
        it = RecieveItem.objects.get(id=item)
        recieve = it.recieve
        if som == 0:
            recieve.dollar = recieve.dollar - (it.dollar * it.quantity) + dollar * quantity
            it.dollar = dollar
            it.kurs = kurs
            try:
                it.quantity = quantity
            except:
                pass
            recieve.save()
            it.save()
        elif dollar == 0:
            recieve.som = recieve.som - (it.som * it.quantity) + som * quantity
            it.som = som
            it.quantity = quantity
            try:
                it.quantity = quantity
            except:
                pass
            recieve.save()
            it.save()

        s = self.get_serializer_class()(it)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def delete(self, request):
        r = request.data
        item = int(r['item'])
        it = RecieveItem.objects.get(id=item)
        recieve = it.recieve

        if it.som == 0:
            recieve.dollar = recieve.dollar - (it.dollar * it.quantity)
            recieve.save()
        elif it.dollar == 0:
            recieve.som = recieve.som - (it.som * it.quantity)
            recieve.save()
        it.delete()
        return Response({'message': 'done'})


class FakturaViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Faktura.objects.all()
    serializer_class = FakturaSerializer
    pagination_class = StandardResultsSetPagination

    @action(methods=['post'], detail=False)
    def st(self, request):
        r = request.data
        faktura = int(r['faktura'])
        try:
            f = Faktura.objects.get(id=faktura)
            f.status = 1
            f.save()
            return Response({'message': 'status o`zgardi'}, status=200)
        except:
            return Response({'message': 'error'}, status=400)

    @action(methods=['get'], detail=False)
    def st1(self, request):
        fil = request.GET.get('fil')
        faktura = Faktura.objects.filter(filial_id=fil, status=1)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def st2(self, request):
        fil = request.GET.get('fil')
        faktura = Faktura.objects.filter(filial_id=fil, status=2)

        st = []
        for f in faktura:
            t = {
                'id': f.id,
                'date': f.date.strftime('%Y-%m-%d %H:%M:%S'),
                'som': f.som,
                'dollar': f.dollar,
                'filial': f.filial.id,
                'status': f.status,
                'difference': f.difference,
                'message': "Qabul qilingan",
            }
            st.append(t)
        page = self.paginate_queryset(st)
        if page is not None:
            return self.get_paginated_response(st)

        return Response(st, status=200)

    @action(methods=['get'], detail=False)
    def ombor1(self, request):
        faktura = Faktura.objects.filter(status=1)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def ombor0(self, request):
        faktura = Faktura.objects.filter(status=0)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def otkaz(self, request):
        fak = request.GET.get('fak')
        faktura = Faktura.objects.get(id=fak)
        items = FakturaItem.objects.filter(faktura_id=fak)
        try:
            for i in items:
                prod = Product.objects.get(id=i.product.id)
                prod.quantity += i.quantity
                prod.save()
            faktura.status = 3
            faktura.save()
            return Response({'message': 'done'}, status=200)
        except:
            return Response({'message': 'error'}, status=400)

    @action(methods=['get'], detail=False)
    def monthly(self, request):
        gte, lte = month()
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        gte, lte = month()
        f = request.GET.get('f')
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte, filial_id=f, status=2)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def range(self, request):
        gte = request.data['sana1']
        lte = request.data['sana2']

        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def range_by_filial(self, request):
        gte = request.data['sana1']
        lte = request.data['sana2']
        f = request.data['f']
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte, filial_id=f, status=2)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)


class FakturaItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FakturaItem.objects.all()
    serializer_class = FakturaItemSerializer

    @action(methods=['get'], detail=False)
    def by_faktura(self, request):
        id = request.GET.get('faktura')
        item = FakturaItem.objects.filter(faktura_id=id)
        d = FakturaItemReadSerializer(item, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        name = r['name']
        barcode = r['barcode']
        faktura = int(r['faktura'])
        product = int(r['product'])
        som = float(r['som'])
        dollar = float(r['dollar'])
        body_som = float(r['body_som'])
        body_dollar = float(r['body_dollar'])
        group = int(r['group'])
        quantity = float(r['quantity'])
        try:
            prod = Product.objects.get(id=product)
            fak = Faktura.objects.get(id=faktura)
            f = FakturaItem.objects.create(faktura_id=faktura, name=name, barcode=barcode, product_id=product,
                                           som=som, dollar=dollar, body_som=body_som, body_dollar=body_dollar,  quantity=quantity, group_id=group)
            if som > 0:
                fak.som += som * quantity
            elif dollar > 0:
                fak.dollar += dollar * quantity
            fak.save()
            prod.quantity -= quantity
            prod.save()
            s = self.get_serializer_class()(f)
            return Response(s.data, status=201)
        except:
            return Response({'message': 'error'}, status=401)

    @action(methods=['get'], detail=False)
    def st1(self, request):
        fak = request.GET.get('fak')
        faktura = FakturaItem.objects.filter(faktura_id=fak)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def up(self, request):
        r = request.data
        item = int(r['item'])
        fak = FakturaItem.objects.get(id=item)
        faktura = fak.faktura
        try:
            price = int(r['price'])
            faktura.summa = faktura.summa - (fak.price * fak.quantity) + fak.quantity * price
            fak.price = price
            fak.save()
            faktura.save()
        except:
            pass
        try:
            quantity = float(r['quantity'])
            faktura.summa = faktura.summa - (fak.price * fak.quantity) + fak.price * quantity
            fak.quantity = quantity
            fak.save()
            faktura.save()
        except:
            pass
        s = self.get_serializer_class()(fak)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def delete(self, request):
        r = request.data
        item = int(r['item'])
        fak = FakturaItem.objects.get(id=item)
        faktura = fak.faktura

        faktura.summa = faktura.summa - fak.price * fak.quantity
        faktura.save()
        fak.delete()

        return Response({'message': 'done'})


class ShopViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data.get
            naqd_som = r('naqd_som')
            naqd_dollar = r('naqd_dollar')
            plastik = r('plastik')
            transfer = r('transfer')
            skidka_som = r('skidka_som')
            skidka_dollar = r('skidka_dollar')
            filial = r('filial')
            saler = r('saler')

            try:
                nasiya_som = r('nasiya_som')
                nasiya_dollar = r('nasiya_dollar')
                fio = request.data['fio']
                sh = Shop.objects.create(naqd_som=naqd_som, naqd_dollar=naqd_dollar, nasiya_som=nasiya_som, nasiya_dollar=nasiya_dollar, plastik=plastik, transfer=transfer,
                                         skidka_som=skidka_som, skidka_dollar=skidka_dollar, filial_id=filial, saler_id=saler)
                phone = r('phone')
                try:
                    d = Debtor.objects.get(fio=fio, phone1=phone)
                except:
                    d = Debtor.objects.create(fio=fio, phone1=phone)
                d.som += nasiya_som
                d.dollar += nasiya_dollar
                d.save()

                return Response({'message': 'Shop qo`shildi. Debtor yangilandi'}, status=201)
            except:
                sh = Shop.objects.create(naqd_som=naqd_som, naqd_dollar=naqd_dollar, plastik=plastik, transfer=transfer,
                                         skidka_som=skidka_som, skidka_dollar=skidka_dollar, filial_id=filial, saler_id=saler)

                return Response({'message': 'Shop qo`shildi.'}, status=201)

    @action(methods=['post'], detail=False)
    def by_date(self, request):

        r = request.data
        date1 = r['date1']
        date2 = r['date2']
        f = r['filial']

        sh = Shop.objects.filter(date__gte=date1, date__lt=date2, filial_id=f)
        data = self.get_serializer_class()(sh, many=True).data

        return Response(data)

    @action(methods=['get'], detail=False)
    def by_hodim(self, request):
        id = request.GET.get('id')
        today = datetime.today()
        sana1 = datetime(today.year, today.month, today.day)
        sh = Shop.objects.filter(date__gte=sana1, saler_id=id)
        t = sh.aggregate(jami=Sum('summa'), n=Sum('naqd'), p=Sum('plastik'), t=Sum('transfer'), c=Sum('currency'),
                         nas=Sum('nasiya'))
        j = {
            'jami': t['jami'],
            'naqd': t['n'],
            'plastik': t['p'],
            'transfer': t['t'],
            'nasiya': t['nas'],
            'valyuta': t['c']
        }
        return Response(j)

    @action(methods=['post'], detail=False)
    def by_date_and_hodim(self, request):
        r = request.data
        date1 = r['date1']
        date2 = r['date2']
        id = r['id']
        t = Shop.objects.filter(date__gte=date1, date__lt=date2, saler_id=id).aggregate(jami=Sum('summa'),
                                                                                        n=Sum('naqd'), p=Sum('plastik'),
                                                                                        t=Sum('transfer'),
                                                                                        c=Sum('currency'),
                                                                                        nas=Sum('nasiya'))
        j = {
            'jami': t['jami'],
            'naqd': t['n'],
            'plastik': t['p'],
            'transfer': t['t'],
            'nasiya': t['nas'],
            'valyuta': t['c']
        }
        return Response(j)


class CartViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        summa = r['summa']
        naqd = r['naqd']
        plastik = r['plastik']
        nasiya = r['nasiya']
        transfer = r['transfer']
        currency = r['currency']
        skidka_dollar = r['skidka_dollar']
        skidka_som = r['skidka_som']
        filial = r['filial']
        saler = r['saler']
        items = r['items']

        sh = Shop.objects.create(summa=summa, naqd=naqd, plastik=plastik, nasiya=nasiya, transfer=transfer,
                                 filial_id=filial, saler_id=saler, currency=currency, skidka_dollar=skidka_dollar,
                                 skidka_som=skidka_som)
        for i in items:
            pr = ProductFilial.objects.get(id=i['product'])
            Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=pr.price,
                                total=pr.price * i['quantity'])
        try:
            debtor = r['debtor']
            dollar = r['dollar']
            d = Debtor.objects.get(id=debtor)
            d.debts += nasiya
            d.debts_dollar += dollar
            d.save()
            Debt.objects.create(debtorr_id=debtor, shop=sh, return_date=r['return_date'], dollar=dollar)
        except:
            pass
        return Response({'message': 'done'})

    @action(methods=['post'], detail=False)
    def mobil_add(self, request):
        if request.method == 'POST':
            r = request.data
            naqd = float(r['naqd'])
            plastik = float(r['plastik'])
            transfer = float(r['transfer'])
            currency = float(r['currency'])
            saler = int(r['saler'])
            items = r['items']
            filial = int(r['filial'])
            nasiya = float(r['nasiya'])
            if nasiya > 0:
                sh = Shop.objects.create(naqd=naqd, plastik=plastik, nasiya=nasiya, saler_id=saler, transfer=transfer,
                                         filial_id=filial, currency=currency)
                summ = 0
                dif = 0
                for i in items:
                    p = ProductFilial.objects.get(id=i['product'])
                    if i['summa'] > 0:
                        Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=i['summa'],
                                            total=i['summa'] * i['quantity'])
                        dif += (i['summa'] - p.price) * i['quantity']
                        summ += i['summa'] * i['quantity']
                    else:
                        Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=p.price,
                                            total=p.price * i['quantity'])
                        summ += p.price * i['quantity']
                    p.quantity = p.quantity - i['quantity']
                    p.save()
                debtor = r['debtor']
                dollar = r['dollar']
                return_date = r['return_date']
                sh.summa = summ
                sh.difference = dif
                sh.save()
                d = Debtor.objects.get(id=debtor)
                Debt.objects.create(debtor=d, shop=sh, return_date=return_date, dollar=dollar)
                d.debts += nasiya
                d.save()
                if currency > 0:
                    dlar = Course.objects.last()
                    sh.summa += currency * dlar.som
                    sh.save()
                return Response({'message': 'Shop qo`shildi. Debtor yangilandi'}, status=201)
            else:
                sh = Shop.objects.create(naqd=naqd, plastik=plastik, saler_id=saler, transfer=transfer,
                                         filial_id=filial, currency=currency)
                summ = 0
                dif = 0
                for i in items:
                    p = ProductFilial.objects.get(id=i['product'])
                    if i['summa'] > 0:
                        Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=i['summa'],
                                            total=i['summa'] * i['quantity'])
                        dif += (i['summa'] - p.price) * i['quantity']
                        summ += i['summa'] * i['quantity']
                    else:
                        Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=p.price,
                                            total=p.price * i['quantity'])
                        summ += i['summa'] * i['quantity']
                    p.quantity = p.quantity - float(i['quantity'])
                    p.save()
                    sh.summa = summ
                    sh.difference = dif
                    sh.save()
                    if currency > 0:
                        dlar = Course.objects.last()
                        sh.summa += currency * dlar.som
                        sh.save()
                return Response({'message': 'Shop qo`shildi.'}, status=201)


class DebtorViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer

    @action(methods=['post'], detail=False)
    def up(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                fio = r['fio']
                phone1 = r['phone1']
                debts = float(r['debts'])
                debts_dollar = float(r['debts_dollar'])
                difference = float(r['difference'])
                d = Debtor.objects.get(fio=fio, phone1=phone1)
                d.debts = debts
                d.debts_dollar = debts_dollar
                d.difference = difference
                d.save()
                return Response({'message': 'Debtor update bo`ldi.'}, status=200)
            except:
                return Response({'message': 'data not found'}, status=400)
        else:
            return Response({'message': 'error'}, status=400)


class DebtViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    @action(methods=['get'], detail=False)
    def by_debtor(self, request):
        id = request.GET.get('d')
        data = Debt.objects.filter(status=0, debtor_id=id)
        d = self.get_serializer_class()(data, many=True)
        return Response(d.data)


class PayHistoryViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PayHistory.objects.all()
    serializer_class = PayHistorySerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                fio = r['fio']
                phone1 = r['phone1']
                som = float(r['som'])
                dollar = float(r['dollar'])
                filial = int(r['filial'])
                d = Debtor.objects.get(fio=fio, phone1=phone1)
                try:
                    PayHistory.objects.create(debtor=d, som=som, dollar=dollar, filial_id=filial)
                    d.som = d.som - som
                    d.dollar = d.dollar - dollar
                    d.save()
                    return Response({'message': 'To`lov qabul qilindi.'}, 200)
                except:
                    return Response({'message': 'error'}, 401)
            except:
                return Response({'message': 'data not found'}, status=400)
        else:
            return Response({'message': 'error'}, 401)

    @action(methods=['post'], detail=False)
    def pay(self, request):
        r = request.data
        p = PayHistory.objects.create(debtor_id=r['debtor'], filial_id=r['filial'], sum=r['summa'], dollar=r['dollar'])
        d = Debtor.objects.get(id=r['debtor'])
        d.debts -= r['summa']
        d.debts_dollar -= r['dollar']
        d.save()
        s = self.get_serializer_class()(p).data
        return Response(s)

    @action(methods=['post'], detail=False)
    def pay_from_mobil(self, request):
        r = request.data
        debt_id = r['debt']
        debt = Debt.objects.get(id=debt_id)
        return_sum = float(r['return_sum'])
        return_dollar = float(r['return_dollar'])
        p = PayHistory.objects.create(debtor=debt.debtor, filial=debt.shop.filial, sum=return_sum)
        d = Debtor.objects.get(id=debt.debtor.id)
        d.debts -= return_sum
        d.debts_dollar -= return_dollar
        d.save()

        debt.return_sum = return_sum
        if debt.shop.nasiya == debt.return_sum:
            debt.status = 1
        debt.save()
        s = self.get_serializer_class()(p).data
        return Response(s)


class CartDebtViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CartDebt.objects.all()
    serializer_class = CartDebtSerializer


class ReturnProductViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ReturnProduct.objects.all()
    serializer_class = ReturnProductSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                return_quan = float(r['return_quan'])
                som = float(r['som'])
                dollar = float(r['dollar'])
                filial = r['filial']
                difference = float(r['difference'])
                status = int(r['status'])
                barcode = r['barcode']
                try:
                    prod = ProductFilial.objects.filter(filial_id=filial, product__barcode=barcode).first()
                    ReturnProduct.objects.create(product=prod, filial_id=filial,
                                                 return_quan=return_quan, som=som, dollar=dollar,
                                                 difference=difference,
                                                 status=status, barcode=barcode)

                    prod = ProductFilial.objects.filter(filial_id=filial, product__barcode=barcode).first()

                    prod.quantity += return_quan
                    prod.save()
                    if status == 1:
                        fio = r['fio']
                        phone1 = r['phone1']
                        d = Debtor.objects.get(fio=fio, phone1=phone1)
                        d.som = d.som - som
                        d.dollar = d.dollar - dollar
                        d.save()
                    return Response({'message': 'done'}, 200)
                except Exception as e:
                    print(e)
                    return Response({'message': 'create qilishda xatolik'}, 401)
            except Exception as e:
                print(e)
                return Response({'message': 'data not found'}, 401)
        else:
            return Response({'message': 'error'}, 401)

    @action(methods=['post'], detail=False)
    def ad(self, request):
        r = request.data
        product = int(r['product'])
        quantity = float(r['quantity'])
        summa = float(r['summa'])

        prod = ProductFilial.objects.get(id=product)
        r = ReturnProduct.objects.create(product_id=product, return_quan=quantity, summa=summa,
                                         difference=quantity * (summa - prod.price), filial=prod.filial,
                                         barcode=prod.barcode)
        d = self.get_serializer_class()(r).data

        return Response(d)


class ChangePriceViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ChangePrice.objects.all()
    serializer_class = ChangePriceSerializer


class ChangePriceItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ChangePriceItem.objects.all()
    serializer_class = ChangePriceItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        filial = r['filial']
        items = r['items']
        ch = ChangePrice.objects.create(filial_id=filial)
        for i in items:
            prod = ProductFilial.objects.filter(barcode=i['barcode']).first()
            ChangePriceItem.objects.create(changeprice=ch, product=prod, old_som=prod.som, old_dollar=prod.dollar,
                                           new_som=i['som'], new_dollar=i['dollar'], quantity=prod.quantity)
            prod.som = i['som']
            prod.dollar = i['dollar']
            prod.save()
        chitems = ChangePriceItem.objects.filter(changeprice=ch)
        dt = ChangePriceItemSerializer(chitems, many=True).data
        return Response(dt)


class ReturnProductToDeliverViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = ReturnProductToDeliver.objects.all()
    serializer_class = ReturnProductToDeliverSerializer


class ReturnProductToDeliverItemViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = ReturnProductToDeliverItem.objects.all()
    serializer_class = ReturnProductToDeliverItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        deliver = r['deliver']
        filial = r['filial']
        som = r['som']
        dollar = r['dollar']
        kurs = r.get('dollar')
        items = r['items']
        ret = ReturnProductToDeliver.objects.create(deliver_id=deliver, som=som, dollar=dollar, filial_id=filial, kurs=kurs)
        for i in items:
            prod = ProductFilial.objects.get(barcode=i['barcode'], filial_id=filial)
            ReturnProductToDeliverItem.objects.create(returnproduct=ret, product=prod, som=i['som'], dollar=i['dollar'],
                                                      quantity=i['quantity'])
            prod.quantity -= i['quantity']
            prod.save()
        data = ReturnProductToDeliverItem.objects.filter(returnproduct=ret)
        dt = self.get_serializer_class()(data, many=True).data
        return Response(dt)


    @action(methods=['post'], detail=False)
    def add_mobil(self, request):
        r = request.data
        deliver = r['deliver']
        filial = r['filial']
        som = r['som']
        dollar = r['dollar']
        items = r['items']
        ret = ReturnProductToDeliver.objects.create(deliver_id=deliver, som=som, dollar=dollar, filial_id=filial)
        for i in items:
            prod = ProductFilial.objects.get(id=i['product'])
            ReturnProductToDeliverItem.objects.create(returnproduct=ret, product=prod, som=i['som'], dollar=i['dollar'],
                                                      quantity=i['quantity'])
            prod.quantity -= i['quantity']
            prod.save()
        data = ReturnProductToDeliverItem.objects.filter(returnproduct=ret)
        deli = Deliver.objects.get(id=deliver)
        deli.som -= som
        deli.dollar -= dollar
        deli.save()

        dt = self.get_serializer_class()(data, many=True).data
        return Response(dt)