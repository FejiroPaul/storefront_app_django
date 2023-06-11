from django.contrib import admin,messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
# from tags.models import TaggedItem
from . import models # so we can register our models to the admin site
# Register your models here.


# implementing custom filter for the products list
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory' # the title of the filter shown in our page
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        # return super().lookups(request,model_admin) # default implementation
        # we instead return a list a tuples where each tuple reps a possible value to be used in the filter
        # the first value is the actual value we use for filtering
        # the second value is a human readable description, which would appear under the filter title
        return [
            ('<10','low')
        ]
    def queryset(self, request, queryset): # here we then implement the filtering logic
        # return super().queryset(request,queryset) # default implementation
        if self.value() == '<10':
           return queryset.filter(inventory__lt = 10) # calling the filter on the queryset


# class TagInline(GenericTabularInline): # generic inline to be used in the Product admin
#     autocomplete_fields = ['tag']
#     model = TaggedItem
# this class is moved to the store_custom app admin module
# this is so we dont need the "from tags.models import TaggedItem" statement in this module anymore
# thus the store app wont be dependent on the tags app
# and it is thus a standalone app that can be used in other projects
@admin.register(models.Product) # telling django that this is the admin model for the Product class
class ProductAdmin(admin.ModelAdmin): # class to customise the admin interface for the product model
    list_display = ['title','unit_price','inventory_status','collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection','last_update', InventoryFilter]
    actions = ['clear_inventory']
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['collection']
    search_fields = ['collection_title']
    # inlines = [TagInline] # implemented by the store_custom app to enable standalone capability for the store app

    def collection_title(selfself,product):# passing in product cus it's a bunch of product objects we are rendering
        # this way is inefficient as a separate query will be run for every product object
        # Setting the list_select_related above to preload the related collections objects prevents us from.....
        # ...having to run a query for every product object in our function.
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory <10:
            return "Low"
        return 'Ok'

    # creating a function for custom action in list page
    @admin.action(description="Clear Inventory")
    def clear_inventory(self,request,queryset):
        # request reps current http request and queryset contains the objects the user selected in the list page
        # in this method we can do anything we want for updating objects
        updated_count = queryset.update(inventory=0) # this will immediately update the database and return a number of objects
        self.message_user(
            request,
            f'{updated_count} products were succesfully updated',
            messages.SUCCESS
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership','orders']
    list_editable = ['membership']
    ordering = ['first_name','last_name']
    list_per_page = 10
    # search_fields = ['first_name', 'last_name'] # this will bring any customer that has the searched word anywhere in their name
    search_fields = ['first_name__istartswith', 'last_name__istartswith'] # this makes sure we only get results...
    #...where the names start with the searched keyword

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )

class OrderItemInline(admin.TabularInline): # cerating inline interface to be used in the Order admin form
    # if we set our class to inherit from stackedInline rather than TabularInline
    # each order item to be added in the form will have its separate form
    # using tabular they all appear in a table format
    model = models.OrderItem
    autocomplete_fields = ['product']
    min_num = 1 # min number of order items that can be added
    max_num = 10 # max number of order items that can be added
    # extra = 0 # setting the number of empty value holders you see in the inline menu to add order items
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','placed_at','customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline] # including inlines for the admin form

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')# so we tell django what field to use to sort this computed column
    def products_count(self,collection):

        # return collection.products_count
        # in the line above, our collections objects dont have an attribute called products_count
        # we therefore need to override the queryset on this admin page and annotate our collections objects ..
        #... with the number of their products as products_count
        # to do this, every model admin has a method called get_queryset which we can override
        # see get_queryset override in the get_queryset function below

        # if we dont want to return just the product_count but a hyperlink so that..
        # when we click on the products_count values we can see the products in the collection that make up the count
        # reverse('admin:app_model_page') # this is the format to retrive the url of a django page you want, using the reverse function imported above
        url = (
            reverse('admin:store_product_changelist') # since we want to send the user to the product list page
            # without the lines below which implement a filter, we would just return all the items in the products list page
            # instead of the just the one in the product count we clicked on
            + '?' # this question mark indicates the beginning of a query string
            + urlencode(# this is where we generate the query string paramters, we use the urlencode utility fucntion imported above
                { # we give it a dictionary which can contain multiple key value pairs
                    'collection__id':str(collection.id) # getting ids of collection objects

            })

        )
        return format_html('<a href= "{}">{}</a>', url, collection.products_count)
    def get_queryset(self, request):
        # return super().get_queryset(request) # this is the default implementation
        # rather than return the queryset above we first annotate it
        return super().get_queryset(request).annotate(
            products_count = Count('product') # import the count function at beginning of module
        ) # now our collections objects in our queryset will have a field called products_count





