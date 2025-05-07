const express = require('express');
const router = express.Router();
const { viewUrl } = require('../utils/report');
const { getPostById } = require('../models/postModel');
const { authenticateJWT } = require('../utils/jwt');

router.use(authenticateJWT);

router.get('/:post_id', async (req, res) => {
    const post_id = req.params.post_id;
    const post = getPostById(post_id);

    if (!post) return res.status(404).json({ message: "Post Not Found." });

    let message;
    let code;

    if (req.user.role !== "INSPECTOR") {
        message = "No Permission.";
        code = 403;
    }
    else {
        const result = await viewUrl(post_id);

        message = result ? "Reported." : "Error occurred while check url.";
        code = result ? 200 : 500;
    }

    res.status(code).send(`
        <script nonce="${res.locals.nonce}">
            alert("${message}");
            window.location.href = "/post";
        </script>
    `);
});

module.exports = router;