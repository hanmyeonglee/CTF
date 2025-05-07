const mysql = require("mysql");

class DB {
    constructor() {
        this.conn = mysql.createConnection({
            host: 'db',
            user: 'codegate',
            password: 'codegate',
            database: 'codegate'
        });
    }

    query(query, params=[]) {
        return new Promise((resolve, reject) => {
            this.conn.query(query, params, (err, result) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(result);
                }
            })
        })
    }

    query(query, params=[]) {
        return new Promise((resolve, reject) => {
            this.conn.query(query, params, (err, result) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(result);
                }
            })
        })
    }
}

module.exports={
    DB
}