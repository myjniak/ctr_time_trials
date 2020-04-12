import logging
from http.client import HTTPConnection
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOGGER.addHandler(ch)
HTTPConnection.debuglevel = 1
