from bunny2.plugins import register

# reflection can be implemented this way but
# it's cleaner to special case it in the dispatcher
# rather than try to ensure this module gets loaded last
@register('(?P<slug>.*)')
def reflect(dispatcher, payload, slug: str) -> str:
    return slug
