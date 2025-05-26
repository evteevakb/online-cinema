"""
Module to initialize the application with gevent monkey patching.
"""

from gevent import monkey
monkey.patch_all()

from app import app
