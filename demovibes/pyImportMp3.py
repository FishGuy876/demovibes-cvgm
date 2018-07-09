#!/usr/bin/env python

import sys, os, getopt

import warnings
warnings.filterwarnings ("ignore", category = DeprecationWarning)

import logging
logging.basicConfig (level=logging.INFO, datefmt='%H:%M', format='[%(asctime)s] %(message)s')

from django.core.management import setup_environ
import settings
setup_environ(settings)

from webview import dscan
from django.contrib.auth.models import User

from webview.models import *
from tagging.models import Tag

from string import *

def usage():
    print """Adds an mp3 to the database.

-f <file>           Path to file
-t <title>          Title of song
-a <artist>         Artist (Can be used multiple times)
-u <user>           User for auto-approve
-y <year>           Year
-s <source id>      Source database id
-T <tags>           Comma separated tags list
-C                  Auto add artist if he does not exist.

--status=<char> Song status. Can be:
        A - Active (Default)
        I - Inactive
        J - Jingle
        V - Needs verification
"""

try:
    opts, args = getopt.getopt(sys.argv[1:], "hy:f:t:a:u:s:T:C", ["help", "status="])
except getopt.GetoptError:
    usage()
    sys.exit(2)

if not dscan.is_configured ():
    print "Dscan should be configured!"
    sys.exit(3)

create = False
status = "A"
artists = []
user = None
year = None
source = None
tags = None


for opt, arg in opts:
    arg = arg.decode ('utf-8')

    if opt in ("-h", "--help"):
        usage()
        sys.exit()
    elif opt == '-f':
        music = arg
    elif opt == '-u':
        user = arg.strip()
    elif opt == '-y':
        year = arg.strip()
    elif opt == '-T':
        tags = map (lambda x: x.strip(), arg.split (","))
    elif opt == '-s':
        source = int(arg.strip())
    elif opt == '-t':
        title = arg.strip()
    elif opt == '-a':
        artists.append(arg.strip())
    elif opt == '-C':
        create = True
    elif opt == '--status':
        status = arg

if not os.path.exists(music):
    print "File does not exist!"
    sys.exit(4)

if not os.path.isfile(music):
    print "File is not file at all!"
    sys.exit(5)

# Get user
user = User.objects.get (username = user)

if source:
    source = SongType.objects.get (id = source)

if tags:
    # Make sure we don't create tags with typos and so on. Only existing tags are allowed'
    for tag in tags:
        try:
            Tag.objects.get (name = tag)
        except:
            print "Tag doesn't exist: " + tag
            sys.exit (99)

# Get artists
A = []
for artist in artists:
    A1 = Artist.objects.filter (handle = artist)
    if A1:
        A.append (A1[0])
    else:
        if create:
            print "Can not find artist. Creating.."
            A1 = Artist(handle=artist)
            A1.save()
            A.append(A1)
        else:
            print "Can not find artist. Exiting." % artist
            sys.exit(1)

# Create song record
song = Song (title = title, file = "media/" + music, status = status, uploader = user)
song.save()

songinfo = SongMetaData (user = user,
                         song = song,
                         checked = True,
                         active = True,
                         release_year = year,
                         type = source)
songinfo.save()

# Song metadata

for artist in A:
    songinfo.artists.add (artist)
songinfo.save()

# Approve
Q = SongApprovals (song = song, approved_by = user, uploaded_by = user)
Q.save ()

# Tag
if tags:
    ttags = " ".join (tags)
    TagHistory.objects.create (user = user, song = song, tags = ttags)
    Tag.objects.update_tags (song, ttags)

# Print result
print "    Song id: " + str(song.id)
print " .. Added!"

#  LocalWords:  usr env asctime hy Dscan metadata
