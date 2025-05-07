const express = require('express');
const path = require('path');
const router = express.Router();
const { authenticateJWT } = require('../utils/jwt');
const { setRole } = require('../models/userModel');

router.get('/', authenticateJWT, (req, res) => {
    res.render('user/index', {
        uuid: req.user.uuid,
        role: req.user.role
    })
});

router.post('/role', authenticateJWT, (req, res) => {
    const { role } = req.body;

    const token = setRole(req.user.uuid, role);
    if (!token) return res.status(400).json({ message: "Invalid Role." });

    res.json({ message: "Role Changed.", token });
});

module.exports = router;