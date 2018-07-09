from django.template import TemplateDoesNotExist
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template

if getattr(settings, 'JINJA2_TEMPLATE_DIRS', False):
    JINJA = True
else:
    JINJA = False

import djangojinja2

def r2r(template_name, context=None, request=None, processors=None, mimetype=None):
    if JINJA:
        try:
            return djangojinja2.render_to_response(template_name, context, request, processors, mimetype)
        except TemplateDoesNotExist:
            pass
    return render_to_response(template_name, context, request and RequestContext(request) or request)

def r2s(template_name, context=None, request=None, processors=None):
    if JINJA:
        try:
            return djangojinja2.render_to_string(template_name, context, request, processors)
        except TemplateDoesNotExist:
            pass
    T = get_template(template_name)
    C = Context (context)
    result = T.render(C)
    return result

def render_string(string, context):
    pad = """{%- import "macro/display.html" as display -%}"""
    template = djangojinja2.get_env().from_string(pad + string)
    return template.render(context)
