from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status

from .filters import ProductFilter
from .models import Collection, Product, OrderItem, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer

# what if we want to find products by their title or description
# this is where we use searching
# searching is for text based fields
# we import searchfilter class from rest framework filters
# a search bar will be added to our filter function in our browsable api
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # using djangofilterbackend
    # adding in search filter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title','description']
    # we can also reference fields in related classes e.g below
    # search_fields = ['title','description','collection__title']



    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # otherwise call the destroy method of the base class
        return super().destroy(request, *args, **kwargs)



# class CollectionViewSet(ReadOnlyModelViewSet):
class CollectionViewSet(ReadOnlyModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):

        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # otherwise call the destroy method of the base class
        return super().destroy(request, *args, **kwargs)



# creating the view function for our reviews model
class ReviewViewSet(ModelViewSet):
    # using model view set so we have once class for listing all reviews or working with just one review

    # queryset = Review.objects.all() # this loads all reviews regardless of product
    # we need to override the get_queryset method so we can filter to get the reviews for just the product we are looking at
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    serializer_class = ReviewSerializer
    # in this view class we have access to url parameter
    # we can therfore read the product id from the url
    # and using a context object pass it to our review serialiser
    # our nested url contains two parameters, product_pk and pk
    def get_serializer_context(self):
        return  {'product_id': self.kwargs['product_pk']}

