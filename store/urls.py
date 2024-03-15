from django.urls import path
from . import views

# URLConf
urlpatterns = [
    # path('products/', views.product_list),
    # moving the view function below from the function based view above to the class based view below
    # the class based view has a method as_view() which converts the class to a normal function based view
    path('products/', views.ProductList.as_view()),
    path('products/<int:pk>/', views.ProductDetail.as_view()),
    path('collections/', views.CollectionList.as_view()),
    path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail'),
]
