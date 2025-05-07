const express = require('express');
const router = express.Router();
const { authenticateJWT } = require('../utils/jwt');
const { getPosts, addPost, getPostById, deletePost } = require('../models/postModel');
const { postGuard } = require('../utils/guard');
// const filterRegex = //gi

router.use(authenticateJWT);

router.get('/', (req, res) => {
    const posts = getPosts(req.user);

    res.render('post/index', {
        uuid: req.user.uuid,
        role: req.user.role,
        posts
    });
});

router.get('/write', (req, res) => {
    res.render('post/write', {
        uuid: req.user.uuid,
        role: req.user.role
    });
});

router.post('/write', postGuard, (req, res) => {
    const { title, content } = req.body;

    if (!title || !content) return res.status(400).json({ message: "Please fill title and content." });
    // In the actual code, a SPECIAL filter is prepared for here.
    // if (content.match(filterRegex)) return res.status(403).json({ message: "Hacking Detected!" });

    const post = addPost(req.user, req.body);

    res.json({ message: "Post Saved.", post });
});

router.get('/:post_id', (req, res) => {
    const post = getPostById(req.params.post_id);

    if (!post) return res.status(404).json({ message: "Post Not Found." });

    res.render('post/view', {
        post,
        isInspector: req.user.role === "INSPECTOR" ? true : false,
        isAdmin: req.user.role === "ADMIN" ? true : false,
        isOwner: post.writer === req.body.uuid ? true : false
    });
});

router.get('/delete/:post_id', (req, res) => {
    const result = deletePost(req.params.post_id);

    const message = result ? "Successfully removed." : "Post Not Found.";
    const code = result ? 200 : 404;

    res.status(code).send(`
        <script nonce="${res.locals.nonce}">
            alert("${message}");
            window.location.href = "/post";
        </script>
    `);
});

module.exports = router;