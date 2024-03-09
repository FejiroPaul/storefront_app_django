from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer
# using djangos response or request class below
from django.http import HttpResponse
# or rather using the more powerful rest framework reponse and request classes
# first import the api view decorator and then response class
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# if the api view decorator is applied on a view function, the request object received in the function..
# .. will become an instance of the request class that comes with rest framework which is simpler and more powerful
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == "GET":
        # return HttpResponse('ok')
        # replacing the django framework response object above with rest framework response below
        # return Response('ok')  # this gives us a browsable Api page as our response page

        # queryset = Product.objects.all() # this doesn't load the related collection for our product serialiser and
        #  thus leads to multiple sub queries. we then use select_related below
        queryset = Product.objects.select_related('collection').all()
        # since we are dealing with a queryset....
        # we have to set many to true when using th serialiser below so the serialiser know it should iterate over..
        # ... the items in the queryset and convert each object to a dictionary
        serializer = ProductSerializer(queryset, many=True,
                                       # we need to pass our request object to our serialiser when we initialise it here
                                       # ...because the request contains info about our urls we need in our defined collection hyperlink related field
                                       # by using the context object below we can give the serialise extra stuff e.g request
                                       context={
                                           'request': request
                                       }
                                       )
        return Response(serializer.data)
    elif request.method == "POST":
        # to deserialise an object we have to set the data argument to request.data
        serializer = ProductSerializer(data=request.data)
        # the deserialised data would then be available in an attribute called validated data which we can access after validtaing the data
        # if serializer.is_valid():
        #     serializer.validated_data
        #     return Response('ok')
        # else: # raise an exception using the status module imported from rest framework
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # rather than the if else block we can write the lines above using the raise_exception argument
        # django automatically would raise the 404 error
        serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)

        # sometimes we also need to consider validation at the object level. sometimes we may even need to compare fields
        # for example checking that a user password is same as confirm password field
        # the validation via is_valid comes from the model definition and cant help us achieve this
        # if we need any extra validation we must override the validate method in our product serialiser

        # we may want to override the way a product object is created
        # e.g set some special fields or associate the product with another object in the database
        # we override the create method in the product serialiser definition
        # create method is one of the methods in the base model serialiser class
        #  it is called by default if we try to save a new product

        # saving the validated data
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# deserialisation is the opposite of serialisation. it happens when you receive data from the client
# a user send a post request for example, with product object included in the body of the request
# we have to deserialise it so we get the product object and store it in the database
# in our api_view decorator we add an array which states the http methods supported at that endpoint
# we then include the if statements to handle the type of requests


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)

    if request.method == 'GET':
        # we use the product serialiser in the serialiser module to convert our product object to a json object
        # ....and then include it in the response. first import the models and serialiser product classes above

        # wrapping in a try block to handle cases when a product does not exist
        # try:
        #     product = Product.objects.get(pk=id)
        #     # create serializer and give it product object retrieved above
        #     serializer = ProductSerializer(product)
        #     # get the data in json and return in
        #     return Response(serializer.data)
        # except Product.DoesNotExist:
        #     # return Response(status=404)
        #     # using the status module from rest framework instead
        #     return Response(status=status.HTTP_404_NOT_FOUND)

        # we can wrap the logic above to get an object or a 404 response by using the get object or 404 function from django shortcuts
        # product = get_object_or_404(Product,pk=id) #pass in type of model and the lookup parameter
        # (line above moved to outside if block so can be accessed by elif and else blocks)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # to update a method we send a put or patch request to a particular product
    elif request.method == 'PUT':
        # we need desrialise, validate it and save it in the database
        # in the deserialistion below we pass a product instance so the serialiser will try to update the attributes of the product
        # ...with the request data
        # in this case, when we try to save the serialiser, it will call the update method because we initialise it
        # .. with we instantiate with an existing product and data to be serialised
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        # before deleting the product we should ideally check for any order items associated with the product
        # note that orderitems is the related name defined in the order items model class
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cant be deleted because assoicted with an order item'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # delete the product that we retrieved
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == "GET":
        # we annotate our queryset with a count of products for each collection
        # this field thus has to be defined in our collections serialiser since it doesnt exist in the model
        queryset = Collection.objects.annotate(products_count=Count('products')).all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# view function for our hyperlink related field in the product serialiser
@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    # check if collection object exists
    collection = get_object_or_404(
        Collection.objects.annotate(
            products_count=Count('products')), pk=pk
    )
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cant be deleted bcus it includes one or more products'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
