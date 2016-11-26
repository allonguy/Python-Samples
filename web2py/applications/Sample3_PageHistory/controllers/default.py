# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import logging
from datetime import datetime

def index():
    # Page titles
    title = request.args(0) or 'Main Page'
    display_title = title.title()
     
    # Page content
    form = None
    content = ''
    b_edit = ''

    # Page checking, and revision items
    indb = False if title is not IS_NOT_IN_DB(db, 'pagetable.title') else True
    editing = request.vars.edit == 'true'
    hist = request.vars.history == 'true'
    revisions = None
 
    # Variables initialized for new page prompt
    new = False
    error = '' 
    
    home = True if request.args(0) is None else False 
 
    # Request for edit
    logger.info("This is a request for page %r, with editing %r" %
                 (display_title, editing))
     
    # You have to serve to the user the most recent revision of the 
    # page with title equal to title.
    p_id = db(db.pagetable.title == title).select().first()  
    rev = db(db.revision.page_id == p_id).select(orderby=~db.revision.date_created).first()
    s = rev.body if rev is not None else ''
     
    # Condition to check for is title is in database
    # Title is not in database -> create a new page
    if (indb is False) and (request.args(0) is not None) and (p_id is None):
       rev = None # New page means no revisions yet
       new = True # Flag for new page
       error = 'Page - %s - does not exist!' % title 
       s = "Would you like to make a new page?" 
       b_edit = A('Create New Page', _class = 'btn', _href = URL('default', 'index', args = [title],
                                              vars = dict(edit = 'true')))
       
    # Title is in database -> present page with edit option
    if (indb is True)  and (request.args(0) is not None):
       b_edit = A('Edit', _class = 'btn', _href = URL('default', 'index', args = [title],
                                                         vars = dict(edit = 'true')))
    # if history is clicked true 
    if hist:
       revisions = db(db.revision.page_id == p_id).select(orderby=~db.revision.date_created)

    # When editing -> During Create or Edit
    if editing:
       # Empty content for new page
       if new is True:
          s = ''
       # Form
       form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     default=s
                                     ))
       # Cancel button -> Returns to Index
       form.add_button('Cancel', URL('default', 'index', args = [display_title]))
       # Submit button clicked
       if form.process().accepted:
          # Write new content if new page
          if rev is None:
             p_id = db.pagetable.insert(title=title).id
             # First time: we need to insert it.
             db.revision.insert(author=auth.user_id,page_id=p_id, body=form.vars.body, 
                                date_created=datetime.utcnow())
          else:
             db.revision.insert(author=auth.user_id,page_id=p_id, body=form.vars.body, 
                                date_created=datetime.utcnow())
          # Return back to the made/edited page 
          redirect(URL('default','index',args=[title]))
       content = form
    else:
       content = s   

    # Show all pages made
    layout = db().select(db.pagetable.ALL)
    
    return dict(display_title=display_title, content=content, editing=editing, b_edit=b_edit, error=error,
                  new=new, title=title, home=home, layout=layout, revisions=revisions, hist=hist)

@auth.requires_login()
# Form for creating a page
def create():
    title = ''
    form = SQLFORM.factory(Field('title', 'text',
                                  label='Title of Page',
                                  default=''
                                  ))
    # Cancel button -> Returns to Index
    form.add_button('Cancel', URL('default', 'index'))
    # Submit button clicked
    if form.process().accepted:
        title = form.vars.title
        redirect(URL('default','index',args=[title],vars=dict(edit='true')))
    return dict(form=form)   

# Viewing all revisions       
def view():
    """View a an old page."""
    p = db.revision(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.revision, record=p, readonly=True)
    title = request.vars.t
    return dict(form=form, title=title)
    
# Reverts back to a prior stage in revision    
def revert():
    # Gets the previous date
    askdate = request.vars.revdate 
    titlepage = request.args(0)
    """Revert back to an old page"""
    # Form for user's added comment for revision
    form = SQLFORM.factory(Field('revision_comment', 'text',
                                  label='Revision Comment',
                                  default= ''
                                  ))
    # Cancel button -> Returns to Index
    form.add_button('Cancel', URL('default', 'index', args = [titlepage],vars=dict(history='true')))
    # Submit button clicked
    if form.process().accepted:
        # Update if everything associated with the page id
        page = db.pagetable(title=titlepage)
        db.revision.insert(page_id=page.id, body=request.vars.revbody,
                            revision_comment=form.vars.revision_comment)
        redirect(URL('default','index',args=[titlepage]))
    return dict(form=form, titlepage=titlepage, askdate=askdate)
    

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
