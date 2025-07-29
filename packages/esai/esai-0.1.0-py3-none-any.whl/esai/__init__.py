import logging

from .app import Application

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler)