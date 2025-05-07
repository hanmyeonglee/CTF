CREATE DATABASE IF NOT EXISTS codegate 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_general_ci;
use codegate;

DROP TABLE IF EXISTS `user`;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(36) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (uid, username, password) VALUES ("00000000-0000-0000-0000-000000000000", "admin", "dcce77b3a8c4a714c76c3c12f8bfb56b431240adc3ec0faf3fd0eead4e7d0cac");