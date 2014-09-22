import os
import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType
# General Django settings for ngsdb03 project.
# For host specific settings see corresponding files
# for example for ngsdb host see ngsdb03.settings.ngsdb

#This is for adding additional attributes to built-in Users from Django
#this enables the get_profile() command for Users
AUTH_PROFILE_MODULE = 'ngsdbview.UserProfile'
LOGIN_URL = '/admin/'
LOGIN_REDIRECT_URL = '/ngsdbview/dashboard/'

GRAPPELLI_ADMIN_TITLE='NGSDB03: Myler Lab NGS database'

ADMINS = (
    ('Gowthaman Ramasamy', 'ragowthaman@gmail.com'),
    ('Marea Cobb', 'marea.cobb@seattlebiomed.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# The absolute path to the project directory.
PROJECT_DIR = os.path.dirname(__file__)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = 'media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
    os.path.join(os.path.dirname(__file__), 'static'),
    # os.path.join(os.path.dirname(__file__))
    # "/Users/gramasamy/djcode/ngsdb03/static",
    # "/opt/django-sites/ngsdb/ngsdb03/static",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
#read via env variable in host specific settings file eg ngsdb.settings.ngsdb
#SECRET_KEY = ''


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_tables2_reports.middleware.TableReportMiddleware',
)

ROOT_URLCONF = 'ngsdb03.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ngsdb03.wsgi.application'

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'templates')),
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../ngsdbview', 'templates')),

    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'django_tables2_reports',
    'grappelli',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'south',
    'ngsdbview',
    'samples',
    'snpdb',
    'django.contrib.humanize',
    'mathfilters',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}


# Gowthaman : Following was adopted from 2scopes of django to
# avoid possible path related uninformative complains from django
# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.

from django.core.exceptions import ImproperlyConfigured
def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)



# django_table2_reports
EXCEL_SUPPORT = 'xlwt'

# LDAP authentication
import logging

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://ds.sbri.org"


AUTH_LDAP_BIND_DN = "AD Lookup"
AUTH_LDAP_BIND_PASSWORD = "pass123"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users,ou=SBRI,dc=sbri,dc=org",
                                   ldap.SCOPE_SUBTREE, "(mailNickname=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=Security Groups,ou=SBRI,dc=sbri,dc=org",
                                    ldap.SCOPE_SUBTREE, "(objectClass=group)")
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType(name_attr="cn")

# Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
# AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=Myler Lab,ou=Security Groups,ou=SBRI,dc=sbri,dc=org",
    "is_staff": "cn=Myler Lab,ou=Security Groups,ou=SBRI,dc=sbri,dc=org",
    "is_superuser": "cn=Myler Lab,ou=Security Groups,OU=SBRI,DC=sbri,DC=org",

    #"is_active": "cn=GHBC-Bifx,ou=Security Groups,ou=SBRI,dc=sbri,dc=org",
    #"is_staff": "cn=GHBC-Bifx,ou=Security Groups,ou=SBRI,dc=sbri,dc=org",
    #"is_superuser": "cn=GHBC-Bifx,ou=Security Groups,OU=SBRI,DC=sbri,DC=org",
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600



# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
