try:
    from .application import app
    from .extension import Extension
    from .routers import *
except ImportError as missing:
    raise ImportError('API is not available - install "api" extra to enable') from missing