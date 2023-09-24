from . import Redirect, register, Action, Payload, Lookup


@register(r"^pypi ?(?P<pkg>\w+)")
def homebrew(dispatcher, payload: Payload, pkg: str) -> Action:
    return Redirect(f"https://pypi.org/project/{pkg}/")


@register(r"^brew ?(?P<pkg>\w+)")
def homebrew(dispatcher, payload: Payload, pkg: str) -> Action:
    return Redirect(f"https://formulae.brew.sh/formula/{pkg}")

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

@register(r"^c(?:al)? ?(?P<idx>\d)?$")
def cal(dispatcher, payload: Payload, idx: int = 0) -> Action:
    return Redirect(f"https://calendar.google.com/calendar/u/{idx}/r")

@register(r"^tw (?P<user>.*)")
def twitter(dispatcher, payload: Payload, user: str) -> Action:
    return Redirect(f"https://twitter.com/{user}")

@register(r"tws (?P<query>.*)")
def twitter_search(dispatcher, payload: Payload, query: str) -> Action:
    return Redirect(f"https://twitter.com/search?q={query}")
    
@register(r"^gh (?P<user>.*)")
def github(dispatcher, payload: Payload, user: str) -> Action:
    return Redirect(f"https://github.com/{user}")

@register(r"^ghm (?P<repo>.*)")
def github_me(dispatcher, payload: Payload, repo: str) -> Action:
    return Redirect(f"https://github.com/abizer/{repo}")
