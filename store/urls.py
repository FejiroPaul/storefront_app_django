from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views

# when we use model viewsets we dont explicity define the urls for our view functions
# we use routers for that
# the routers take crae if generating the url patterns for us
# we import the router class above and create a router object and register our viewsets with the router
# router = SimpleRouter()

# router = DefaultRouter() # if we use this router we get two additions into our browsable api

# we get endpoint generated inn our responses
# we can see our data in json format if we add .json to our endpoints

# router.register('products',views.ProductViewSet)
# first argument above is the url prefix i.e the name of our endpoint
# second argument is our viewset
# i.e products endpoint should be managed by the products viewset
# router.register('collections',views.CollectionViewSet)


# urlpatterns  = router.urls

# in the github repo drf-nested router we can find info on using the nested routers library
# how to install it and all
# our reviews are nested resources hence the need for nested routers
# the nested router module comes with its own router classes such as its own DefaultRouter that..
#..replaces DefaultROuter in the usual rest framework library

# using the default router that comes with nested router libraryr
# create the parent routers
router = routers.DefaultRouter()
# register resources
# we explicitly state the basename for products endpoint because we override the get queryset logic for the products viewset
#..in our views module. by that basename, as usual we will have url patterns called products-list and producst-detail
router.register('products',views.ProductViewSet, basename='products')
router.register('collections',views.CollectionViewSet)
# create the child routers
# first argument is parent router, second arg is parent prefix, last arg is our lookup parameter
# the lookup being set to product means we will have a parameter called product_pk in our router
products_router = routers.NestedDefaultRouter(router,'products',lookup='product')
# on the child router we register our child resource and view set
# basename arg is used as a prefix in generating the name of the url pattern
# setting basename as product-reviews means our routes are going to be set as product-reviews-list or product-reviews-detail
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# now that we have two router, parent and child
# we can combine the urls of both the patterns and include them in the url patterns object
urlpatterns = router.urls + products_router.urls
# we can alternitively do below if we have explicit additional routes we want to define
# urlpatterns = [
#     path('',include(router.urls)),
#     path('',include(products_router.urls))
# ]