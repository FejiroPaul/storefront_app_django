from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import F
from django.db import transaction, connection
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product,Order, OrderItem, Collection # every model in django has object called objects
from tags.models import TaggedItem

# Create your views here.
# views are request handlers

# def calculate():
#     x = 1
#     y = 2
#     return x + y

def say_hello(request):
    # we can do anything we want such as pull data, transform data, send email etc
    # return HttpResponse("Hello World")

    # telling the view function to return this template created in the templates folder instead
    # return render(request,'hello.html')

    # using mappings in the render function
    # x = calculate()
    # return render(request,'hello.html', {'name':'Paul'})

    # demonstrating managers and query sets
    # query_set = Product.objects.all()
    # for product in query_set:
    #     print(product)

    try:# handling excpetions when retirieving objects . the code below if not in a try block
        # would raise an error because no objeect has the primary key of
        product = Product.objects.get(pk = 0)
    except ObjectDoesNotExist:
        pass

    exists = Product.objects.filter(pk=0).exists() # checks if an object exists and returns a boolean

    # in filtering query set obejcts the line below gives an error
    # query_set = Product.objects.filter(unit_price > 20)
    # in django the right way to write that line is using keyword arguents
    # after we type the field name we follow with 2 underscores and a lookup type e.g
    # query_set = Product.objects.filter(unit_price__gt=20)
    # other keywords are lt,lte,gte (greater than or equal to), range  etc

    query_set = Product.objects.filter(unit_price__range=(20,30)) # example using range
    # search google for queryset api and see field lookups

    # we can also filter across relationships
    # example finding all the products in collection 1
    # we filter and link on the collection class and supply a field of that class after two underscores..
    #..and after another two underscores we add a lookup such as less than(lt) of gt
    # query_set = Product.objects.filter(collection__id__range=(1,2,3))

    # filtering for strings. using e.g contains lookup for case-sensitive and icontains for case-insensitive
    query_set = Product.objects.filter(title__icontains="coffee")

    # example for checking for null
    query_set = Product.objects.filter(description__isnull=True)

    # exmaple for multiple filters. we can either write it like below
    query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # o written as below
    query_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)
    # to make the query to be an "or" rather than and for the two conditions above we use q objects import from Q
    # using the Q class we can encapsulate a keyword argument and use the or logical operator e.g
    query_set = Product.objects.filter(
        Q(inventory__lt=10) | Q(unit_price__lt=20))

    # if we need to reference a particular field when filtering data e.g
    # where inventory = unit price
    # if we do ...
    # query_set = Product.objects.filter( inventory=unit_price) # we get an error
    # ..since unit_price is not a valid value for inventory. even if we convert unit_price there to a string
    # we still get an error cus inventory field is a number and we cant compare number to a string
    # to solve this..we use the F class to reference the field we want
    query_set = Product.objects.filter(inventory=F('unit_price'))
    # we can even reference a field in a connected table  e.g comparing the inventory of a product with the id of its collection below
    query_set = Product.objects.filter(inventory=F('collection__id'))
    # this is done using F objects

    # querying only specific fields
    query_set = Product.objects.values('id', 'title', 'collection__title') # each record in the query set will be a dictionary
    # the collections__title reads the title field from the realted collections table
    # if we want tuples rather than dictionary we can use the values list method instead
    # query_set = Product.objects.values_list('id', 'title', 'collection__title')

    # example exercise to select items that have been ordered and sort them by their title
    # we need to first get all the product id from the products table
    # we need to find out which ones have been ordered i.e product id exists in the order items table
    # we then filter to get only those products and sort by title field
    # first import the order item table into the views script (done above)
    query_set = Product.objects.filter(
        id__in = OrderItem.objects.values('product_id').distinct()).order_by('title')

    # using the TaggedItem custom manager defined in the tags app for the tagged item class...
    #..to retrieve the taggs for a product with id 1
    TaggedItem.objects.get_tags_for(Product,1)

    # final return
    return render(request, 'hello.html', {'name': 'Paul','products': list(query_set)})



