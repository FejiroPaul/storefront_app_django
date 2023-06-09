# Generated by Django 4.2 on 2023-05-01 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_add_slug_to_product'),
    ]

    # running python manage.py makemigrations store --empty created this initially empty migration file
    # the operations array was therefore empty

    operations = [ # to define custom sql for our database schema
        # the first sql argument in creating an instance of the migrate.sql class below is..
        # ..for upgrading our database and the second argument is for downgrading it
        # the second argument although optional, is needed unless we wont be able to revert the migration
        migrations.RunSQL("""
            INSERT INTO store_collection (title)
            VALUES ('collection1')
        """, """
        DELETE FROM store_collection 
        WHERE title='collection1'
        """ )
    ] # using the technique above, we could do other stuff like create functions, views, stored procedures etc
