-- Create table `urls` in the SQLite database
CREATE TABLE IF NOT EXISTS urls (
    slug TEXT PRIMARY KEY,
    url TEXT NOT NULL
);