# function example on creating and updating and deleting objects
def say_hello2(request):
    collection = Collection()  # creating a collection object
    collection.title = 'Video Games' # setting the collection title
    # the featured product field below is optional in the collections table
    # we can demonstrate how to set it and create a relationship
    # one way is to set it to a product object
    collection.featured_product = Product(pk=1) # or just using the value of the primary key field directly below
    # collection.featured_product_id = 1
    # either way, the way must exist before creating the collection

    # rather than defining the fields individually as above...
    # another approach is to define them using key word arguments when defining the collection object
    # collection = Collection(title = 'Video Games')
    # the downside to this is the keyword arguments arent intellisense supported
    # in the previous way also, if the title field in the collections table was renamed to something else..
    #..the name update would also be effected here automatically
    # keyword arguments wont do this for us

    # to insert the newly created collection object into our database we call the save method
    collection.save()
    # because we havent set the id of the object, django will treat it as an insert operation

    # a shorthand way to create and save the new object using keywords is
    # collection = Collection.objects.create(name= "Video Games",featured_product_id=1)
    # this creates and saves the object automatically
    # the keywords would still have that problem about intellisense tho


    # to update an object, all we have to do is set the Primary key field or id field(id id is the PK)
    collection = Collection(pk = 11) # after checking database to see that pk for the video games collection we want to update is 11
    collection.title = 'Games' # changing the title from Video games to games
    collection.featured_product = None # setting to NONE rather than Product(pk=1)
    # in the sql code generated, the above fields would be updated

    # if we just update one field rather than all, e.g update just the featured  product field...
    # and not explicitly updating the title as in the lines above
    collection = Collection(pk = 11)
    collection.featured_product = None
    # this would set the title to an empty string
    # with django ORM we have to explicity define and update all the fields unless it would default to empty

    # the way around this is to first read in the object from the database
    collection = Collection.objects.get(pk = 11) # first getting the particular object from the database
    # we now have the collection object with all its values and can choose to update only certain fields
    collection.title = 'Games' # changing the title from Video games to games
    collection.featured_product = None
    # having to read the object before making updates and then saving back ..
    # may or may not neccesarily imppact performance
    # but if you see that it does..another way to go is using the update method below using keywords

    # Collection.objects.update(featured_product= None)
    # the update method avoids reading in the data first
    # it updates directly in the database
    # the update line above will update for all the objects in the collections table
    # that isnt what we want . to find a specific product we do below
    Collection.objects.filter(pk=11).update(featured_product=None)


    # for delting objects we also have two options
    # we can delete a single object or multiple objects in a queryset
    # for single object
    collection = Collection(pk=11)
    collection.delete() # deleting the object retrieved above
    # to delete multiple objects we first need to get a queryset
    collection.objects.filter(id__gt=5).delete() # deleting objects with id greater than 5 


def sayhello3(request): # to demonstrate transactions
    order = Order()
    order.customer_id = 1
    order.save()

    item = OrderItem()
    item.order = order
    item.product_id = 1
    item.quantity = 1
    item.unit_price  = 10
    item.save()

    # if the code is set up as above, if something breaks while saving the item,
    # our database will be left in an inconsistent state and we will be left with an order without an item
    # to prevent this we can wrap all the operations in a transaction so if one fails, all fails
    # we import the transaction module from django.db above
    # we wrap our view function in a transaction using the atomic function

@transaction.atomic()
# def sayhello3(request): # to demonstrate transactions
#     order = Order()
#     order.customer_id = 1
#     order.save()
#
#     item = OrderItem()
#     item.order = order
#     item.product_id = 1
#     item.quantity = 1
#     item.unit_price  = 10
#     item.save()

# if you want more controll over what bits of your code should be in a transaction
# ..we can use the atomic function as a context manager instead
def sayhello3(request):

    # code not to be inside transaction .....

    with transaction.atomic(): # using atomic as a context manager
        order = Order()
        order.customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price  = 10
        item.save()


def sayhell4(request): #demonstrating writing and excecuting our own raw sql queries
    queryset = Product.objects.raw('SELECT id,title FROM store_product')
    # the query above does return a queryset but this queryset is different from querysets return from queries using django ORM
    # this one doesnt have methods such as annotate, filter etc

    # sometimes we may also want to excute queries that dont map to our model object
    # in those cases we can access the databse directly and bypass the model layer
    # we use the cursor from the connection module imported above
    cursor = connection.cursor()
    # we can then pass in any sql statement into the cursor to excute
    cursor.execute()
    cursor.close() #closing the cursor afterwards
    # cursors should be wrpapped inside a try finally block  or in a with statement as below
    with connection.cursor() as cursor:
        cursor.execute()

        # we can also choose to execute stored procedures using the callproc
        # for example executing a stored procedure called get_customers
        cursor.callproc('get_customers',[1,2,'a'])

    return render(request, 'hello.html', {'name': 'Paul', 'products': list(queryset)})















