from django.urls import path
from . import views # importing views from the current folder so we can reference our view functions

# define the special variable which django looks for
# it is a Url configuration .... URLConf
urlpatterns = [
    # use the path function to create a url path object
    path("hello/", views.say_hello) # notice that the function say_hello is just referenced not called

]
# the url configuration above needs to be impprted into the main url configuration for our django project
# this is in the storefront directory and also called urls