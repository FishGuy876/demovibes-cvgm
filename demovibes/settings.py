# Default settings for demovibes project.
# Do not change most of these settings, use settings-local.py instead!

import os
import django
# calculated paths for django and the site
# used as starting points for various other paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
SITE_ROOT = os.path.dirname(SITE_ROOT)

def pj(*path):
    return os.path.join(SITE_ROOT, *path)

from smileys import SMILEYS

LOGIN_URL = "/account/signin/"

DEMOVIBES_VERSION = "1.0.0"

DEBUG = True
TEMPLATE_DEBUG = False

#For looking up flag country on users with no flag set
# IPCountry Lookup data can be obtained from https://db-ip.com/db/download/ip-to-country-lite
LOOKUP_COUNTRY = True
DEFAULT_FLAG = "nectaflag"

# URL to use for Flash streaming.
#FLASH_STREAM_URL = "http://server:port/stream"

#UWSGI_EVENT_SERVER = ("127.0.0.1", 3032)

#If you have vserver that need a specific url, use this:
#UWSGI_EVENT_SERVER_HTTP = "http://<hostname>/demovibes/ajax/monitor/new/"
# Remember to also add ip to allowed_ips in uwsgi_eventhandler/local_settings.py

# To protect private notices from prying eyes, type a random secret here.
#UWSGI_ID_SECRET = ""
# Note that the same setting will have to be in local_config.py for
# uwsgi_eventhandler for it to work.

#from django.conf import global_settings
#FILE_UPLOAD_HANDLERS = ('webview.uploadprogress.UploadProgressCachedHandler', ) + \
#    global_settings.FILE_UPLOAD_HANDLERS

## Decides if a user can vote on and request his own songs
#SONG_SELFQUEUE_DISABLED = False
#SONG_SELFVOTE_DISABLED = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

HAYSTACK_SITECONF = 'demovibes.search_sites'
HAYSTACK_SEARCH_ENGINE = "whoosh"
HAYSTACK_WHOOSH_PATH = pj("local","whoosh")

DATABASES = {
    'default': {
        'ENGINE'    : 'django.db.backends.sqlite3',
        'NAME'      : pj('sqlite.db'),
        'USER'      : '',
        'PASSWORD'  : '',
        'HOST'      : '',
        'PORT'      : '',
        # Use the following on MySQL 5.5
        # 'OPTIONS'   : {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'},
        }
    }

# Search results per type (group, artist, songs)
SEARCH_LIMIT = 40

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

ACCOUNT_ACTIVATION_DAYS = 7

## Notifications

NOTIFY_NEW_FORUM_POST = False
NOTIFY_NEW_FORUM_THREAD = False
NOTIFY_NEW_SONG_APPROVED = False
NOTIFY_NEW_SONG_COMMENT = False
# There may be a situation where your server doesn't have a built-in SMTP server, and you
# Wish to use a 3rd party SMTP server. Uncommenting these boxes and setting them accordingly
# Will allow this to take place. The default SMTP options may not deliver to outside world, in
# Which case, use this instead. AAK.

# Host for sending e-mail. This would be the SMTP host for your email provider
#EMAIL_HOST = ''
#DEFAULT_FROM_EMAIL = ""

# Port for sending e-mail. By default, it is almost always 25.
#EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST. Some SMTP servers require the
# Authoriazation to be the same as the email address for the count, and work better using
# The + chanarcter instead of @.
#EMAIL_HOST_USER = 'smtpuser+domain.com'
#EMAIL_HOST_PASSWORD = 'smtp_password'
#EMAIL_USE_TLS = False

# END SMTP Configuration

