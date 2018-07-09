#!/usr/bin/env python

# Album Art Conversion Script
#
# Converts the existing album art covers from the old Compilation screenshot
# System, placing them into the new Screenshot class and assigning the correct
# ID to that compilation. After many unsuccessful attempts at getting this to
# Work via a migration, I have placed it into this script instead. 
#
# This will not patch the songs in the compilation, as they may already be assigned
# To other screenshots. Other logic will display the compilation artwork when playing
# If no other images exist. FishGuy876

from django.core.management import setup_environ
import settings
setup_environ(settings)
from webview.models import *

comps = Compilation.objects.all()

for c in comps:
    if c.cover_art:
        try:
            print 'Converting: ' + c.name
            c.convert_screenshot()
        except:
            print 'Error Occured (Screenshot Name Probbably Exists Already)'
    else:
        print 'No Album Art For: ' + c.name

