from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.generics import ListCreateAPIView
from rest_framework import status
from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer


# in the productlist view get method we create a queryset
# feed into a serialiser
# return the response with serialised data
# we have the same pattern for listing our collections
# the two differences in both places is how we create our queryset and the serialiser used
# the post method for products and collections also have similarities
# in cases like this, mixings then come into play
# we import mixins from restframework above
# we have different mixings for performing different operations on resources
# most times we dont use mixins directly
# we use classes that combine one or more mixins and these are called generic views
# e.g listcreatapiview which combines list model mixin and create model mixin
# import particular generic view from generics above and let the view funciton below inherit from it

# generic view also grant us added functionality in our browsable api for creating resources

class ProductList(ListCreateAPIView):
    # we have to override two methods
    # the get queryset method and the get serialiser context
    # def get_queryset(self):
    #     return Product.objects.select_related('collection').all()
    # def get_serializer_class(self):
    #     # we return a class not an object
    #     return ProductSerializer
    # note that in our initial serialiser in the get method, we add in a context object
    # we do the same by overriding the get_serializer_context method for the generic view

    # overriding the get_queryset and get serilaiser class methods above are useful when we have a certain logic we want to implement
    # for example checking a user then returning a queryset based on permissions
    # if we are just returning a queryset expression or serialiser class..
    #.. we can instead just use the generic view attributes below

    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    def get_serializer_context(self):
        return{'request': self.request}

    # we no longer need the methods below because they are already implemented in by the generic view

    # def get(self,request):
    #     queryset = Product.objects.select_related('collection').all()
    #     serializer = ProductSerializer(
    #         queryset, many=True, context={'request': request})
    #     return Response(serializer.data)
    # def post(self,request):
    #     serializer = ProductSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductDetail(APIView):
    def get(self,request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    def put(self,request,id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self,request,id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollcetionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(
        Collection.objects.annotate(
            products_count=Count('products')), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

