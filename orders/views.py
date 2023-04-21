from decimal import Decimal

from rest_framework import viewsets, generics
from rest_framework.views import Response, status

from shop.models import Product

from .models import Order
from .serailizers import OrderSerializer


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            product = Product.objects.get(id=product_id)

            payment_price = Decimal(request.data.get('price'))
            product_price = product.price
            paid_payment = False

            if payment_price == 0.00 and product_price == 0.00:
                paid_payment = True
            elif payment_price < product_price:
                return Response(
                    {'detail': f'You can\'t pay {payment_price} for a {product_price} product'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order = Order(product=product, price=payment_price, paid=paid_payment)
            order.save()
            
            return Response(OrderSerializer(order.data), status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'This product is not available'},
                status=status.HTTP_404_NOT_FOUND
            )


class PayOut(generics.ListAPIView):
    queryset = Order.objects.filter(paid=True)
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        payouts = []
        for order in queryset:
            if order.product.creator == user:
                payouts.append(order.id)
                
        return Order.objects.filter(id__in=payouts)
                
    