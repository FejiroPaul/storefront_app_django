from store.pagination import DefaultPagination
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .filters import ProductFilter
from .models import Collection, Product, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer


# for the cart api...
# we have to support various operations and endpoints
# we should be able to create a cart, add items to a cart, update the quantity of items, remove items from a cart,
#.. get a cart with its items and finally delete a cart
# for creating a cart.........
## we will send a post request with an empty object to the carts endpoint /carts/. we use an empty object and no user id..
# because our carts our anonymous as we dont want to force users to login before adding items to cart
# this created cart should have a unique identifier which we will save on the client for subsequent requests
# so when the user adds an item to the cart we will send the cart id to the server
# for getting a cart, we will send a cart object to the endpoint /carts/:id to get a cart object
# for deleting a cart we send a delete request to the /carts/:id/endpoint also
# for adding items to a cart we send  a post request to the endpoint carts/:id/items. we will only send product id and..
#.. quantity in the body of the request because we already have cart id in the url
# we send this request and get back the item that was created. this item will also have a unique identifier used for subsequent request
# for example when updating an item we send a patch request to the endpoint carts/:id/items/:id. in the body of the request..
#.. we will send the quanity and in the response we will get the updated quantity. we will only support a patch request ..
#.. and not a put request because with put we replace an internal object but here we arent doing that. we just want to update its quantity
# for deleting an item we send a delete request to this endpoint /carts/:id/items/:id
# we therefore have four new endpoints
# /carts , /carts/:id
# /carts/:id/items , /carts/:id/items/:id
# we can implement the first two endpoints using a viewset called CartViewSet
# and the other two using a CartItemViewSet
# we also need to revisit our data model for the cart class
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
