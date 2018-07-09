# -*- coding: utf-8 -*-
"""
    djangojinja2
    ~~~~~~~~~~~~

    Adds support for Jinja2 to Django.

    Configuration variables:

    ======================= =============================================
    Key                     Description
    ======================= =============================================
    `JINJA2_TEMPLATE_DIRS`  List of template folders
    `JINJA2_EXTENSIONS`     List of Jinja2 extensions to use
    `JINJA2_CACHE_SIZE`     The size of the Jinja2 template cache.
    ======================= =============================================

    :copyright: (c) 2009 by the Jinja Team.
    :license: BSD.
"""
from itertools import chain
from django.conf import settings
from django.http import HttpResponse
import jinja2
from django.template.context import get_standard_processors
from django.template import TemplateDoesNotExist
from jinja2 import FileSystemLoader, TemplateNotFound
from django.template.context import Context
import jinja2_funcs

# the environment is unconfigured until the first template is loaded.
_jinja_env = None

from jinja2_cacher import FragmentCacheExtension
from django.core.cache import cache

#So generic views can use jinja via 'template_loader': djangojinja2._jinja_env
class DjangoTemplate(jinja2.Template):
    def render(self, *args, **kwargs):
        if args and isinstance(args[0], Context):
            for d in reversed(args[0].dicts):
                kwargs.update(d)
            args = []
        return super(DjangoTemplate, self).render(*args, **kwargs)

class DjangoEnvironment(jinja2.Environment):
    template_class = DjangoTemplate

def get_env():
    """Get the Jinja2 env and initialize it if necessary."""
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = create_env()
    return _jinja_env


def create_env():
    """Create a new Jinja2 environment."""
    searchpath = list(settings.JINJA2_TEMPLATE_DIRS)
    ENV = DjangoEnvironment(loader=FileSystemLoader(searchpath),
                       auto_reload=settings.DEBUG,
                       cache_size=getattr(settings, 'JINJA2_CACHE_SIZE', 50),
                       extensions=[FragmentCacheExtension] + getattr(settings, 'JINJA2_EXTENSIONS', []))
    ENV.globals.update(jinja2_funcs.GLOBALS)
    ENV.filters.update(jinja2_funcs.FILTERS)
    ENV.fragment_cache = cache
    #trans = getattr(settings, 'LANGUAGE_CODE')
    ENV.install_null_translations(newstyle=True)
    ENV.fragment_cache_prefix = "fcache"
    return ENV


def get_template(template_name, globals=None):
    """Load a template."""
    try:
        return get_env().get_template(template_name, globals=globals)
    except TemplateNotFound, e:
        raise TemplateDoesNotExist(str(e))


def select_template(templates, globals=None):
    """Try to load one of the given templates."""
    env = get_env()
    for template in templates:
        try:
            return env.get_template(template, globals=globals)
        except TemplateNotFound:
            continue
    raise TemplateDoesNotExist(', '.join(templates))


def render_to_string(template_name, context=None, request=None, processors=None):
    """Render a template into a string."""
    context = dict(context or {})
    if request is not None:
        context['request'] = request
        for processor in chain(get_standard_processors(), processors or ()):
            context.update(processor(request))
    return get_template(template_name).render(context)


def render_to_response(template_name, context=None, request=None,
                       processors=None, mimetype=None):
    """Render a template into a response object."""
    if not mimetype:
        mimetype=settings.DEFAULT_CONTENT_TYPE
    if not "charset" in mimetype:
        mimetype = mimetype + "; charset=" + settings.DEFAULT_CHARSET
    return HttpResponse(render_to_string(template_name, context, request,
                                         processors), mimetype=mimetype)

get_env()