# Cherokee secure url shared key
# If empty, disable
# The secure url root should point to static folder.
# See http://www.cherokee-project.com/doc/modules_handlers_secdownload.html for more info
CHEROKEE_SECRET_DOWNLOAD_KEY=""
CHEROKEE_SECRET_DOWNLOAD_PATH=""
# IF defined, will alter default file url with re.sub(r1, r2, url)
#CHEROKEE_SECRET_DOWNLOAD_REGEX=(r'', r'')
# If defined, will limit number of generated links per user to X links per Y seconds
#CHEROKEE_SECRET_DOWNLOAD_LIMIT={'number': X, 'seconds': Y}
# Or, more specified:
#CHEROKEE_SECRET_DOWNLOAD_LIMIT={
#    'admin': {'number': 30, 'seconds': 60*60*24},
#    'Group name': {'number': 15, 'seconds': 60*60*24},
#    'default': {'number': 0, 'seconds': 60*60*24},
#    'staff': {'number': 3, 'seconds': 60*60*24},
#}
# URL to redirect to if limit is reached
#CHEROKEE_SECRET_DOWNLOAD_LIMIT_URL="/static/badman.html"

# maximum time a song will be played in seconds
# only used when demosauce streamer is used
# default fadeout is right before knucklebusters gets ugly
# comment out or set to zero to disable
#MAX_SONG_LENGTH = 480

#location of demosauce scan tool
DEMOSAUCE_SCAN = pj("demosauce", "scan")

# a value that decides if a module is likely to be loopded. 0.1 seems to be good for starters
# only required if demosauce scan is used
LOOPINESS_THRESHOLD = 0.1

# time a song is looped in seconds
# this ONLY applies to modules (.mod, .xm, etc...) AND if a loop has been detected
# only required if demosauce scan is used
LOOP_LENGTH = 150

# Customize the dimensions on the avatars used on the site. AVATAR_SIZE is a value in
# Bytes that the image file cannot exceed. Reccomend no less than 40Kb so users can have
# Some pretty AnimGIF files to use. HEIGHT and WIDTH are specified in pixels.
MAX_AVATAR_SIZE = 65536
MAX_AVATAR_HEIGHT = 100
MAX_AVATAR_WIDTH = 100

# Artist pictures can also be customized to fit your site using these values
MAX_ARTIST_AVATAR_SIZE = 65536
MAX_ARTIST_AVATAR_HEIGHT = 200
MAX_ARTIST_AVATAR_WIDTH = 200

# Group Logo controls
MAX_GROUP_AVATAR_SIZE = 65536
MAX_GROUP_AVATAR_HEIGHT = 250
MAX_GROUP_AVATAR_WIDTH = 250

MAX_COMPILATION_ICON_WIDTH = 16
MAX_COMPILATION_ICON_HEIGHT = 16
MAX_COMPILATION_ICON_SIZE = 16384

# When displaying screenshots, pouet images and youtube videos, you can configure a maximum
# Width & Height of those images here. These same values are used to verify newly added
# Screenshots. Larger images are scaled down to fit the width, and smaller images are scaled
# Upwards to fit within the frame.
#
# You should also remember that base.css contains hard-coded screenshot sizes that will be affected
# By the theme, depending on how big or small you make these. Alter the following elements in
# base.css, element div.screenshot (currently around line 100):
#
# div.screenshot {
#     padding: 3px;
#     text-align: center;
#     margin: 4px;
#     float: left;
#     height: 150px;		<-- Adjust this to best viaually fit your changes
#     width: 128px;			<-- Adjust this to best visually fit your changes
# }
#
THUMB_DISPLAY_WIDTH = 128			# Specify the maximum width of the generated thumbnail, in pixels
THUMB_DISPLAY_HEIGHT = 128			# Specify the maximum height of a thumbnail, in pixels
THUMB_DISPLAY_BORDER = 0			# Passed to template as variable 'scrborder' so the CSS etc. can add a border size around images
SCREEN_SCALE_QUALITY = 85			# Specify a quality level for scaled images (for file formats that support it)
SHOW_ANONYMOUS_SCREENSHOTS = False  # Set this to TRUE to show song screenshots for users not logged in

# Specify a maximum width/height for screenshot uploads, in pixels
SCREEN_UPLOAD_WIDTH = 800
SCREEN_UPLOAD_HEIGHT = 800

# Specify an output format, such as png, jpeg etc. PNG is the default, as its always available in
# PIL. If you need to install libjpeg, make sure you rebuild PIL afterwards.
SCREEN_SCALE_FORMAT = 'png'

