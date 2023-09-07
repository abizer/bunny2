import sqlite3

connection = sqlite3.connect('db/urls.db')
cursor = connection.cursor()

def lookup_url_for_slug(slug: str) -> str:
    cursor.execute("SELECT url FROM urls WHERE slug=?", (slug,))
    result = cursor.fetchone()

    return result[0] if result else None

def update_url_for_slug(slug: str, url: str) -> None:
    cursor.execute("INSERT OR REPLACE INTO urls (slug, url) VALUES (?, ?)", (slug, url))

    connection.commit()

def list_all(n: int = 100):
    cursor.execute("SELECT slug, url FROM urls LIMIT ?", (n,))
    result = cursor.fetchall()

    return result

def clear(slug: str):
    cursor.execute("DELETE FROM urls WHERE slug=?", (slug,))
    connection.commit()

# close connections on exit
import atexit
atexit.register(lambda: connection.close())
