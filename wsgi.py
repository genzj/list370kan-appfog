#!/usr/bin/env python2
#coding:utf-8

import web
import web.template
import socket
from web import form
from list370kan import PlaylistReaper
from search370kan import Search370Kan
import os
import mimetypes

# win32 pton workaround
if 'inet_pton' not in dir(socket):
    # Win32 platform doesn't support this
    def dummyf(*args, **kwargs):
        pass
    socket.inet_pton = dummyf

urls = ('/', 'index',
        '/(static/.*)','staticHandler',
        '/search', 'search',
        '/find', 'find',
        '/favicon.ico', 'favicon')

render = web.template.render('templates/')

myform = form.Form(
            form.Textbox("key", description="Name of Movie")
         )

class staticHandler:
    def _request(self,name):
        '''
        i used mimetypes to guess the file's type and set the HTTP header's Content-Type
        if file not exits return 404 error
        the urls must config like this
        urls = (
        '/(static/.*)','staticHandler'
        )
        '''
        basedir = os.path.abspath(os.path.dirname(__file__))
        fn = os.path.join(basedir, name)
        if not os.path.isfile(fn):
            return web.notfound()
        try:
            try:
                mtype = mimetypes.guess_type(fn)[0]
                if mtype == None: mtype = 'application/octet-stream'
                web.header('Content-Type', mtype, unique=True)
                f = open(fn,'rb')
                return f.read()
            finally:
                f.close()
        except:
            return web.notfound()

    def GET(self,name):
        return self._request(name)

    def POST(self,name):
        return self._request(name)

class favicon:
    def GET(self):
        raise web.redirect('static/favicon.ico')

class index:
    def GET(self):
        form = myform()
        return render.index(form)

class search:
    def GET(self):
        url1 = web.input(q="").q
        if not url1:
            raise web.seeother('/')
        title, pl = PlaylistReaper().fromindex(url1)
        return render.playlist(title, pl)

class find:
    def GET(self):
        key = web.input(key="").key
        if not key:
            raise web.seeother('/')
        movies = Search370Kan().search(key)
        return render.find(key, movies)

web.config.debug = True
application = web.application(urls, globals()).wsgifunc()
