from . import Redirect, register, Action, Payload, Lookup

@register(r"^h ?(?P<idx>\d+)")
def hobby(dispatcher, payload: Payload, idx: int) -> Action:
    return Lookup(f"hobby/{idx}")

@register(r"^w (?P<query>.*)")
def wikipedia(dispatcher, payload: Payload, query: str) -> Action:
    return Redirect(f"https://en.wikipedia.org/w/index.php?search={query}")

@register(r"^g (?P<query>.*)")
def google(dispatcher, payload: Payload, query: str) -> Action:
    return Redirect(f"https://www.google.com/search?q={query}")

@register(r"^(?:ai|chat) ?")
def chatgpt(dispatcher, payload: Payload) -> Action:
    return Redirect("https://chat.openai.com/")

@register(r"c(?:al)? ?(?P<idx>\d)?")
def cal(dispatcher, payload: Payload, idx: int = 0) -> Action:
    return Redirect(f"https://calendar.google.com/calendar/u/{idx}/r")