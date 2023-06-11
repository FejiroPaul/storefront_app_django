# this app we combine features from the two plugable apps , store and tags
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
# Register your models here.

# we can go about defining the features to be combined


class TagInline(GenericTabularInline):# generic inline to be used in the Product admin
    autocomplete_fields = ['tag']
    model = TaggedItem

# we then need to create a new product admin that inherits from the product admin imported into this module
# in this new implementation we will reference the tag inline class created above
class CustomProductAdmin(ProductAdmin): # creating new product admin
    inlines = [TagInline]
# we then tell django to unregister the old product admin and register the new one above
admin.site.unregister(Product)
admin.site.register(Product,CustomProductAdmin) # registering Product model with the new custom admin