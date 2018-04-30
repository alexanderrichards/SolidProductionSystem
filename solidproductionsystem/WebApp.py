import os
import re
import cherrypy
from productionsystem.webapp.WebApp import WebApp

@cherrypy.expose
class CVMFSDirectoryListing(object):

    def _cp_dispatch(self, vpath):
        cherrypy.request.params['path'] = os.path.join(*vpath)
        while vpath:
            vpath.pop()
        return self

    @cherrypy.tools.accept(media='application/json')
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, path):
        data = cherrypy.request.json
        print "in GET:", path, data
        with cherrypy.HTTPError.handle(KeyError, 400, "No type key"):
            list_type = data['type']
        with cherrypy.HTTPError.handle(KeyError, 400, "No regex key"):
            regex = data['regex']
        with cherrypy.HTTPError.handle(Exception, 400, "Bad RegEx"):
            regex = re.compile(regex)
        list_type = list_type.lower()

        target = os.path.join('/cvmfs', path)
        try:
            _, dirs, files = os.walk(target).next()
        except StopIteration:
            raise cherrypy.HTTPError(400, "Couldn't access '%s'" % target)

        output = []
        if list_type == 'dirs' or list_type == 'all':
            for dir_ in dirs:
                match = regex.match(dir_)
                if match is not None:
                    output.append(match.group(len(match.groups())))
        if list_type == 'files' or list_type == 'all':
            for file_ in files:
                match = regex.match(file_)
                if match is not None:
                    output.append(match.group())
        return output


class SolidWebApp(WebApp):
    def _mount_points(self):
        super(SolidWebApp, self)._mount_points()
        cherrypy.tree.mount(CVMFSDirectoryListing(),#'/cvmfs/solidexperiment.egi.eu/el6',
                            '/cvmfs',
                            {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})
