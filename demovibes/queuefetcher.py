## Imports

import sys, random
import time
import bitly
import logging, logging.config

from os import popen
from datetime import datetime, timedelta

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import transaction

from webview.models import Queue, Song, DJRandomOptions
from webview import common


## Classes

class song_finder (object):
    songweight = getattr (settings, 'SONG_WEIGHT', {'N' : 1,
                                                    1   : 40,
                                                    1.5 : 35,
                                                    2   : 25,
                                                    2.5 : 20,
                                                    3   : 10,
                                                    3.5 : 6,
                                                    4   : 3,
                                                    4.5 : 2,
                                                    5   : 1})

    songweight_best = getattr (settings, 'SONG_WEIGHT_BEST', songweight)

    min_votes = getattr (settings, 'DJ_RANDOM_MIN_VOTES', 5)

    def __init__(self, djuser = None):
        self.sysenc = sys.getdefaultencoding()
        self.fsenc = sys.getfilesystemencoding()

        self.meta = None
        self.timestamp = None
        self.song = None

        self.log = logging.getLogger ("queuefetcher")

        if not djuser:
            djuser = getattr(settings, 'DJ_USERNAME', "djrandom")
        try:
            self.dj_user = User.objects.get(username = djuser)
        except:
            print "User (%s) not found! Aborting!" % djuser
            sys.exit(1)

        self.bitly_username = getattr(settings, 'BITLY_USERNAME', False)
        self.bitly_key = getattr(settings, 'BITLY_API_KEY', False)

        self.max_songlength = getattr(settings, 'DJ_MAX_LENGTH', None)
        self.twitter_username = getattr(settings, 'TWITTER_USERNAME', False)
        self.twitter_password = getattr(settings, 'TWITTER_PASSWORD', False)

        self.base_url = self.get_site_url()
        self.init_jt()
        self.weight_table = {
            'N' : 0,
            1   : 0,
            1.5 : 0,
            2   : 0,
            2.5 : 0,
            3   : 0,
            3.5 : 0,
            4   : 0,
            4.5 : 0,
            5   : 0
        }

    @transaction.commit_on_success
    def get_next_song (self):
        """
        Return next song filepath to be played. This is called by sockulf when it needs a new song.
        """

        # Force new transaction since we want to see newly committed transactions
        # (for repeatable read isolation level which is default for innodb).
        # Otherwise DJRandom will be unable to see newly queued songs until it queues its own song
        # (i.e. until it saves/commits its own song into db).
        transaction.commit ()

        # Guard against crash-looping or whatever...
        if self.timestamp:
            delta = datetime.now() - self.timestamp
            if delta < timedelta(seconds=3):
                self.log.warning(u"Song '%s' stopped playing after less than 3 seconds for some reason!" % self.meta)
                time.sleep(3)
        self.timestamp = datetime.now()

        # Find queued song or ask DJRandom for one)
        song = self.__find_queued ()

        # Update information for further usage
        self.meta = u"%s - %s" % (song.artist(), song.title)
        self.log.debug ("Now playing \"%s\" [ID %s]" % (song.title, song.id))
        self.song = song

        try:
            filepath = song.file.path.encode(self.fsenc)
        except:
            try:
                filepath = song.file.path.encode(self.sysenc)
            except:
                filepath = song.file.path

        self.log.debug ("Returning path %s" % filepath)

        return filepath

    def __find_queued (self):
        """
        Return next queued song, or a random song, or a jingle.
        """

        # Jingle time?
        if settings.PLAY_JINGLES:
            jingle = self.JingleTime()
            if jingle:
                return jingle

        # Fetch from queue with playtime explicitly set
        queues = Queue.objects.filter (played=False, playtime__lte = datetime.now()).order_by('-priority', 'id')

        # Nothing explicitly set for the moment, lets check normal queue entries
        if not queues:
            # Since OR queries have been problematic on production server earlier, we do this hack..
            queues = Queue.objects.filter (played=False, playtime = None).order_by ('-priority', 'id')

        if queues:
            # Something we should take from the queue
            queue = queues [0]
        else:
            # Nothing in queue, DJRandom turn
            song = self.getRandomSong ()
            queue = common.queue_song (song, self.dj_user, False, True)

        common.play_queued (queue)
        return queue.song

    def get_metadata(self):
        return self.meta.encode(self.sysenc, 'replace')

    def get_site_url(self):
        current_site = Site.objects.get_current()
        protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
        port     = getattr(settings, 'MY_SITE_PORT', '')
        base_url = '%s://%s' % (protocol, current_site.domain)
        if port:
            base_url += ':%s' % port
        return base_url

    def select_random(self, qs):
        nr = qs.count ()
        rand = random.randint (0, nr - 1)
        entry = qs [rand]
        return entry

    def getRandomSong (self):
        djrandom_options = DJRandomOptions.snapshot ()
        mood = djrandom_options.mood

        if mood == DJRandomOptions.MOOD_BEST:
            mood_weights = self.songweight_best
        elif mood == DJRandomOptions.MOOD_LEAST_VOTES:
            return self.get_least_voted (djrandom_options)
        else:
            mood_weights = self.songweight

        query = self.max_songlength and Song.active.filter(song_length__lt = self.max_songlength) or Song.active.all()
        query = query.filter (Song.unlocked_condition())
        song = self.select_random (query)

        C = 0
        self.log.debug("Trying to find a random song")

        # Try to find a good song that is not locked. Will try up to 50 times.
        while not self.isGoodSong (song, djrandom_options, mood_weights) and C < 50:
           self.log.debug("Random %s - song : %s [%s]" % (C, song.title, song.id))
           song = self.select_random(query)
           C += 1

        self.log.debug("Using song %s (%s)" % (song.title, song.id))

        return song

    def get_least_voted (self, djrandom_options):
        # Get songs, least voted songs first. Songs with the same amount of votes
        # are given in a pseudo random order
        order_by = ['rating_votes', 'times_played', 'rnd']
        if djrandom_options.avoid_explicit:
            order_by.insert (0, "explicit")

        qs = Song.active.filter (Song.unlocked_condition()).order_by (*order_by)

        return qs [0]

    def init_jt(self):
        self.jt = {
            'count': 0,
            'timelast': datetime.now(),
            'max': timedelta(minutes = 30),
            'min': timedelta(minutes = 20)
        }

    def isGoodSong(self, song, djrandom_options, mood_weights):
        """Check if song is a good song to play

        Checks if song is locked, and if that voteclass of songs have been played recently.
        Returns true or false
        """

        if djrandom_options.avoid_explicit and song.explicit:
            return False

        if song.rating_votes < self.min_votes: # Not voted or few votes
            C = 'N'
        else:
            C = int(round(2 * song.rating)) / 2.0

        if self.weight_table[C] >= mood_weights[C]:
            self.weight_table[C] = 0
            return True
        for X in self.weight_table.keys():
            self.weight_table[X] += 1

        return False

    def JingleTime(self):
        jt = self.jt
        if jt['timelast'] + jt['min'] < datetime.now():
            if jt['count'] >= 10 or jt['max'] + jt['timelast'] < datetime.now():
                jt['count'] = 0
                jt['timelast'] = datetime.now()
                S = Song.objects.filter(status='J')
                S = self.select_random(S)
                self.log.debug("JingleTime! ID %s" % S.id)
                return S
        jt['count'] += 1
        self.jt = jt
        return False

    def send_to_twitter(self, song):
        twitter_message = "Now Playing: %s - %s" % (song.artist(), song.title)

        if self.bitly_username and self.bitly_key:
            url = self.base_url + song.get_absolute_url()
            self.log.debug("Bitly : Full URL To Song URL: %s" % url)
            try:
                api = bitly.Api(login=self.bitly_username, apikey=self.bitly_key)
                short_url = api.shorten(url)
                twitter_message += ' - %s' % short_url
            except:
                self.log.warning("Bit.ly failed to shorten url!")

        if self.twitter_username and self.twitter_password:
            self.log.debug("Tweeting: %s" % twitter_message)
            self.tweet(self.twitter_username, self.twitter_password, twitter_message)

    def tweet(self, user, password, message):
        if len(message) < 140:
            url = 'http://twitter.com/statuses/update.xml'
            curl = 'curl --connect-timeout 10 -s -u %s:%s -d status="%s" %s' % (user, password, message, url)
            try:
                popen(curl, 'r')
            except:
                self.log.warning("Failed To Tweet: %s"% message)

## For flyspell
#  LocalWords:  sockulf queuefetcher innodb DJRandom filepath
