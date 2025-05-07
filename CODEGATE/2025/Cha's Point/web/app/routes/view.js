const router = require("express").Router();
const fs = require("fs");
const path = require("path");
const child_proces = require("child_process");
const { default_template, UPLOAD_DIR } = require("../utils/utils");
const { DB } = require("../utils/db.js") ;

let revealmd = null;

async function getRevealMd() {
    if (!revealmd) {
        revealmd = await import("reveal-md/lib/render.js");
    }
    return revealmd;
}

router.get("/render", async (req, res) => {
    try {
        const userId = req.session.userid;
        const configPath = path.join(UPLOAD_DIR, userId, "config", "config.md");

        if (!fs.existsSync(configPath)) {
            return res.redirect("/");
        }

        const slidePath = path.join(UPLOAD_DIR, userId, "slide", "default.md");
        const useTemplate = !fs.existsSync(slidePath);

        const configData = fs.readFileSync(configPath, "utf8").toString();
        let data = configData;
        if (useTemplate) {
            data += default_template;
        } else {
            data += fs.readFileSync(slidePath, "utf8").toString();
        }

        const { render } = await getRevealMd();
        const rendered = await render(data);
        return res.send(rendered);
    } catch {
        return res.status(500).send("Error");
    }
});

router.get("/render/PDF", async (req, res) => {
    const conn = new DB();
    const userId = req.query.uuid;
    const option = req.query.option ? req.query.option : {};
    console.log(req.query.option);
    console.log(option.admin);
    const outputFileName = !/'|;|&|\|"|\$|\s/.test(req.query.outputFileName) ? req.query.outputFileName : "output.pdf";

    /* if (req.ip !== '::ffff:127.0.0.1' && req.ip !== '::1' && req.ip !== '127.0.0.1') {
        return res.status(403).send("Not Allowed Ip"); 
    } */

    try {
        const result = await conn.query("SELECT * FROM users WHERE username = 'admin'", []);
        if (userId !== result[0].uid) {
            return res.status(403).send("You are not Admin");
        }
    } catch (err) {
        return res.status(500).send("Error");
    }

    const configPath = path.join(UPLOAD_DIR, userId, "config", "config.md");
    if (!fs.existsSync(configPath)) {
        fs.mkdirSync(path.join(UPLOAD_DIR, userId, "config"), { recursive: true });
        fs.writeFileSync(configPath, '');
    }

    const slidePath = path.join(UPLOAD_DIR, userId, "slide", "default.md");
    const useTemplate = !fs.existsSync(slidePath);

    const configData = fs.readFileSync(configPath, "utf8").toString();
    let data = configData;
    if (useTemplate) {
        data += default_template;
    } else {
        data += fs.readFileSync(slidePath, "utf8").toString();
    }

    if (!fs.existsSync(path.join(UPLOAD_DIR, userId, "target"))) {
        fs.mkdirSync(path.join(UPLOAD_DIR, userId, "target"));
    }

    const { render } = await getRevealMd();
    console.log('rendering...')
    try {
        const rendered = await render(data, option);
        console.log(rendered)
        return res.send(rendered);
    } catch(err) {
        console.log(err);
        return res.status(500).send("Error");
    }
});

router.get("/:file", (req, res) => {
    const requestedFile = req.params.file;
    const highlightStylesPath = path.resolve(
        require.resolve("highlight.js"),
        "..",
        "..",
        "styles",
        requestedFile
    );
    const highlightBase16Path = path.resolve(
        require.resolve("highlight.js"),
        "..",
        "..",
        "styles",
        "base16",
        requestedFile
    );
    const revealThemePath = path.join(
        path.dirname(require.resolve("reveal.js")),
        "..",
        "dist",
        "theme",
        requestedFile
    );

    console.log('highlightStylesPath', highlightStylesPath);
    console.log('highlightBase16Path', highlightBase16Path);
    console.log('revealThemePath', revealThemePath);

    if (fs.existsSync(highlightStylesPath)) {
        return res.sendFile(highlightStylesPath);
    } else if (fs.existsSync(highlightBase16Path)) {
        return res.sendFile(highlightBase16Path);
    } else {
        return res.sendFile(revealThemePath);
    }
});

router.get("/:uuid/:style/:file", (req, res) => {
    const { uuid, style, file } = req.params;
    const check = !req.query.preview;

    let cssPath;

    if (style === "highlight") {
        if (check) {
            cssPath = path.join(
                UPLOAD_DIR,
                uuid,
                file.slice(0, -4),
                style + ".css"
            );
        } else {
            cssPath = path.join(UPLOAD_DIR, uuid, file, style + ".css");
        }
    } else if (style === "style") {
        cssPath = path.join(UPLOAD_DIR, uuid, file, style + ".css");
    } else {
        return res.status(404).send("Not Found");
    }

    if (!fs.existsSync(cssPath)) {
        return res.status(404).send("Not Found");
    }
    return res.sendFile(cssPath);
});

module.exports = router;
