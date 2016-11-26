# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

##  Code reference: 
## http://web2py.com/books/default/chapter/29/07/forms-and-validators#SQLFORM-and-uploads
def download():
    return response.download(request, db) 

# Returns form for User to add a post
@auth.requires_login()
def add():
    """Add a post."""
    form = SQLFORM(db.bboard)
    if form.process().accepted:              # Confirms that post is added          
        # Successful processing.
        session.flash = T("inserted")
        redirect(URL('default', 'index'))
    return dict(form=form)

# Returns form viewing a post
def view():
    """View a post."""
    p = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.bboard, record=p, readonly=True, upload=URL('download'))
    # p.name would contain the name of the poster.
    return dict(form=form)

# Returns a form that allows the User to edit their post
@auth.requires_login()
@auth.requires_signature()
def edit():
    """View a post."""
    p = db.bboard(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:            # Checks id
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index')) 
    form = SQLFORM(db.bboard, record=p)
    if form.process().accepted:
        session.flash = T('Updated')         # Confirms that post is updated
        redirect(URL('default', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form)

# Returns a form that confirms whether the User does want to delete the post
@auth.requires_login()
@auth.requires_signature()
def delete():
    """Deletes a post."""
    # Deleted variable p, same as item
    item = db.bboard(request.args(0)) or redirect(URL('default', 'index')) 
    form = FORM.confirm('Yes, delete post') 
    if item.user_id != auth.user_id:         # Checks id
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index'))
    if form.accepted:
        db(db.bboard.id == item.id).delete() # Confirms permission to delete
        redirect(URL('default', 'index'))
    return dict(form=form)

# Main page
def index():
    """Better index."""
    # Let's get all data. 
    q = db.bboard
    
    # Retrieve parameter # Comparison to check if arg(0) = 'all'
    show_all = request.args(0) == 'all'

    # Query asks for sold status, default will show everything
    q = (db.bboard) if show_all else (db.bboard.sold == False)

    def generate_del_button(row):
        # If the record is ours, we can delete it.
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id], user_signature=True))
        return b
    
    def generate_edit_button(row):
        # If the record is ours, we can edit it.
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.id], user_signature=True))
        return b

    def shorten_post(row):
        return row.bbmessage[:10] + '...'

    # Toggles the sold/unsold listings 
    @auth.requires_signature()
    @auth.requires_login()
    def toggle_sold():
        item = db.bboard(request.vars(0)) or redirect(URL('default', 'index'))
        item.update_record(sold = not item.sold) 
        redirect(URL('default', 'index')) # Assuming this is where you want to go

    # Creates the button for sold/unsold
    if show_all:
        button = A('See unsold', _class='btn', _href=URL('default', 'index'))
    else:
        button = A('See all', _class='btn', _href=URL('default', 'index', args=['all']))   

    # Creates extra buttons.
    
    links = [
        dict(header='', body = generate_del_button),
        dict(header='', body = generate_edit_button),
        ]

    if len(request.args) == 0:
        # We are in the main index.
        links.append(dict(header='Post', body = shorten_post))
        db.bboard.bbmessage.readable = False
   
    # if show_all is set, first arg of URL should not be se to SQLFORM.grid
    start_idx = 1 if show_all else 0    
    form = SQLFORM.grid(q, args=request.args[:start_idx],
        fields=[db.bboard.user_id, db.bboard.date_posted, db.bboard.sold,
                db.bboard.category, db.bboard.title, db.bboard.price, 
                db.bboard.bbmessage],
        editable=False, deletable=False,
        links=links,
        paginate=50,
        )

    return dict(form=form, button=button) # Returns form and the toggle button

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
