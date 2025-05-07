const express = require('express');
const router = express.Router();
const { addUser, getUser } = require('../models/userModel');
const { generateToken } = require('../utils/jwt');


router.get('/login', (req, res) => {
    res.render('auth/login');
});

router.post('/login', (req, res) => {
    const { uuid, password } = req.body;
    const user = getUser(uuid);

    if (!user || user.password !== password) return res.status(403).json({ message: "Invalid credentials." });
    if (user.role === "BANNED") return res.status(403).json({ message: "You have been BANNED." });

    const payload = { uuid, ...user };
    delete payload.password;

    const token = generateToken(payload);
    res.json({ message: "Logged in successfully", token });
});

router.get('/register', (req, res) => {
    res.render('auth/register');
});

router.post('/register', (req, res) => {
    const { password } = req.body;

    if (!password) {
        return res.status(401).json({ message: "Please enter password." });
    }

    const uuid = addUser(password);
    res.status(200).json({ message: "User registered successfully", uuid: uuid });
});

module.exports = router;