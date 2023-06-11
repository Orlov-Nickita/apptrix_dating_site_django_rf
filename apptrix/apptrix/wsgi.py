# -*- coding: utf-8 -*-
import platform
import environ
import sys
import os

env = environ.Env()
environ.Env.read_env()

sys.path.insert(0, '/home/c/cq67819/django/public_html/apptrix')
sys.path.insert(0, '/home/c/cq67819/django/public_html/apptrix/apptrix')
sys.path.insert(0, '/home/c/cq67819/django/venv/lib/python{0}/site-packages'.format(platform.python_version()[0:3]))

os.environ["DJANGO_SETTINGS_MODULE"] = "apptrix.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
