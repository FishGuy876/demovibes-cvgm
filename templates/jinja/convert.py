
import sys
import re

#Fixes some standard django -> jinja2 stuff.

class changer:
    exp = (
        (r'{%\s*with\s+([\w\.]+)\s+as\s+(\w+)\s*%}', r'{% set \2 = \1 %}'),
        (r'{%\s*endwith\s*%}', r''),
        (r'forloop.', r'loop.'),
        (r'{%\s*url\s+([^\s]+)\s*%}', r'{{ url("\1") }}'),
        (r'{%\s*load.*?%}', r''),
        (r'({%\s*cache\s+.*?%})', r'{# \1 #}'),
        (r'({%\s*endcache\s*%})', r'{# \1 #}'),
        (r'.all', r'.all()'),
        (r'is_authenticated', r'is_authenticated()'),
        (r'{%\s*ifnotequal\s+([^\s]+)\s+([^\s]+)\s*%}', r'{% if \1 != \2 %}'),
        (r'{%\s*endifnotequal\s*%}', r'{% endif %}'),
        (r'{%\s*ifequal\s+([^\s]+)\s+([^\s]+)\s*%}', r'{% if \1 == \2 %}'),
        (r'{%\s*endifequal\s*%}', r'{% endif %}'),
        #(r'|slice:"(.+?)"', r'[\1]'),
        (r'(|\w+):(".+?")', r'\1(\2)'),
        (r'.get_absolute_url', r'.get_absolute_url()'),
        (r'{%\s*url\s+([^\s]+)\s+([^\s]+)\s*%}', r'{{ url ("\1", \2) }}'),
        (r'.as_table', r'.as_table()'),
        (r'{%\s*site_(\w+)\s*%}', r'{{ dv.site_\1() }}'),
    )
    def __init__(self):
        temp = []
        for x in self.exp:
            temp.append((re.compile(x[0]), x[1]))
        self.exp = temp
        
    def convert(self, string):
        for x in self.exp:
            string = x[0].sub(x[1], string)
        return string


if __name__ == "__main__":
    OO = open(sys.argv[1])
    F = OO.read()
    OO.close()
    conv = changer()
    F = conv.convert(F)
    print F
