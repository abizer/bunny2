import importlib
import os
import re

import logging

logger = logging.getLogger(__name__)

plugin_registry = {}

def load_plugins(src="plugins"):
    for filename in os.listdir(src):
        if filename.endswith(".py") and not filename.startswith(".") and not filename.startswith("_"):
            module = f"{src}.{filename[:-3]}" # strip .py
            logger.debug(f"importing {module}")
            plugin = importlib.import_module(module)
        

def register(pattern):
    def wrapper(fn):
        name = '.'.join((fn.__module__, fn.__name__))
        print(f"registering {name} under {pattern}")
        fn.pattern = pattern
        plugin_registry[name] = (re.compile(pattern), fn)
    return wrapper
    
