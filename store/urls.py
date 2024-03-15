from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from . import views

# when we use model viewsets we dont explicity define the urls for our view functions
# we use routers for that
# the routers take crae if generating the url patterns for us
# we import the router class above and create a router object and register our viewsets with the router
router = SimpleRouter()
router = DefaultRouter() # if we use this router we get two additions into our browsable api
# we get endpoint generated inn our responses
# we can see our data in json format if we add .json to our endpoints

router.register('products',views.ProductViewSet)
# first argument above is the url prefix i.e the name of our endpoint
# second argument is our viewset
# i.e products endpoint should be managed by the products viewset
router.register('collections',views.CollectionViewSet)
# we can  then get all the url patterns as below

# since we dont have any explicit patterns in our url patterns  we can just do below
urlpatterns  = router.urls

# if we had some specific patterns in our url patterns array
# we then dont  want to just set to routers.url so we do below
# urlpatterns = [
#     path('', include(router.urls),
#     # path('products/', views.ProductList.as_view()),
#     # path('products/<int:pk>/', views.ProductDetail.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail'),
# ]
