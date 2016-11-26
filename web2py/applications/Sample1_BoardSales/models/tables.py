# -*- coding: utf-8 -*-
from datetime import datetime


def get_first_name():
    name = 'Nobody'
    if auth.user:
        name = auth.user.first_name
    return name

# Sets
CATEGORY = ['Misc.', 'Bike', 'Books', 'Car', 'For the house', 'Music', 'Outdoors']
ITEM_STATUS = ['For Sale', 'Sold']

## Code reference: 
## http://www.web2py.com/books/default/chapter/29/06/the-database-abstraction-layer

db.define_table('bboard',
                Field('name'),
                Field('user_id', db.auth_user),
                Field('phone'),
                Field('email'),
                Field('category'),
                Field('date_posted', 'datetime'),
                Field('title'),
                Field('sold', 'boolean', default=False), 
                Field('price'),
                Field('image','upload'), 
                Field('bbmessage', 'text'),
                )

## Code reference: 
## http://web2py.com/books/default/chapter/29/07/forms-and-validators#SQLFORM-and-uploads

# References to other tags
db.bboard.name.default = get_first_name()
db.bboard.user_id.default = auth.user_id
db.bboard.category.default = 'Misc'
db.bboard.date_posted.default = datetime.utcnow()
db.bboard.price.label = 'Price ($)'
db.bboard.bbmessage.label = 'Message'

# Conditionals for text areas 
db.bboard.phone.requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
         error_message='Not a phone number, i.e. valid number: (xxx)xxx-xxxx')
db.bboard.email.requires = IS_EMAIL()
db.bboard.category.requires = IS_IN_SET(CATEGORY, 
          error_message='Please select a category', zero=None)
db.bboard.price.requires = IS_FLOAT_IN_RANGE(0, 100000.0, 
          error_message='The price should be in the range 0..100000')

# Boolean areas - Readable/Writable
db.bboard.name.writable = False
db.bboard.id.readable = False
db.bboard.user_id.writable = db.bboard.user_id.readable = False
db.bboard.category.required = True
db.bboard.date_posted.writable = False



