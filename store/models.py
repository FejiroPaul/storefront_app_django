from django.db import models

# creating a promotions class which would have many to many relationship with products
# products can have different promotions and promotions can apply to different products
# we know that when we define a relationship in one class, django automatically creates the reverse relationship..
# .. in the other class concerned. we just need to decide where we want to define the relationship first
# in this case it makes sense to define this relationship between products and promotions in the product class
# so that along side every product, the promotion that applies to it is shown
# see promotions field defined in products class below, django then defines the reverse relation to link the promtions class

class Promotion(models.Model):
    description = models.CharField(max_length= 255)
    discount = models.FloatField()



# defining the collection class first so we can reference it in the product class later below
# we reference it as by passing Collections object as the first argunent in the foreign key field
# if we cant arrange it like this, i.e collection before the product class....
#...we can just pass collection as a string instead e.g collection = models.ForeignKey("Collection",on_delete=models.PROTECT)
class Collection(models.Model):
    title = models.CharField(max_length=255)

    # product_set
    # we would have the field above when django creates the reverse relationship to complete the many to many
    # ....relationship defined in the products class
    # if using the related_name argument in defining the relationship in the products class...
    #..it sets the name of the field above to the value of the related_name

    featured_product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True,
                                         related_name='+')
    # we also have a field called featured_product which is a dependency on the product class
    # if you look at the product class we also have a field called collections which initiates...
    # ..a dependency of the products class on the collections class also
    # this is thus a circular dependency
    # if you remove the quotes from "Product" above, you see an unresolved reference error
    # because product class has not been defined before collections class and hence quotes needed
    # if we ever rename the products class we would need to rename that string also

    # another issue is that as we know, django automatically creates a reverse relationship..
    #..  in the products class to complete the relation we defined when we create the feautured_product field
    # that is we would have a field named collections in the product class
    # but we already have defined a field named collections in the products class below
    # django therefore cant create the reverse relationship because of the name clash
    # the solution is to use the related_name argument in the featured_name field above
    # we can set the name of the reverse relationship django creates to something we want...
    #.. or just use a "+" in there if we dont care about the reverse relationship
    # the "+" tells django not to create that reverse relationship


class Product(models.Model):

    # django creates id field automatically so we dont need create a field and make it ID
    # every entity or model class will have an id field that will serve as the primary key
    # but if we don't want that id field we can define our primary key as below
    # django will then no longer create the id field and use it as primary key
    # sku = models.CharField(max_length=10, primary_key=True)

    # you can google to see possible field types
    # every field type has a bunch of options, some generic or particular to that type
    # we want our title to be of the charfield type
    title = models.CharField(max_length=255)
    slug = models.SlugField() # we can either define slugfield like this line and select the default value
    # ...when django prompts us to while making the migration .
    # this would mmean that the default slug value will be defined in our migrations file only
    # the alternative is the line below where we can either set a default value or set null to true
    # slug = models.SlugField(default='-')
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection,on_delete=models.PROTECT)
    # used models.protect above so if we delete a collection we dont delete all products in the collection

    # in the collections field above we have a dependency on the collections class

    promotions = models.ManyToManyField(Promotion)
    # we also supply a keyword argument called related name to set the name of the field django creates..
    #... in the promotions class to complete the relationship e.g
    # promotions = models.ManyToManyField(Promotion, related_name="products")

class Customer(models.Model):
    # sometimes we may also need to limit the number of values that can be stored in  field
    # this is done using the choice option which is available to all field types
    # choices are supplied via an array of tuples containing two values each
    # the first value being the value stored in the database
    # the second being a human readable name
    # the human readable name is used in the admin interface in a dropdown list

    # setting these variables so if we wanted to change values of
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [ # using uppercase to indicate that it is fixed and shouldnt be changed
        (MEMBERSHIP_BRONZE,"Bronze"),
        (MEMBERSHIP_SILVER,"Silver"),
        (MEMBERSHIP_GOLD, "Gold")
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True) # using date field rather than datetime cus we dont need time here
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default= MEMBERSHIP_BRONZE)

    # class Meta:  # google options that can be defined in this subclass
    #     db_table = 'store_customer' # setting the table name
    #     indexes = [ # creating indexes
    #         models.Index(fields=["last_name","first_name"])
    #     ]

class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"

    PAYMENT_STATUS_CHOICE = [
        (PAYMENT_STATUS_PENDING,"Pending"),
        (PAYMENT_STATUS_COMPLETE,"Complete"),
        (PAYMENT_STATUS_FAILED,"Failed")
    ]
    # auto_now_add in the field below means that the first time we place an order and thus an order object is created
    # ......, djnago automatically populates this field
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1,choices=PAYMENT_STATUS_CHOICE,default=PAYMENT_STATUS_PENDING
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    # using protect above so we dont delete orders is a customer is deleted

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.PROTECT)
    product= models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    # unit_price is stored here in order item also, because since the price of the product can always change..
    #.. it is good to store the price of the item at the time ordered

# we can also implement one to one relationships between two models
# each address should belong to one and only one! customer
class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    # since an address must belong to a customer, the customer must exist before an address can
    # we need to specify the parent entity which is the customer

    # customer = models.OneToOneField(Customer, on_delete=models.CASCADE,primary_key=True) # the first argument is the type of the parent field model

    # the second argument sprecifies what should happen when we delete that parent entity i.e customer
    # we can set the second argument e.g models.CASCADE to delete the associated address when a customer is deleted..
    #.. or even models.SET_NULL if the field accepts null values, then the field will set to null is customer is deleted
    # models.SET_DEFAULT sets it to a default value
    # models.protect prevents the deletion of the parent and hence we cant delete the parent customer unless ..
    #... we delete the child address

    # we also set the primary key to true so django doesn't create the id field and....
    # every address then would have an id field and hence a one to many relationship between customers and addresses
    #...since that would mean many customers could have same address
    # making that field the primary key we can only have one address for each customer because primary keys dont allow duplicatr values

    # we don't also need to define and address field in the customer model to complete the relationship
    # django automatically does this for us

    # if we want a customer to have a one to many relationship rather, i.e a customer can have many addresses
    # we first make the field a foreign key
    # we want to allow duplicate values in the customer column so we remove the primary key argument
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)# cascade meaning, delete all items if a cart is deleted
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    # cascade above meaning if you can delete a product i.e product has also never been ordered before..
    # ...then that product should be removed from all the existing shopping carts as well
    quantity = models.PositiveSmallIntegerField()





























