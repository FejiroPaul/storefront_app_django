from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail),
    path('collections/',views.collection_list),
    # we give th path mapping below a name. this is because we use this name in the hyperlink related field in our ..
    #... Product serialiser. the name is the one used there as view name
    # we also need to use the pk keyword rather than id because for this hyperlink case, it is what django expects
    # it will read the value of pk and use that to lookup a collection
    path('collections/<int:pk>/',views.collection_detail, name='collection-detail')
]
