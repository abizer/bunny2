import sqlite3

# Establish a connection to the SQLite database
connection = sqlite3.connect('db/urls.db')
cursor = connection.cursor()


# Function to lookup a URL for a given slug from the database
def lookup_url_for_slug(slug: str) -> str:
    cursor.execute("SELECT url FROM urls WHERE slug=?", (slug,))
    result = cursor.fetchone()

    # If a result is found, return the URL, else return None
    return result[0] if result else None

# Function to update the URL for a given slug in the database
def update_url_for_slug(slug: str, url: str) -> None:
    cursor.execute("INSERT OR REPLACE INTO urls (slug, url) VALUES (?, ?)", (slug, url))

    # Commit the changes and close the connection to the database
    connection.commit()

def list_all(n: int = 100):
    cursor.execute("SELECT slug, url FROM urls LIMIT ?", (n,))
    result = cursor.fetchall()

    return result

# Be sure to close the connection to the database when the script finishes executing
import atexit
atexit.register(lambda: connection.close())