# Max internal length of the oneliner, in characters
MAX_ONELINER_LENGTH = 256

# In the updates page, you can limit the number of entries displayed for each category by
# Adjusting these values accordingly.
RECENT_ARTIST_VIEW_LIMIT  = 20
RECENT_SONG_VIEW_LIMIT    = 20
RECENT_LABEL_VIEW_LIMIT   = 20
RECENT_GROUP_VIEW_LIMIT   = 20
RECENT_COMP_VIEW_LIMIT    = 20

# Adjust this value to show the most recent member count at the bottom of the 'Who's Online' section
# For new members. The default is 1 user, but can be any number to suit your site and layout. Newest
# Members will appear at the beginning of the list.
SHOW_NEW_MEMBER_COUNT = 1

# Auto-Approve Admin Uploads
#
# Anyone with a Super User status who uploads tracks will be auto approved if set to 1. No
# Email notification will be sent if this occurs. Default is Off (0). Set to 1 to Enable.
ADMIN_AUTO_APPROVE_UPLOADS = 0
ADMIN_AUTO_APPROVE_GROUP = 0
ADMIN_AUTO_APPROVE_LABEL = 0
ADMIN_AUTO_APPROVE_ARTIST = 0
ADMIN_AUTO_APPROVE_COMPILATION = 0
ADMIN_AUTO_APPROVE_SCREENSHOT = 0

# When users submit new song info, do we email them when its approved? Many users get annoyed by this, and
# Setting to False will only email them if it's rejected.
ADMIN_EMAIL_ON_INFO_APPROVE = False

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = DOCUMENT_ROOT = pj('static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Please set a backend here
# We recommend memcached.
# If that's not avaliable we recommend file or database cache,
# because locmem can't always be trusted to have a consistent cache
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
#CACHE_BACKEND = 'dummy://'

# UWSGI Server is needed to handle background transactions such as oneliner and other internal events
#To make this work you need:
#  1. uWSGI
#  2. start the uwsgi_eventhandler module
#  3. Point /demovibes/ajax/monitor/* urls to it
UWSGI_EVENT_SERVER = ("127.0.0.1", 3032)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'replaceThis!'

AUTH_PROFILE_MODULE = 'webview.userprofile'


# Default flag to show for people having no flag or mistyped flag
#DEFAULT_FLAG = "nectaflag"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_authopenid.middleware.OpenIDMiddleware',
    'django.middleware.transaction.TransactionMiddleware'
 #add ?profiler to url to get a profile of the page. Debug needs to be on
)

ROOT_URLCONF = 'demovibes.urls'

