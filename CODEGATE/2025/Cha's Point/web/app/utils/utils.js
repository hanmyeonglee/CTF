const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { decode } = require("html-entities");

const FILTER = /\'|`|\.\.|\.\/|#|%|&|\?|<|>|\(|\)|script|onerror|src|\n/i;
const UPLOAD_DIR = "/app/uploads/";

const TEMPLATE = `---
title: "{TITLE}"
theme: {THEME}
highlightTheme: {HIGHLIGHT}
---`;

const default_template = `# Slide 1

* Item 1
* Item 2
* Item 3

---

# Slide 2

Lorem ipsum.

---

# Slide 3

Lorem _ipsum_.`;

const encode = (text) => {
    try {
        return encodeURI(text.replace(/"/g, ""));
    } catch {
        return text;
    }
};

const sha256hash = (text) => {
    return crypto.createHash("sha256").update(text).digest("hex");
};

const read_config = (uuid) => {
    const configPath = path.join(UPLOAD_DIR, uuid, "config", "config.md");
    if (!fs.existsSync(configPath)) {
        return {};
    }
    const data = fs.readFileSync(configPath, "utf8");
    const lines = data.split("\n");
    return {
        title: decode(lines[1].slice(8, -1)),
        theme: decode(lines[2].slice(7)),
        highlightTheme: decode(lines[3].slice(16))
    };
};

const set_config = (uuid, title, theme, highlightTheme) => {
    const userDir = path.join(UPLOAD_DIR, uuid);
    const requiredFolders = ["config", "slide"];
    if (!fs.existsSync(userDir)) {
        fs.mkdirSync(userDir, { recursive: true });
    }
    requiredFolders.forEach((folder) => {
        const folderPath = path.join(userDir, folder);
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath);
        }
    });
    const configPath = path.join(userDir, "config", "config.md");
    try {
        const content = TEMPLATE.replace("{TITLE}", encode(title))
            .replace("{THEME}", encode(theme))
            .replace("{HIGHLIGHT}", encode(highlightTheme));
        fs.writeFileSync(configPath, content);
    } catch {}
    return fs.existsSync(configPath);
};

module.exports = {
    FILTER,
    sha256hash,
    set_config,
    read_config,
    default_template,
    UPLOAD_DIR
};
