from django.db import models
# from store.models import Product
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

# defining a custom manager class
class TaggedItemManager(models.Manager):
    def get_tags_for(self, obj_type,obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)
        queryset = TaggedItem.objects.\
            select_related('tag').\
            filter(
                content_type=content_type,
                object_id=obj_id
            )
        return queryset




# the tags app is to be designed so we can reuse it in any project
# we want the ability to tag items anywhere
# the Tag model represents an actual tag
# Taggeditem represents a tag applied to a particular item which can be anything

class Tag(models.Model):
    label = models.CharField(max_length=255)


class TaggedItem(models.Model): # class for what tag applies to what object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    # the interesting thing is how do we identify the object that the tag above is applied to
    # the poor way of doing this is done in line below

    # product = models.ForeignKey(Product)

    # if doing the line above we would need to import the product model from the store app
    # so that we can reference the product app and the taggeditem model becomes dependent on it
    # we dont want to do this
    # not efficient especially if we need to import more models from other apps

    # what we need is a generic way to identify an object. to do this we need two things
    # Type(e.g product, video, article)   and  ID
    # with these we can identify any objects in our applications
    # for Type, we do this using django's abstract model called contenttype
    # this contenttype app is in our lists of installled apps in setting.py
    # using contenttype class from that app we can create generic relationships between our models
    # we import the class at top of the script
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)# cascade to remove all asscoiated types if a content type is removed

    object_id = models.PositiveIntegerField()
    # we make this field a positive integer field because we assume that all tables will have primary keys...
    #.. and all primary keys are positive integers
    # if in a particular table the primary key is not an integer, this solution wont work, thats its limitation

    # to then get the actual object the tag is applied to
    content_object = GenericForeignKey()
    # using the content_object field above, we can then read the actual object that a tag is applied to

    # creating an objects field which is an instance of the TaggedItemManager class defined above
    objects = TaggedItemManager()














