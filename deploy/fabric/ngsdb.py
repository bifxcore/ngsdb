##################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

FABRIC = {
    "SSH_USER": "gramasamy", # SSH username
    "SSH_PASS":  "gramasamy", # SSH password (consider key-based authentication)
    "SSH_USER_GRP": "GHBC-Bifx", # The unix group SSH user belongs to.
    "SSH_KEY_PATH":  "", # Local path to SSH key file, for key-based auth
    "HOSTS": ['ssgcidpws-temp'], # List of hosts to deploy to
    "BASE": "/opt", # Absolute remote path for the base dir which holds Django-code and virtual env.
    "VIRTUALENV_HOME":  "/opt/virtualenv/ssgcidpws-temp", # Absolute remote path for virtualenvs
    "PROJECT_HOME": "/opt/django-sites/ssgcidpws-temp", # Absolute remote path for django sites
    "PROJECT_NAME": "ssgcidpws", # Unique identifier for project
    "REQUIREMENTS_PATH": "requirements/project.txt", # Path to pip requirements, relative to project
    "GUNICORN_PORT": 8000, # Port gunicorn will listen on
    "GUNICORN_LOGLEVEL":"debug", # Server's log level [debug|error]
    "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
    "LIVE_HOSTNAME": "ssgcidpws-temp", # Host for public site.
    "REPO_URL": "gitolite@gitwwwstage.sbri.org:ssgcidpws", # Git or Mercurial remote repo URL for the project
    "DB_PASS": "ssgcidpws123", # Live database password
    "ADMIN_PASS": "", # Live admin user password
}