const express = require("express");
const session = require("express-session");
const crypto = require("crypto");
const path = require("path");
const { rateLimit } = require('express-rate-limit')

const { FILTER } = require("./utils/utils");
const { encode } = require("html-entities");

const auth = require("./routes/auth");
const edit = require("./routes/edit");
const view = require("./routes/view");

const app = express();

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(express.static("public"));
app.use("/plugin", express.static("plugin"));
app.use("/dist", express.static("dist"));
app.use(
    "/mermaid",
    express.static(path.join(path.dirname(require.resolve("mermaid")), ".."))
);

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(
    session({
        secret: crypto.randomBytes(32).toString("hex"),
        resave: false,
        saveUninitialized: true,
    })
);

const limiter = rateLimit({
    windowMs:  60 * 1000,
    max: 30,
    standardHeaders: 'draft-8',
    legacyHeaders: false,
});
app.use(limiter);

app.use((req, res, next) => {
    if (req.session.userid || req.path.startsWith("/auth/")) return next();
    return res.redirect("/auth/login");
});

app.use((req, res, next) => {
    if (req.method === "POST") {
        for (const key in req.body) {
            if (req.body[key] && typeof req.body[key] !== "string") {
                return res.status(401).send("Invalid Data");
            }
            if (FILTER.exec(req.body[key])) {
                req.body[key] = encode(req.body[key], { mode: "extensive" });
            }
        }
    }
    next();
});

app.use("/auth", auth);
app.use(["/view", "/_assets", "/css/highlight"], view);
app.use(edit);

process.on('uncaughtException', (err) => {
    console.error('Unhandled Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`[+] Start on port ${PORT}`);
});
