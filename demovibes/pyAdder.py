import sys, random, os
from datetime import datetime, timedelta
import time
import bitly
from os import popen
import logging, logging.config
from django.core.management import setup_environ
import settings
setup_environ(settings)
from webview.models import *
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from webview import common
from string import *

#Only set up logging if called directly
if __name__ == '__main__':
	if os.path.exists("logging.conf"):
    		logging.config.fileConfig("logging.conf")
	else:
    		logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] %(name)-8s %(levelname)-8s %(message)s")
Log = logging.getLogger("pyAdder")

enc = sys.getdefaultencoding()
fsenc = sys.getfilesystemencoding()

dj_username = getattr(settings, 'DJ_USERNAME', "djrandom")
max_length = getattr(settings, 'DJ_MAX_LENGTH', None)
twitter_username = getattr(settings, 'TWITTER_USERNAME', False)
twitter_password = getattr(settings, 'TWITTER_PASSWORD', False)

# Attempt to get Bit.ly details. Bit.ly is a free service that provides detailed
# Tracking to your tweets. Register for free at http://www.bit.ly and add the
# Username and Key (from the Account page) to your settings.py file.
bitly_username = getattr(settings, 'BITLY_USERNAME', False)
bitly_key = getattr(settings, 'BITLY_API_KEY', False)

try:
    djUser = User.objects.get(username = dj_username)
except:
    Log.critical("User '%s' does not exist! Please create that user or change user in pyAdder. Can not start!" % dj_username)
    sys.exit(1)

meta = None
timestamp = None

# Here we will attempt to construct the base url for the site.
current_site = Site.objects.get_current()
protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
port     = getattr(settings, 'MY_SITE_PORT', '')
base_url = '%s://%s' % (protocol, current_site.domain)
if port:
    base_url += ':%s' % port

# Jingles variable setup
jt_count = 0
jt_timelast = datetime.datetime.now()
jt_max = timedelta(minutes = 30)
jt_min = timedelta(minutes = 20)

#Good song weighting
# N is "No votes / fewer than 5 votes"
# The "weight" just means that the system will try to
# play X songs until it play one from that weight class again.
songweight = {
        'N' : 1,
        1 : 40,
        2 : 25,
        3 : 10,
        4 : 3,
        5 : 1,
    }

Weight = {
        'N' : 0,
        1 : 0,
        2 : 0,
        3 : 0,
        4 : 0,
        5 : 0
    }


# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.

def ices_init ():
        Log.debug("Ices initiating")
        return 1

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown ():
        Log.debug("Ices shutting down")
        return 1

# Function called to get the next filename to stream.
# Should return a string.
def ices_get_next ():
    global meta
    global timestamp
    global twitter_username
    global twitter_password

    if timestamp:
        delta = datetime.datetime.now() - timestamp
        if delta < timedelta(seconds=3):
            time.sleep(3)
            Log.warning("Song '%s' borked for some reason!" % meta)
    timestamp = datetime.datetime.now()
    Log.debug("Finding a new song for ices")
    song = findQueued()

    meta = "%s - %s" % (song.artist(), song.title)
    Log.debug("Now playing \"%s\" [ID %s]" % (song.title, song.id))

    # Now to add the song portion of the link to the end of it

    # Generate simplified Twitter message
    twitter_message = "Now Playing: %s - %s" % (song.artist(), song.title)

    # Append the Bit.Ly shortened URL, only if it's active
    if bitly_username and bitly_key:
        url = base_url + song.get_absolute_url()
        Log.debug("Bitly : Full URL To Song URL: %s" % url)
        try:
            api = bitly.Api(login=bitly_username, apikey=bitly_key)
            short_url = api.shorten(url)
            twitter_message += ' - %s' % short_url
        except:
            Log.warning("Bit.ly failed to shorten url!")

    if twitter_username and twitter_password:
        Log.debug("Tweeting: %s" % twitter_message)
        tweet(twitter_username,twitter_password,twitter_message)

    try:
        filepath = song.file.path.encode(enc)
    except:
        filepath = song.file.path.encode(fsenc, 'ignore')

    Log.debug("Giving ices path %s" % filepath)
    return filepath

def isGoodSong(song):
    """Check if song is a good song to play

    Checks if song is locked, and if that voteclass of songs have been played recently.
    Returns true or false
    """
    if song.is_locked() :
        return False
    global Weight
    if song.rating_votes < 5: # Not voted or few votes
        C = 'N'
    else:
        C = int(round(song.rating))
    if Weight[C] >= songweight[C]:
        Weight[C] = 0
        return True
    #print "Debug : C = %s, Weight[C] = %s, songweight[C] = %s" % (C, Weight[C], songweight[C])
    for X in Weight.keys():
        Weight[X] += 1
    return False

def getRandom():
    query = max_length and Song.active.filter(song_length__lt = max_length) or Song.active.all()
    songs = query.count()
    rand = random.randint(0,songs-1)
    song = query[rand]
    C = 0
    Log.debug("Trying to find a random song")
    # Try to find a good song that is not locked. Will try up to 10 times.
    while not isGoodSong(song) and C < 10:
       Log.debug("Random %s - song : %s [%s]" % (C, song.title, song.id))
       rand = random.randint(0,songs-1)
       song = query[rand]
       C += 1
    Log.debug("Using song %s (%s)" % (song.title, song.id))
    Q = common.queue_song(song, djUser, False, True)
    common.play_queued(Q)
    return song

def JingleTime():
    global jt_count
    global jt_timelast
    if jt_timelast + jt_min < datetime.datetime.now():
        if jt_count >= 10 or jt_max + jt_timelast < datetime.datetime.now():
            jt_count = 0
            jt_timelast = datetime.datetime.now()
            S = Song.objects.filter(status='J').order_by('?')[0]
            Log.debug("JingleTime! ID %s" % S.id)
            return S
    jt_count += 1
    return False

def findQueued():
    songs = Queue.objects.filter(played=False, playtime__lte = datetime.datetime.now()).order_by('-priority', 'id')
    if not songs: # Since OR queries have been problematic on production server earlier, we do this hack..
        songs = Queue.objects.filter(played=False, playtime = None).order_by('-priority', 'id')
    if settings.PLAY_JINGLES:
        jingle = JingleTime()
        if jingle:
            return jingle
    if songs:
        song = songs[0]
        common.play_queued(song)
        return song.song
    else:
        return getRandom()

# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata ():
        #return 'Artist - Title (Label, Year)'
        Log.debug("Ices asked for metadata, giving %s" % meta.encode(enc, 'replace'))
        return meta.encode(enc, 'replace')

# function to update twitter with currently playing song
def tweet(user, password, message):
    if len(message) < 140:
        url = 'http://twitter.com/statuses/update.xml'
        curl = 'curl --connect-timeout 10 -s -u %s:%s -d status="%s" %s' % (user,password,message,url)
        try:
            pipe=popen(curl, 'r')
        except:
            Log.warning("Failed To Tweet: %s"% message)
