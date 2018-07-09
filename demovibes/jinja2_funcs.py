from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext as _
from django.template import defaultfilters
from jinja2 import escape

from webview.models import TimeDelta
from webview.templatetags import dv_extend

def dummy(dummystuff):
    return "Dummy for %s" % dummystuff

def mkstr(*args):
    args = [unicode(x) for x in args]
    return u''.join(args)

def url(view_name, *args, **kwargs):
    from django.core.urlresolvers import reverse, NoReverseMatch
    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        try:
            project_name = settings.SETTINGS_MODULE.split('.')[0]
            return reverse(project_name + '.' + view_name,
                           args=args, kwargs=kwargs)
        except NoReverseMatch:
            return ''

def nbspize(text):
    import re
    return re.sub('\s','&nbsp;',text.strip())

def get_lang():
    return translation.get_language()

def timesince(date):
    from django.utils.timesince import timesince
    return timesince(date)

def timeuntil(date):
    from django.utils.timesince import timesince
    from datetime import datetime
    return timesince(datetime.now(),datetime(date.year, date.month, date.day))

def timedelta(seconds):
    return TimeDelta(seconds = int(seconds)).to_string (day_delim = _(" days "))

def mksafe(arg):
    """
    Force escaping of html

    First turn it into a Markup() type with escape, then force it into unicode again,
    so other modifications to the string won't be automatically escaped.
    """
    result = escape(arg)
    result = unicode(result)
    return result


#dict of filters
FILTERS = {
    'time': defaultfilters.time,
    'date': defaultfilters.date,
    'escapejs': defaultfilters.escapejs,
    'pluralize': defaultfilters.pluralize,
    'timesince': timesince,
    'timeuntil': timeuntil,
    'timedelta': timedelta,
    'floatformat': defaultfilters.floatformat,
    'linebreaks': defaultfilters.linebreaks,
    'linebreaksbr': defaultfilters.linebreaksbr,
    'smileys': dv_extend.smileys,
    'smileys_oneliner': dv_extend.smileys_oneliner,
    'oneliner_mediaparse': dv_extend.oneliner_mediaparse,
    'bbcode_oneliner': dv_extend.bbcode_oneliner,
    'bbcode': dv_extend.bbcode,
    'dv_urlize': dv_extend.dv_urlize,
    'mksafe': mksafe,
    'restricted_smileys': dv_extend.smileys_restricted,
}

# Dictionary over globally avaliable variables and functions
GLOBALS = {
    'url': url,
    'mkstr': mkstr,
    'dummy': dummy,
    'dv': dv_extend,
    'STATIC_URL': settings.MEDIA_URL,
}
