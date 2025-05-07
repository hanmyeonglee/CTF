const express = require('express');
const router = express.Router();
const { authenticateJWT } = require('../utils/jwt');
const { adminGuard } = require('../utils/guard');
const { getUser, setPerm } = require('../models/userModel');

router.use(authenticateJWT);
router.use(adminGuard);

router.get('/', (req, res) => {
    res.render('admin/index', {
        uuid: req.user.uuid,
        role: req.user.role
    });
});

// TODO : Testing HTML tag functionality for the "/post".
router.get('/test', (req, res) => {
    res.render('admin/test');
});

router.get('/user', (req, res) => {
    res.render('admin/user');
});

router.post('/user/perm', (req, res) => {
    const { uuid, value } = req.body;

    const user = getUser(uuid);

    if (!user) return res.status(404).json({ message: "User Not Found." });
    if (typeof (value) !== "boolean") return res.status(401).json({ message: "Invalid Permission Status. Please use boolean." });

    setPerm(uuid, value)

    res.json({ message: "User Permission Changed." })
});

module.exports = router;