# New changes introduced to demovibes to support user/global template changes. The
# Local folder should always be checked first for user customized templates. In the
# Event that this fails, then the global template is used instead. AAK.
TEMPLATE_DIRS = (
    pj('templates', 'local'),
    pj('templates', 'global'),
    pj('templates', 'jinja', 'local'),
    pj('templates', 'jinja', 'global'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

JINJA2_TEMPLATE_DIRS = (
    pj('templates', 'jinja', 'local'),
    pj('templates', 'jinja', 'global'),
)

JINJA2_EXTENSIONS = ["jinja2.ext.i18n"]

# The minimum number of songs in queue before limits are considered
#MIN_QUEUE_SONGS_LIMIT = 1

# Maximum number of songs a user can have in the queue at the same time.
SONGS_IN_QUEUE = 5

# Optional filter for how many songs of "lowvote" or lower user can have in queue
#SONGS_IN_QUEUE_LOWRATING = {'limit': 1, 'lowvote':2}

#QUEUE_TIME_LIMIT = (
#   { 'days' : 0, 'hours' : 0, 'minutes' : 5 }, # Max combined song time
#   { 'days' : 0, 'hours' : 0, 'minutes' : 5 }  # Over this period of time
#)

# Time to lock a song until it can be requested again.
SONG_LOCK_TIME = { 'days' : 0, 'hours' : 0, 'minutes' : 5 }
#SONG_LOCK_TIME_VOTE = { 'days' : 0, 'hours' : 0, 'minutes' : 5 }
#SONG_LOCK_TIME_RANDOM = { 'days' : 0, 'hours' : 0, 'minutes' : 5 }

# Define a function to return extra locktime for vote
# Song is first and only parameter, a number between 0 and 1 should be
# retuned from that function
# SONG_LOCKTIME_FUNCTION = None

# Need to have at least one song marked as jingle for this to work
# Will play one every 30 minutes or 10 songs, but not more often than every 20 minutes.
PLAY_JINGLES = False

#SONG_WEIGHT = {
# 'N' : 18,
# 1 : 50,
# 1.5 : 40,
# 2 : 30,
# 2.5 : 20,
# 3 : 7,
# 3.5 : 5,
# 4 : 3,
# 4.5 : 2,
# 5 : 1}

#DJ_RANDOM_MIN_VOTES = 1
RADIO_STATUS_VOTED_MIN_VOTES = 9

# How many objects per page:
PAGINATE = 30
FORUM_PAGINATE = 15

# When displaying approved songs, specify the maximum number to display on the page here.
# You should take into account that you will want to display about an average of 2 days worth
# Of uploads; Otherwise the list will never be useful except at the time a new batch of
# Large songs are approved. AAK
UPLOADED_SONG_COUNT = 150

# If you wish to turn off Uploading (maintenance, or other reasons) then set this to True.
# IF the user tries to Upload during this time, they will be re-directed back to the Queue page
DISABLE_UPLOADS = False

# When a user views the Forums, they will now display the most recent posts to any forum, except
# For private forums. This number specifies how many posts are shown on the screen to the user.
NUM_DISPLAY_LAST_FORUM_POSTS = 5

# You can adjust the size of the truncation of the posts using this value. Make the number larger 
# To show more characters in a message preview.
TRUNCATED_THREAD_STRING_SIZE = 256

# When creating a new compilation, alter the number of search results that are returned when searching
# For songs directly within the Add Compilation screen. The default is 20.
NUM_SONGS_PER_COMPILATION_SEARCH = 20

# You can specify if you want shortened url's in the oneliner. If enabled, it will take
# A link such as http://www.blah.com/blah/bleh/blob.html and make a clickable link to
# Only http://www.blah.com in the display portion, the clicked link contains the full path.
# Set to a value of 1 to enable truncated links.
SHORTEN_ONELINER_LINKS = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django_authopenid.context_processors.authopenid',
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'demovibes.webview',
    'demovibes.registration',
    'demovibes.forum',
    'django.contrib.markup',
    'south',
    'tagging',
    'django_extensions',
    'haystack',
    'openid_provider',
    'demovibes.search',
    'django_authopenid',
]

try:
    import django_wsgiserver
    INSTALLED_APPS.append("django_wsgiserver")
except:
    pass

## SMILEY LIMITS
##
# Note that total is not hard limit, and can in some cases
# allow (PER_SMILEY_LIMIT - 1) smileys extra

#ONELINER_PER_SMILEY_LIMIT = 0
#ONELINER_TOTAL_SMILEY_LIMIT = None
#OTHER_PER_SMILEY_LIMIT = 0
#OTHER_TOTAL_SMILEY_LIMIT = None

# List of smileys to be restricted to certain users
#RESTRICTED_SMILEYS = [("trigger", "smiley image")]
#
# List of usernames allowed to use the restricted smileys
#RESTRICTED_SMILEYS_USERS = ["username"]

# Time to mute new users. To limit oneliner spam accounts
#
#import datetime
#NEW_USER_MUTE_TIME = datetime.timedelta(minutes=5)

## Ban / Mute settings
#
BAN_ANNOUNCE = True
BANTIME_MIN = 5
BANTIME_MAX = 60
BANTIME_INITIAL = 15

## List of domains to not accept email registration from
#BAD_EMAIL_DOMAINS = []


# demosauce scan requires this. terra said there were problems...
# but when I tested it I didn't see any
# in django it looks like that: if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = -1

from settings_local import *

try:
    modify_globals(globals())
except:
    pass
