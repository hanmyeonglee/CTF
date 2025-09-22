DROP TABLE IF EXISTS memos;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  token VARCHAR(255),
  password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS memos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  memo_id INT,
  title TEXT,
  content TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


/* fake admin token & fake admin password */
INSERT IGNORE INTO users (email, token, password) VALUES ('admin@admin.com', '614ab2525fdfa78a14b62d4f0d5ac88f', '$2b$12$desX6fopB6Njo2.95kn0vOLtlYQnS80excvskvcIwuYqf.6l13FXi'); 