import sqlite3


class DB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def lookup_url_for_slug(self, slug: str) -> str:
        self.cursor.execute("SELECT url FROM urls WHERE slug=?", (slug,))
        result = self.cursor.fetchone()

        return result[0] if result else None

    def update_url_for_slug(self, slug: str, url: str) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO urls (slug, url) VALUES (?, ?)", (slug, url)
        )
        self.conn.commit()

    def list_all(self, n: int = 100):
        self.cursor.execute("SELECT slug, url FROM urls LIMIT ?", (n,))
        result = self.cursor.fetchall()

        return result

    def clear(self, slug: str):
        self.cursor.execute("DELETE FROM urls WHERE slug=?", (slug,))
        self.conn.commit()
