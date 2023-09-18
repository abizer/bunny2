import random
import re 

from . import register

def hex32():
    return f"{random.getrandbits(32):08x}"

def patterned_slug(payload: str) -> str:

    # by default create shorturls in the /s/ namespace
    prefix = 's'
    
    gdrive_re = re.compile(r'^https://(docs|drive|slides|sheets).google.com/.+')
    if gdrive_re.match(payload):
        prefix = 'g'

    
    return f"{prefix}/{hex32()}"

@register(r'^shorten')
def shorten(dispatcher, payload: str) -> str:
    return patterned_slug(payload)
