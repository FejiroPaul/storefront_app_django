from django_filters.rest_framework import FilterSet
from .models import Product
class ProductFilter(FilterSet):
    class Meta:
        model = Product
        # instead of an array we use a dictionary for fields below
        # because for each field we can specify how the filtering should be done
        fields = {
            'collection_id':['exact'],
            'unit_price':['gt','lt']
        }
