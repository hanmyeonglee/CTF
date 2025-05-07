const router = require("express").Router();
const { read_config, set_config, default_template, UPLOAD_DIR } = require("../utils/utils");
const fs = require("fs");
const path = require("path");

router.get("/", (req, res) => res.render("add"));

router.get("/edit", (req, res) => {
    const userDir = path.join(UPLOAD_DIR, req.session.userid);
    if (!fs.existsSync(userDir)) {
        return res.redirect("/");
    }
    const config = read_config(req.session.userid);
    const slidePath = path.join(userDir, "slide", "default.md");
    const data = fs.existsSync(slidePath) ? fs.readFileSync(slidePath, "utf8").toString() : default_template;
    return res.render("edit", { userId: req.session.userid, data, config });
});

router.post("/edit", (req, res) => {
    const userDir = path.join(UPLOAD_DIR, req.session.userid);
    if (!fs.existsSync(userDir)) {
        return res.redirect("/");
    }
    try {
        fs.writeFileSync(path.join(userDir, "slide", "default.md"), req.body.markdown);
    } catch {
        return res.render("edit", { error: "error" });
    }
    return res.redirect("/view/render");
});

router.post("/edit/add/config", (req, res) => {
    const { title, theme, highlightTheme } = req.body;
    if (typeof title !== "string" || typeof theme !== "string" || typeof highlightTheme !== "string") {
        return res.json({ status: "error" });
    }
    return res.json({ status: set_config(req.session.userid, title, theme, highlightTheme) ? "success" : "error" });
});

router.post("/edit/add/theme", async (req, res) => {
    let url;
    try {
        url = new URL(req.body.url);
    } catch {
        return res.json({ status: "error" });
    }

    const url_ = url.origin + url.pathname;
    const config = read_config(req.session.userid);
    if (!config.title) {
        return res.json({ status: "error" });
    }

    if (!url_.startsWith("https://") && !url_.startsWith("http://")) {
        return res.json({ status: "error" });
    }

    const userDir = path.join(UPLOAD_DIR, req.session.userid);
    const themeDir = path.join(userDir, "_" + path.basename(path.normalize(url_)));

    if (!fs.existsSync(themeDir)) fs.mkdirSync(themeDir, { recursive: true });
    try {
        const response = await fetch(url_);
        const themeData = await response.text();
        fs.writeFileSync(path.join(themeDir, "style.css"), themeData);
        set_config(
            req.session.userid,
            config.title,
            req.session.userid + "/style/_" + path.basename(path.normalize(url_)),
            config.highlightTheme
        );
        return res.json({ status: "success" });
    } catch {
        fs.rmdirSync(themeDir, { recursive: true, force: true });
        return res.json({ status: "error" });
    }
});

router.delete("/edit/del/theme", (req, res) => {
    const config = read_config(req.session.userid);
    const delPath = path.join(UPLOAD_DIR, path.dirname(path.dirname(config.theme)), path.basename(config.theme));
    if (config.theme && fs.existsSync(delPath)) {
        fs.rmdirSync(delPath, { recursive: true, force: true });
        set_config(req.session.userid, config.title, "black", config.highlightTheme);
        return res.json({ status: "success" });
    }
    return res.json({ status: "error" });
});

router.post("/edit/add/highlight", async (req, res) => {
    let url;
    try {
        url = new URL(req.body.url);
    } catch {
        return res.json({ status: "error" });
    }

    const url_ = url.origin + url.pathname;
    const config = read_config(req.session.userid);

    if (!config.title) {
        return res.json({ status: "error" });
    }
    if (!url_.startsWith("https://") && !url_.startsWith("http://")) {
        return res.json({ status: "error" });
    }

    const userDir = path.join(UPLOAD_DIR, req.session.userid);
    const highlightDir = path.join(userDir, "_" + path.basename(path.normalize(url_)));

    if (!fs.existsSync(highlightDir)) {
        fs.mkdirSync(highlightDir, { recursive: true });
    }
    try {
        const response = await fetch(url_);
        const themeData = await response.text();
        fs.writeFileSync(path.join(highlightDir, "highlight.css"), themeData);
        set_config(
            req.session.userid,
            config.title,
            config.theme,
            req.session.userid + "/highlight/_" + path.basename(path.normalize(url_))
        );
        return res.json({ status: "success" });
    } catch {
        fs.rmdirSync(highlightDir, { recursive: true, force: true });
        return res.json({ status: "error" });
    }
});

router.delete("/edit/del/highlight", (req, res) => {
    const config = read_config(req.session.userid);
    const delPath = path.join(UPLOAD_DIR, path.dirname(path.dirname(config.highlightTheme)), path.basename(config.highlightTheme));
    if (config.highlightTheme && fs.existsSync(delPath)) {
        fs.rmdirSync(delPath, { recursive: true, force: true });
        set_config(req.session.userid, config.title, config.theme, "zenburn");
        return res.json({ status: "success" });
    }
    return res.json({ status: "error" });
});

module.exports = router;