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
    "HOSTS": ['ngsdb'], # List of hosts to deploy to
    "BASE": "/opt", # Absolute remote path for the base dir which holds Django-code and virtual env.
    "VIRTUALENV_HOME":  "/opt/virtualenv/ngsdb", # Absolute remote path for virtualenvs
    "PROJECT_HOME": "/opt/django-sites/ngsdb", # Absolute remote path for django sites
    "PROJECT_NAME": "ngsdb03", # Unique identifier for project
    "REQUIREMENTS_PATH": "requirements/ngsdb.txt", # Path to pip requirements, relative to project
    "GUNICORN_PORT": 8000, # Port gunicorn will listen on
    "GUNICORN_LOGLEVEL":"debug", # Server's log level [debug|error]
    "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
    "LIVE_HOSTNAME": "ngsdb", # Host for public site.
    "REPO_URL": "ssh://git@stash.sbri.org:7999/bifx/ngsdb03.git", # Git or Mercurial remote repo URL for the project
    "DB_PASS": "ngsdb03", # Live database password
    "ADMIN_PASS": "", # Live admin user password
}
