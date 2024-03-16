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
from .models import Collection, Product, OrderItem, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer

# currently we can see all products in our products list when we go to that endpoint
# if we wanted to filter the list by say collection to show only products in collection 1
# we cant call the filter method in our queryset attribute
# we have to override the get queryset method

# we would however need to set the basename since we override the get_queryset method
# for example, in our nested router for our products viewset , we set the basename while registering the products review route
# django uses the basename to generate the name of our url patterns
# by default django uses the queryset attribte to figure out the basename for our urls
# after deleting the queryset attribute below and using the get queryset method, django cant figure out what the name should be called based on the logic
# we thus have to explicitly specify the basename when we register the products url in our url module
class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        # return Product.objects.filter(collection_id=self.request.query_params['collection_id'])
        # in the implementation above, if we dont have a collection id, our code will therefore fail
        # the correct way to implement the filtering by collection is therefore below
        # first define a queryset
        queryset = Product.objects.all()
        # then try to read collection id from the query string
        collection_id = self.request.query_params.get('collection_id')
        if collection_id is not None:
           queryset= queryset.filter(collection_id = collection_id)
        return queryset
    def get_serializer_context(self):
        return {'request': self.request}

    # overriding the destry method rather than delete method below
    # so that delete option only pops up in our browsable api when dealing with a particular product
    def destroy(self, request, *args, **kwargs):
        # change validation logic
        # we need a product object but rather than retrieve the object again..
        # in the destroy method in the destroy model mixin , the implementation calls the obbject from the database
        # so we dont need to retrieve it twice
        # we rather change the validation logic
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

