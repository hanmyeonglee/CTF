import { Hono } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import {
    CookieStore,
    Session,
    sessionMiddleware,
} from "https://deno.land/x/hono_sessions/mod.ts";
import { DenoKvStore } from "https://deno.land/x/hono_sessions/src/store/deno/DenoKvStore.ts";
import { checkAdmin, createUser, getUser, loginUser } from "./utils/auth.js";
import {
    buyItem,
    getStore,
    initStore,
    sellItem,
    STORE_LIST,
} from "./utils/store.js";

const app = new Hono();

const kv = await Deno.openKv("./db");
const store = new DenoKvStore(kv);

app.use(
    "*",
    sessionMiddleware({
        store: store,
        encryptionKey: Deno.env.get("SECRET_KEY"),
        cookieOptions: { httpOnly: true, sameSite: "Lax", path: "/" },
    }),
);

app.get("/", (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (username) {
        return c.text(`Hello ${username}!`);
    }

    return c.text("Hello Hono!");
});

app.post("/login", async (c) => {
    const session = c.get("session");
    const sess_username = session.get("username");

    if (sess_username) {
        return c.text(`You are already logged in as ${sess_username}`);
    }

    const { username, password } = await c.req.parseBody();
    console.log(username, password);

    try {
        const user = await loginUser(username, password);
        if (user) {
            session.set("username", username);
            return c.json(user);
        }
    } catch (e) {
        return c.text(e.message);
    }

    return c.text("Invalid login");
});

app.post("/logout", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (!username) {
        return c.text("You are not logged in");
    }
    session.delete("username");
    return c.text("Logged out");
});

app.post("/register", async (c) => {
    const { username, password } = await c.req.parseBody();

    if (!username || !password) {
        return c.text("Invalid username or password");
    }

    // check if user already exists
    const _user = await getUser(username);
    console.log(_user.value !== null);
    if (_user.value !== null) {
        return c.text("User already exists");
    }

    try {
        await createUser(username, password);
    } catch (e) {
        return c.text(e.message);
    }

    initStore(username);

    const session = c.get("session");
    session.set("username", username);
    return c.text("User created");
});

app.get("/store", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (!username) {
        return c.text("You are not logged in");
    }

    const user = await getUser(username);
    const store = await getStore(username);
    return c.json({ user, store });
});

app.get("/store/list", async (c) => {
    return c.json(STORE_LIST);
});

app.post("/store/buy", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (!username) {
        return c.text("You are not logged in");
    }

    const { item, quantity } = await c.req.parseBody();

    try {
        await buyItem(username, item, quantity);
    } catch (e) {
        return c.text(e.message);
    }

    return c.text("Item bought");
});

app.post("/store/sell", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (!username) {
        return c.text("You are not logged in");
    }

    const { item, quantity } = await c.req.parseBody();

    try {
        await sellItem(username, item, quantity);
    } catch (e) {
        return c.text(e.message);
    }

    return c.text("Item sold");
});

app.get("/flag", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    if (!username) {
        return c.text("You are not logged in");
    }

    const store = await getStore(username);

    if (store.value["Flag"] > 0) {
        const flag = Deno.env.get("FLAG");
        return c.text(flag);
    }

    return c.text("You are not authorized to view the flag");
});

app.get("/readfile", async (c) => {
    const session = c.get("session");
    const username = session.get("username");

    const filepath = c.req.query("file");

    if (!username) {
        return c.text("You are not logged in");
    }

    if (!filepath) {
        return c.text("Invalid file path");
    }

    const user = await getUser(username);
    if (user.value.balance < 1000000) {
        return c.text("Not enough balance");
    }

    const file = Deno.readTextFileSync(filepath);
    return c.text(file);
});

Deno.serve(app.fetch);
