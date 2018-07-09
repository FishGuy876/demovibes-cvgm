import os

LOG_ROOT = os.path.dirname(os.path.realpath(__file__))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | %(process)d | %(levelname)7s | %(name)20s:%(lineno)-4d | %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'file': {
            'level': "DEBUG",
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_ROOT, 'demovibes.log'),
            'maxBytes': 5 * 1024 ** 2,
            'backupCount': 0,
            'encoding': "utf8",
            'formatter': 'verbose'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'dv': {
            'handlers': ["file"],
            'level': "DEBUG",
        }
    }
}
