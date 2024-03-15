from decimal import Decimal
from store.models import Product, Collection, Review
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)
    # we mark the products_count field as read only because it isnt used for creating or updating a collection
    # it prevents an error when we try to put or update a collections resource..
    #... in our api, without specifying the product count


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

# creating the review serialiser
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # fields = ['id','date','name','description','product']
        # we want to read the product id directly from our url rather than input it in our api when reviwing a product
        # i.e below
        fields = ['id','date','name','description']
        # to implement this...
        # we know  the serialiser has a save method that can either create a resource or update it
        # when creating a review it would take the fields set in meta and use it to set the fileds in a reviews object
        # in our review view set class we have access to url parameter
        # we can therfore read the product id from the url
        # and using a context object pass it to our review serialiser
        # in our serialiser here we override the create method here for creating a reviw
    def create(self,validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(
            product_id= product_id, **validated_data
        )

