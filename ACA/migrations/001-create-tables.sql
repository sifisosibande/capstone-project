CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    email TEXT,
    verification_token TEXT,
    email_verified INTEGER DEFAULT 0
);
