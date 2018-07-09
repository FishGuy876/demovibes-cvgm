# Customized Settings From settings.py
# Modified versions of this file are ignored in the Repo

from smileys import SMILEYS
from secretsmileys import SECRETSMILEYS

# Allow the new song locktime calculations to be used
from webview.song_locktime import calc_songlock

DEBUG = False

#ADMINS = (
#    ('FishGuy876', 'andy@andykellett.com'),
#)

#MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE'    : 'django.db.backends.mysql',
        'NAME'      : 'db',
        'USER'      : 'db',
        'PASSWORD'  : 'password',
        'HOST'      : '127.0.0.1',
        'PORT'      : '',
        # Use the following on MySQL 5.5
        # 'OPTIONS'   : {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'},
        }
    }

# Customize the dimensions on the avatars used on the site. AVATAR_SIZE is a value in
# Bytes that the image file cannot exceed. Reccomend no less than 40Kb so users can have
# Some pretty AnimGIF files to use. HEIGHT and WIDTH are specified in pixels.
MAX_AVATAR_SIZE = 95536
MAX_AVATAR_HEIGHT = 150
MAX_AVATAR_WIDTH = 150

# Artist pictures can also be customized to fit your site using these values
MAX_ARTIST_AVATAR_SIZE = 95536
MAX_ARTIST_AVATAR_HEIGHT = 400
MAX_ARTIST_AVATAR_WIDTH = 400

# Group Logo controls
MAX_GROUP_AVATAR_SIZE = 95536
MAX_GROUP_AVATAR_HEIGHT = 400
MAX_GROUP_AVATAR_WIDTH = 400

# When working with text links, users can submit icons to accompany them. These determine
# The maximum allowed dimensions for all text link icons submitted via the webform.
MAX_LINK_IMG_SIZE = 16384
MAX_LINK_IMG_WIDTH = 75
MAX_LINK_IMG_HEIGHT = 18

# When displaying screenshots, pouet images and youtube videos, you can configure a maximum
# Width & Height of those images here. These same values are used to verify newly added
# Screenshots. Larger images are scaled down to fit the width, and smaller images are scaled
# Upwards to fit within the frame.
THUMB_DISPLAY_WIDTH = 190
THUMB_DISPLAY_HEIGHT = 190
THUMB_DISPLAY_BORDER = 0

# We can also limit the size of the original sized image
SCREEN_UPLOAD_WIDTH = 1024
SCREEN_UPLOAD_HEIGHT = 1024

# Specify a quality level for scaled images
SCREEN_SCALE_QUALITY = 90

# Specify an output format, such as png, jpeg etc. PNG is the default, as its always available in
# PIL. If you need to install libjpeg, make sure you rebuild PIL afterwards.
SCREEN_SCALE_FORMAT = 'png'

# Max internal length of the oneliner, in characters
MAX_ONELINER_LENGTH = 256

#MEDIA_ROOT = '/path/to/this/static/'

# Please set a backend here
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'Hehe'

# Maximum number of songs a user can have in the queue at the same time.
#SONGS_IN_QUEUE = 6

# Optional filter for how many songs of "lowvote" or lower user can have in queue
SONGS_IN_QUEUE_LOWRATING = {'limit': 2, 'lowvote':2.5}

# Time to lock a song until it can be requested again.
#SONG_LOCK_TIME = { 'days' : 18, 'hours' : 6, 'minutes' : 0 }
#SONG_LOCK_TIME_RANDOM = { 'days' : 6, 'hours' : 4, 'minutes' : 5 }

# This one really is affected by the crapness of the song
SONG_LOCK_TIME_VOTE = { 'days' : 18, 'hours' : 6, 'minutes' : 5 }


# Need to have at least one song marked as jingle for this to work
# Will play one every 30 minutes or 10 songs, but not more often than every 20 minutes.
PLAY_JINGLES = True

# How many objects per page:
PAGINATE = 100
FORUM_PAGINATE = 30

# When displaying approved songs, specify the maximum number to display on the page here.
# You should take into account that you will want to display about an average of 2 days worth
# Of uploads; Otherwise the list will never be useful except at the time a new batch of
# Large songs are approved. AAK
#UPLOADED_SONG_COUNT = 100

