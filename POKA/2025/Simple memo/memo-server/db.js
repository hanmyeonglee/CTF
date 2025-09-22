const mysql = require('mysql2/promise');

const dbConfig = {
  host: process.env.DB_HOST || 'db',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '1234',
  database: process.env.DB_NAME || 'memodb',
  port: process.env.DB_PORT || 3306
};

async function getConnection() {
  return await mysql.createConnection(dbConfig);
}

module.exports = { getConnection };