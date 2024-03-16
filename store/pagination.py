from rest_framework.pagination import PageNumberPagination

# define custom pagination class
class DefaultPagination(PageNumberPagination):
    # we set the page size here rather than in the settings module
    page_size = 10