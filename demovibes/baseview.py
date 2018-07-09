import logging
import copy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.core.cache import cache
import hashlib

class BaseView(object):
    __name__ = "BaseView"

    methods = ("GET", "POST")

    template = "notemplate.html"
    basetemplate = ""

    login_required = False
    staff_required = False
    permissions = []

    forms_valid = True
    forms = []

    cache_key = None
    cache_duration = 60*5
    cache_output = False
    cache_hash_key = True

    use_decorators = []
    run_before_main = ["initialize", "run_permissions_check", "setup_session", "handle_forms", "pre_view"]
    run_after_main = ["post_view", "update_context", "close_session", "check_caching", "render"]

    content_type = settings.DEFAULT_CONTENT_TYPE

    response = None
    _is_instance = False

    def __call__(self, request, *args, **kwargs):
        if not self._is_instance:
            newcopy = copy.copy(self)
            newcopy._is_instance=True
            if self.login_required or self.permissions or self.staff_required:
                newcopy = login_required(newcopy)
            for decorator in self.use_decorators:
                newcopy = decorator(newcopy)
            return newcopy(request, *args, **kwargs)

        self.context = {}
        self.formdata = {}

        if hasattr(self, "configure"):
            self.configure()

        self.args = args
        self.kwargs = kwargs

        self.log = logging.getLogger("BaseView")

        self.method = method = request.method

        self.log.debug(u"Request method is : %s" % self.method)

        if not method in self.methods:
            return self.method_not_allowed()

        self.request = request

        return self.run_requests(*args, **kwargs)

    def run_functions_from_list(self, funclist):
        """
        Take a list of functions, and run them in order if defined.
        """
        for f in funclist:
            self.log.debug("Checking for %s" % f)
            if hasattr(self, f):
                self.log.debug("Running %s" % f)
                r = getattr(self, f)()
                if r:
                    return r

    def run_requests(self, *args, **kwargs):
        """
        Run the request gauntlet
        """
        funclist = self.run_before_main + [self.method] + self.run_after_main
        return self.run_functions_from_list(funclist)

    # ---- Permission check block ----

    def run_permissions_check(self):
        """
        Check if user have permission to view, if not return denied
        """
        if not self.default_permissions_check():
            return self.deny_permission()

    def default_permissions_check(self):
        if self.staff_required and not self.request.user.is_staff:
            return False
        for perm in self.permissions:
            if not self.request.user.has_perm(perm):
                return False
        return self.check_permissions()

    def check_permissions(self):
        return True

    def deny_permission(self):
        response = HttpResponse("Permission denied")
        response.status_code = 403
        return response

    # ---- End permission check block

    def setup_session(self):
        self.session = self.request.session

    def close_session(self):
        self.request.session = self.session

    def update_context(self):
        self.context.update(self.set_context())

    def set_context(self):
        return {}

    def handle_forms(self):
        """
        Create and initialize forms defined in self.forms
        """
        for (form, formname) in self.forms:

            formfunc = "form_%s_init" % formname
            if hasattr(self, formfunc):
                self.log.debug(u"Calling INIT for form %s" % formname)
                kwargs = getattr(self, formfunc)()
            else:
                kwargs = {}

            if self.method == "POST":
                form_instance = form(self.request.POST, self.request.FILES, **kwargs)
                if not form_instance.is_valid():
                    self.forms_valid = False
                else:
                    self.formdata[formname] = form_instance.cleaned_data
            else:
                form_instance = form(**kwargs)

            formfunc = "form_%s_edit" % formname
            if hasattr(self, formfunc):
                self.log.debug(u"Calling EDIT for form %s" % formname)
                kwargs = getattr(self, formfunc)(form_instance)

            self.context[formname] = form_instance

    def redirect(self, target, get=""):
        self.log.debug(u"Setting redirect to target %s" % target)
        self.response = redirect(target)
        return self.response

    def render(self):
        if self.response:
            self.log.debug("Returning predefined response")
            return self.response
        self.log.debug("Returning default template")
        return self.render_template(self.basetemplate + self.template, self.context, self.request)

    def render_template(self, template, context, request):
        return render_to_response(template, context, context_instance=RequestContext(request), mimetype=self.content_type)

    def method_not_allowed(self):
        self.log.info("Method is not allowed")
        response = HttpResponse('Method not allowed: %s' % self.method)
        response.status_code = 405
        return response

    # ---- Caching block ----

    def check_caching(self):
        key = self.get_cache_key()
        if not key:
            return False
        if self.cache_hash_key:
            key = hashlib.md5(key).hexdigest()
        if not self.cache_output:
            self.log.debug("Updating cached context")
            self.update_cached_context(key)
        else:
            self.log.debug("Returning cached output")
            return self.render_cached(key)

    def render_cached(self, key):
        return self.fetch_cache(key, self.render)

    def fetch_cache(self, key, function):
        data = cache.get(key)
        if data == None:
            self.log.debug("Generating new output cache")
            time = self.get_cache_duration()
            data = function()
            cache.set(key, data, time)
        return data

    def update_cached_context(self, key):
        if key and hasattr(self, "set_cached_context"):
            context = self.fetch_cache(key, self.set_cached_context)
            self.context.update(context)

    def get_cache_key(self):
        return self.cache_key

    def get_cache_duration(self):
        return self.cache_duration

    # ---- End caching block ----
