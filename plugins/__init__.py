import importlib
import logging
import os 
import re

logger = logging.getLogger(__name__)

plugin_registry = {}

# load plugins
def load_plugins(src: str = "plugins"):
    for filename in os.listdir(src):
        # deactivate plugins by prepending _ (and ignore __init__.py)
        if filename.endswith(".py") and not filename.startswith(".") and not filename.startswith("_"):            
            # strip .py
            module = f"{src}.{filename[:-3]}" 
            logger.debug(f"importing {module}")
            plugin = importlib.import_module(module)

def register(pattern: str):
    def wrapper(fn):
        name = '.'.join((fn.__module__, fn.__name__))
        logger.info(f"registering {name} under {pattern}")
        plugin_registry[name] = (re.compile(pattern), fn)
    return wrapper