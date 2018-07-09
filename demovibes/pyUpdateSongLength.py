#!/usr/bin/env python
import mad

from django.core.management import setup_environ
import settings
setup_environ(settings)
from webview.models import *

from string import *

songs = Song.objects.filter(song_length=None)
songs = Song.objects.all()
for song in songs:
    print "Doing song", song
    mf = mad.MadFile(song.file.path)
    seconds = mf.total_time()/1000
    song.song_length = seconds
    song.save()
