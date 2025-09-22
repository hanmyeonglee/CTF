const express = require('express');
const { execFile } = require('child_process');


const redis = require('redis');
const app = express();
const port = 3001;


FLAG = process.env.FLAG || 'poka{test_flag}';

async function getUrlStatusCode(_url) {
    return new Promise((resolve, reject) => {
        if (_url.toLowerCase().startsWith("file")) {
            reject(new Error("Protocol not allowed"));
            return;
        }

        execFile("curl", ["-w", "%{http_code}", "-o", "/dev/null", "-I", "-L", _url], (error, stdout, stderr) => {
            if (error) {
                reject(error);
                return;
            }

            const result = stdout;
            resolve(result);
        });
    });
}

const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://redis:6379'
});

redisClient.on('error', (err) => {
    console.error('Redis error:', err);
});

app.get('/', (req, res) => {
    res.send('Hello World');
});

app.get('/set', async (req, res) => {
    const { key, value } = req.query;
    if (key.toLowerCase().includes('apple') || key.toLowerCase().includes('banana') || key.toLowerCase().includes('locked')) {
        return res.send('Not allowed');
    }
    try {
        await redisClient.set(key, value);
    } catch (error) {
        res.send(error.message);
    }
    res.send('OK');
});

app.get('/get', async (req, res) => {
    
    const { key } = req.query;
    try {
        const data = await redisClient.get(key);
        res.send(data);
    } catch (error) {
        res.send(error.message);
    }
});

app.get('/check', (req, res) => {
    const url = req.query.url;
    getUrlStatusCode(url)
        .then(data => {
            res.send(data);
        })
        .catch(error => {
            res.send('error');
        });
});

app.get('/flag', async (req, res) => {
    try {
        const { username } = req.query;

        await redisClient.set(`${username}_locked`, 'true');

        const apple = await redisClient.get(`${username}_apple`);

        if (apple !== 'apple') {
            return res.send('not apple');
        }

        const banana = await redisClient.get(`${username}_banana`);

        if (atob(banana) !== 'banana') {
            return res.send('not banana');
        }

        if (await redisClient.get(`${username}_locked`) === 'true') {
            return res.send('locked');
        }

        res.send(FLAG);
    } catch (error) {
        res.send(error.message);
    }
});


app.listen(port, async () => {
    await redisClient.connect();
    console.log(`Server is running on port ${port}`);
});