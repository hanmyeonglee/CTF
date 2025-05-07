const express = require('express');
const router = express.Router();
const { authenticateJWT } = require('../utils/jwt');

router.get('/role', authenticateJWT, (req, res) => {
    return res.status(403).json({ error: `You can't use this function wih your role. ( Your role is ${req.user.role} )` });
});

module.exports = router;