# Stuff affecting how DJ Random picks good songs to play depending on mood
DJ_RANDOM_MIN_VOTES = 2  # The number of votes needed to be considered by DJ Random (Default: 5)

# Time to mute new users. To limit oneliner spam accounts
#
#import datetime
#NEW_USER_MUTE_TIME = datetime.timedelta(minutes=5)

## Ban / Mute settings
#
BAN_ANNOUNCE = True
BANTIME_MIN = 5
BANTIME_MAX = 10080
BANTIME_INITIAL = 15

## List of domains to not accept email registration from
#BAD_EMAIL_DOMAINS = []

# Attempt to set some SongWeight values
SONG_WEIGHT = {
 'N' : 18,
 1 : 50,
 1.5 : 40,
 2 : 30,
 2.5 : 20,
 3 : 7,
 3.5 : 5,
 4 : 3,
 4.5 : 2,
 5 : 1
}

# You can specify if you want shortened url's in the oneliner. If enabled, it will take
# A link such as http://www.blah.com/blah/bleh/blob.html and make a clickable link to
# Only http://www.blah.com in the display portion, the clicked link contains the full path.
# Set to a value of 1 to enable truncated links.
SHORTEN_ONELINER_LINKS = 1

FILE_UPLOAD_PERMISSIONS = 0755
FILE_UPLOAD_MAX_MEMORY_SIZE = 128

# Where /static/ files are.
# XXX Only to be used for development server! XXX
#DOCUMENT_ROOT = '/home/cvgm/cvgm.net/static/'

# Custom CSS
#DEFAULT_CSS = '/static/themes/default/cvgm_style.css'
DEFAULT_CSS = '/static/themes/cvgm_black/cvgm_black.css'  # CSS by Rams Le Prince

#To make this work you need:
#  1. uWSGI
#  2. start the uwsgi_eventhandler module
#  3. Point /demovibes/ajax/monitor/* urls to it
UWSGI_EVENT_SERVER = ("127.0.0.1", 3032)
#UWSGI_EVENT_SERVER_HTTP = "http://www.site.net/demovibes/ajax/monitor/new/"

# To protect private notices from prying eyes, type a random secret here.
UWSGI_ID_SECRET = "Cheeky Peepers"

## Decides if a user can vote on and request his own songs
SONG_SELFQUEUE_DISABLED = True
SONG_SELFVOTE_DISABLED = True

# Determines which notifications we want active on CVGM
#NOTIFY_NEW_FORUM_POST = True
#NOTIFY_NEW_FORUM_THREAD = True
#NOTIFY_NEW_SONG_APPROVED = False
#NOTIFY_NEW_SONG_COMMENT = True

# Only show tag cloud entries with this number of entries
#TAG_CLOUD_MIN_COUNT = 5

RADIO_STATUS_VOTED_MIN_VOTES = 5

# Define a function to return extra locktime for vote
# Song is first and only parameter, a number between 0 and 1 should be
# retuned from that function
SONG_LOCKTIME_FUNCTION = calc_songlock

# List of smileys to be restricted to certain users
#RESTRICTED_SMILEYS = [("trigger", "smiley image")]
#
# List of usernames allowed to use the restricted smileys
#RESTRICTED_SMILEYS_USERS = ["username"]

# Time to mute new users. To limit oneliner spam accounts
#
#import datetime
#NEW_USER_MUTE_TIME = datetime.timedelta(minutes=5)

# Always show screenshots for Anonymous users
SHOW_ANONYMOUS_SCREENSHOTS = True

# If you wish to turn off Uploading (maintenance, or other reasons) then set this to True.
# IF the user tries to Upload during this time, they will be re-directed back to the Queue page
DISABLE_UPLOADS = True

# When a user views the Forums, they will now display the most recent posts to any forum, except
# For private forums. This number specifies how many posts are shown on the screen to the user.
NUM_DISPLAY_LAST_FORUM_POSTS = 5

# You can adjust the size of the truncation of the posts using this value. Make the number larger 
# To show more characters in a message preview.
TRUNCATED_THREAD_STRING_SIZE = 256

# When creating a new compilation, alter the number of search results that are returned when searching
# For songs directly within the Add Compilation screen. The default is 20.
NUM_SONGS_PER_COMPILATION_SEARCH = 30


