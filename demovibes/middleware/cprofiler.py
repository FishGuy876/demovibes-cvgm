import sys
import cProfile
from cStringIO import StringIO
from django.conf import settings
import datetime
import os

# If fancyprofile is also in url, it assumes a few things:
#
# 1. gprof2dot is downloaded, executable and its path is set - http://code.google.com/p/jrfonseca/wiki/Gprof2Dot
# 2. graphwiz / dot is installed
# 3. pngnq is installed
# 4. output_dir exist and is world writable
#
# Note: creating the graph is SLOW! Expect up to half a minute for result
#

class ProfilerMiddleware(object):
    
    #Variables needed for fancyprofile
    gprof2dot_path="/home/terra/gprof2dot.py"
    output_dir = "/home/terra/demovibes/static/debug"
    #| pngnq >
    command = "%(gprof2dot)s -f pstats /tmp/%(filename)s | dot -Tpng -o %(outdir)s/%(filename)s.png ; pngnq -f %(outdir)s/%(filename)s.png"
    url = "/static/debug/%(filename)s.png"
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'profile' in request.GET or 'fancyprofile' in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and 'profile' in request.GET or 'fancyprofile' in request.GET:
            self.profiler.create_stats()
            out = StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            filename = "django-profile.%s.%s.log" % (request.path.replace('/', '_'), datetime.datetime.now().strftime("%d_%b_%H:%m:%S"))
            self.profiler.dump_stats("/tmp/%s" % filename)
            self.profiler.print_stats(1)
            sys.stdout = old_stdout
            link=""
            if 'fancyprofile' in request.GET:
                vars = {'gprof2dot' : self.gprof2dot_path, 'outdir':self.output_dir, 'filename':filename }
                os.system( self.command % vars)
                url = self.url % vars
                link = "<a href='%s' target='_new'>Image link</a><br />" % url
            response.content = '%s<pre>%s</pre>' % (link, out.getvalue())
        return response
