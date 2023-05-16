from django.db import models
from django.contrib.auth.models import User
# auth is an app that is also automatically installed in every django project
# using this app we can authenticate and authorise users

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class LikedItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    # user field above is a foreign key to the user defined in django.contrib.auth.models
    # cascade so if a user a deleted, all object sthat user has liked is deleted as well

    # content type below identifies the type of object that the user likes
    # object_id references that particular object and
    # content_type reads the actual object
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()






