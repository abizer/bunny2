from . import register

@register(r"h ?(?P<idx>\d+)")
def hobby(dispatcher, payload, idx):
    return f"hobby/{idx}"
