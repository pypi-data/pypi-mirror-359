import inspect
import os
import sys

from fastapi import APIRouter, FastAPI
from ..app import Application


def create():
    return FastAPI(lifespan=lifespan)

def lifespan(application):
    global INSTANCE

    config = Application.read(os.environ.get("CONFIG"))

    routers = apirouters()

    for name, router in routers.items():
        if name in config:
            application.include_router(router)
    yield

def apirouters():
    api = sys.modules[".".join(__name__.split(".")[:-1])]

    available = {}
    for name, rclass in inspect.getmembers(api, inspect.ismodule):
        if hasattr(rclass, "router") and isinstance(rclass.router, APIRouter):
            available[name.lower()] = rclass.router
        
    return available

def start():
    list(lifespan(app))

app = create()