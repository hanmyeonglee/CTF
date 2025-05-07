const jwt = require('jsonwebtoken');
require('dotenv').config();

const secretKey = process.env.SECRET_KEY;

const generateToken = (payload) => {
    return jwt.sign(payload, secretKey, { expiresIn: '1h' });
};

const authenticateJWT = (req, res, next) => {
    const token = req.cookies?.jwt;

    if (!token) return res.status(401).json({ message: 'Unauthorized' });

    jwt.verify(token, secretKey, (err, user) => {
        if (err) return res.status(403).json({ message: 'Forbidden' });

        req.user = user;
        next();
    });
};

module.exports = { authenticateJWT, generateToken };