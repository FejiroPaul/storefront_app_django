from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer

# we have our product list and product detail classes
# closely looking we can observe we have some duplication across the classes
# e.g we use the product serialiser in both cases
# querysets are similar too
# in this case we then use view sets
# using view sets we can combine the logic for multiple related views inside a single class
# to use them we import modelview set class above
# all we know from generic views also exists in generic viewsets
# we will however need to use routers to create the url routes for our viewsets

# follow the viewset naming convention for the viewset classes we create
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # using this single viewset class we can now view our products, create, update and delete
    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self,request,pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductList(ListCreateAPIView):
#     # queryset = Product.objects.select_related('collection').all()
#     # the above queryset was needed back when we needed to display the title of collection
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     def get_serializer_context(self):
#         return{'request': self.request}
#
#
#
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     # our delete method has some logic specific to our app
#     # no mixin knows about products, order items and their count
#     # we thus need to override the delete method we inherit from the generic view class
#
#
#     def delete(self,request,pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# with modelviewset we can perform operations such as read,create, update,delete etc
# what if we dont want to create and delete and so on
# we can use the readonlyModelviewSet class
# we can perform only read operations with this class such as list all collections or retrieve a single one


# class CollectionViewSet(ReadOnlyModelViewSet):
class CollectionViewSet(ReadOnlyModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def delete(self, request,pk):
        collection = get_object_or_404(Collection,pk = pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(
        products_count = Count('products')
    )
    serializer_class = CollectionSerializer

    def delete(self, request,pk):
        collection = get_object_or_404(Collection,pk = pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

