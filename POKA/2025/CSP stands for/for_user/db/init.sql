CREATE DATABASE IF NOT EXISTS prob_csp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE prob_csp;

CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255),
  password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (username, email, password) VALUES
('admin', 'admin@example.com', '$2b$12$kzpZsGUBuXlKCCagnjJYsusMRB2Dwa7flT4JK2ZoUcO.EishPQKwe');

