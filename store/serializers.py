# we need a way to convert our products objects for example to json objects
# the json renderer class in rest framework takes a dict object and  converts to json
# if we convert a product object to a dict, we can therefore render it as json
# this essentially is what serialisers do

from decimal import Decimal
from store.models import  Product , Collection
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','products_count']
    # defining products count because the field doesnt exist in the collections model
    # it is an annotated field added in the collections_list view function
    products_count = serializers.IntegerField()

# class ProductSerializer(serializers.Serializer):
#     # we decide what fields from the product class we want to include our python dictionary
#     # what we return from our API doesnt necesarily need to have all the fields
#     # we define the fields to return exactly as we define fields in our models
#     # the name of the fields dont have to match. e.g unit_price below can be called price
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     # unit_price = serializers.DecimalField(max_digits=6,decimal_places=2)
#     # we can rename feilds eg below.instead of the unit_price name above. we set the source attribute
#     price = serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')
#
#
#     # just as we dont necessary need to all fields or exact field from the product class to the product serializer...
#     #.. we can also create fields that dont exist in the product class
#     # we use serialiser method fields which mean we define a method that generates the value for the field
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#     def calculate_tax(self,product): # takes two parameters. self, and the product being serialised
#         return product.unit_price * Decimal(1.1)
#
#     # when returning a product we can also serialise a relationship to return a related object like its collection
#     # collection = serializers.PrimaryKeyRelatedField(
#         # with this we can set the primary key of each collection in a product object.
#         # we set a queryset argument which is a lookup for collection objects
#         queryset=Collection.objects.all()
#         # in this implementation using primarykeyrelated fields we will render the id in the output
#         # if we want to instead render the string represntation of the related object e.g its _str_ method which is title
#         # we use stringRelatedField as done below
#     # )
#     # collection = serializers.StringRelatedField(
#     #     # we will have too many queries under the hood. one query for each product to read its collection
#     #     # to avoid this we need to load products and their collections together
#     #     # we make this change by adding the select_related argument to our product_list serializer function in our views module
#     #     # this will load the collection along with the product so the data that is serialsed by the serialiser contains all we need
#     # )
#     # another way to include a related object is by nested relationshios.
#     # we create a collections serialiser and use it in our product serialiser
#     collection = CollectionSerializer() # each collection will then be rendered as an object within the product
#
#     # another way to serialise a relationship is by including a hyperlink to an endpoint for viewing the collection
#     # we use hyperlink related field for this
#     collection = serializers.HyperlinkedRelatedField(# we need to set two argument
#         queryset= Collection.objects.all(),
#         # the view name argument below is used for generating hyperlinks
#         view_name = 'collection-detail'  # we then define the view and route in the view and urls module
#     )
    # we also need to pass our request object to our serialiser when we initialise it in the product list view function
    # ...because the request contains info about our urls
    # excluding this would generate an exception

# using the usual serialisers we define fields again. this kind of is a duplication seeing as ..
#.. we have also defined these fields in our model classes
# if we decide to change something, we have to change it in two places. in the serialiser and the model class
# using a model serialiser instead we can quickly create a serialiser without the duplication
class ProductSerializer(serializers.ModelSerializer):
    class Meta: # we set the model to include and fields in the model class we want to include
        model = Product
        fields = ['id','title','slug','inventory','unit_price','description','collection','price_with_tax']
        # notice the model serialiser above by defaul uses primary key related field to render the related collection
        # if we want, we can override this by defining the field below which uses hyperlink related field
        # if we also defined price in fields above (renaming unit_price ) which isnt defined in the model class. if the model serialiser doesnt find the field..
        #..in the model class it will look for it in the product serialiser class hence the definition of price below
        # we include price_with_tax because it is a calculated method field and doesnt exist in the model class
        # we can include all fields in the product model class by setting fields = '__all__'
        # this is bad beacuse we dont want to expose all fields. if we add a new field tomorrow, it will auto be shown

    # price = serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self,product):
        return product.unit_price * Decimal(1.1)
        queryset=Collection.objects.all()

    # collection = serializers.HyperlinkedRelatedField(
    #     queryset= Collection.objects.all(),
    #     view_name = 'collection-detail'
    # )

    # if overriding the validate method for validation of data when desrialising client sent data
    # in case we want to do some extra object validation beyond the default model field validation
    # def validate(self,data):
    #     if data['password']!=data['confirm_password']:
    #         return serializers.ValidationError('Passwords do not match')
    #     return data

    # # if overriding the create method
    # def create(self, validated_data):
    #     # we can create a product object here byt first unpacking the validated data dictionary
    #     product = Product(**validated_data)
    #     # we can then set whatever special fields we want
    #     product.other = 1
    #     product.save()
    #
    #     return product
    # # if overriding how a product is updated
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance
    # we can rely on django rest framework to automatically set these fields in the create and update methods
    # the save method will call one of the create or update methods depending on the state of the serialiser
