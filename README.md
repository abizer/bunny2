# bunny2

inspired by facebook bunnylol, a flexible url shortener and redirector

usage:

either run with uvicorn directly or through docker:

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
docker compose up
```

interact using httpie:

```
$ http :8000/
HTTP/1.1 404 Not Found
content-length: 0
date: Thu, 07 Sep 2023 12:32:59 GMT
server: uvicorn

$ echo "https://ocf.io/abizer" | http -A bearer -a 12345 :8000/
HTTP/1.1 200 OK
content-length: 2
content-type: application/json
date: Thu, 07 Sep 2023 12:33:40 GMT
server: uvicorn

""

$ http :8000/
HTTP/1.1 307 Temporary Redirect
content-length: 0
date: Thu, 07 Sep 2023 12:33:43 GMT
location: https://ocf.io/abizer
server: uvicorn

$ http delete :8000/ -A bearer -a 12345
HTTP/1.1 200 OK
content-length: 0
date: Thu, 07 Sep 2023 12:33:40 GMT
server: uvicorn

""

```

functionality can be added via plugins in the plugins folder.

each plugin is a function. it registers itself to a regex, and receives as 
arguments the dispatcher context, the request payload (if given), and any 
match groups from the regex. the plugin is responsible for converting this
context to a slug that can be looked up in the database. various types
of functionality can be implemented, such as a url shortener.

