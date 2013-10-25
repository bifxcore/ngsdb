import os

bind = "127.0.0.1:%(gunicorn_port)s"
workers = (os.sysconf("SC_NPROCESSORS_ONLN") * 2) + 1
loglevel = "%(gunicorn_loglevel)s"
proc_name = "%(proj_name)s"
user = 'gramasamy'
group = 'GHBC-Bifx'
logfile = "%(proj_home)s/gunicorn_logs/%(proj_name)s.log"
