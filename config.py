import os

HOST = 'localhost'
PORT = 80
DEBUG = True

basedir = os.path.abspath(os.path.dirname(__name__))
REPOS_DIR = os.path.join(basedir, 'repos')

CLONE_TIMEOUT = 60