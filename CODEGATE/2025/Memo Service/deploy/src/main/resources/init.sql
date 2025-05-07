CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE memos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

INSERT INTO users (username, password) VALUES ('admin', '5e329c21d96697aa7ce4a3f2a68c7a80453040945d8c5e8ab87a570f7056202b');
INSERT INTO memos (owner, title, content) VALUES (1, "hello", "world");