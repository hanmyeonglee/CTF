const router = require("express").Router();
const { DB } = require("../utils/db");
const { v4: uuidv4 } = require("uuid");
const { sha256hash } = require("../utils/utils");

router.use((req, res, next) => {
    if (req.session.userid) {
        return res.redirect("/");
    }
    next();
});

router.get("/register", (req, res) => res.render("register"));

router.post("/register", async (req, res) => {
    const { username, password } = req.body;
    if (typeof username !== "string" || typeof password !== "string") {
        return res.sendStatus(400);
    }

    const encodedUsername = btoa(username);
    const hashedPassword = sha256hash(password);
    const conn = new DB();

    try {
        await conn.query(
            "INSERT INTO users (uid, username, password) VALUES (?, ?, ?)",
            [uuidv4(), encodedUsername, hashedPassword]
        );
        res.redirect("/auth/login");
    } catch (err) {
        res.render("register", { error: "Registration Failed" });
    }
});

router.get("/login", (req, res) => res.render("login"));

router.post("/login", async (req, res) => {
    const { username, password } = req.body;
    if (typeof username !== "string" || typeof password !== "string") {
        return res.sendStatus(400);
    }

    const conn = new DB();
    try {
        const result = await conn.query("SELECT * FROM users WHERE username = ?", [btoa(username)]);
        const user = result[0];
        if (user && user.password === sha256hash(password)) {
            req.session.userid = user.uid;
            res.redirect("/");
        } else {
            res.render("login", { error: "Invalid username or password" });
        }
    } catch (err) {
        res.render("login", { error: "Invalid username or password" });
    }
});

router.get("/logout", (req, res) => {
    req.session.destroy(() => res.redirect("/"));
});

module.exports = router;
