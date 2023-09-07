# Utility functions for transformations

from typing import List, Any
import re
import random

r_ = re.compile

def patterned_slug(payload: str) -> str:
    hex32 = f"{random.getrandbits(32):08X}"
    
    gdrive_re = re.compile(r'^https://(docs|drive|slides|sheets).google.com/.+')
    if gdrive_re.match(payload):
        return f"/g/{hex32}"

    # default create shorturls in the /s/ namespace
    return f"/s/{hex32}"
        
def check_alias(alias):
    # in the future check if this is valid
    return alias

plugins = {
    'hobby':  (r_(r'^h ?(?P<idx>\d+)'),
     lambda _, p, idx: f'/hobby/{idx}'),
    'shorten': (r_(r'^shorten'),
                lambda _, payload: patterned_slug(payload)),
    'alias': (r_(r'^(?:a|alias)/(?P<alias>\w+)'),
              lambda _, payload, alias: check_alias(alias)),
    # default case
    'reflection': (r_(r'(?P<slug>.+)'), lambda _, p, slug: slug)
}

class path_dispatcher:
    def _dispatch(self, processors: List[Any], path: str, payload: bytes):
        # first regex processors
        for name, (pattern, fn) in processors.items():
            found = pattern.match(path)
            if found:
                print(f"dispatching to {name}")
                return fn(self, payload, *found.groups())        

    def run(self, path: str, payload: bytes):
        return self._dispatch(plugins, path, payload)

def transform_path_to_slug(path: str, payload: bytes = None) -> str:
    """
    Converts the given path to a slug that can be looked up in the database.
    To maintain consistency, the same function is used on both read and write paths.
    On the write path, the additional context from the payload may be used for deriving
      new slugs on known patterns.
    
    default behavior is that the request path is the slug
    transform_path_to_slug("exploring") -> "exploring"

    slugs can be aliased to other slugs 
    transform_path_to_slug("h5") -> "/hobby/5"

    can implement a pattern-based shorturl generator
    transform_path_to_slug("shorturl", "https://docs.google.com/...") -> "/g/ef45gh"

    do arbitrary work, like curl-able pastebin
    transform_path_to_slug("paste", <file contents>) -> "/p/abd4f5b32"
    transform_path_to_slug("pasted/debuglogs", <file contents>) -> "/p/20230823/debuglogs"

    it's expected that the single argument call produces only readable slugs and the
    double argument call produces only writable slugs
    """

    return path_dispatcher().run(path, payload)
    


def transform_payload_to_url(payload: bytes) -> str:
    """
    Converts the given payload to a URL.
    As per the current plan, it returns the payload as is.
    
    Args:
    payload (str): The payload to be transformed.
    
    Returns:
    str: The transformed URL.
    """
    is_url = payload[:4] == b"http"

    if is_url:
        return bytes.decode(payload).strip()
    
