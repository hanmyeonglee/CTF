import kv from "./db.js";
import { merge, sha256 } from "./util.js";

export async function loginUser(username, password) {
  const user = await kv.get(["users", username]);
  if (user.value && user.value.password === await sha256(password)) {
    return user;
  } else {
    return null;
  }
}

export async function getUser(username) {
  return await kv.get(["users", username]);
}

export async function createUser(username, password) {
  const hashedPassword = await sha256(password);
  console.log(hashedPassword);

  if (username === "admin") {
    throw new Error("Invalid username");
  }

  const user = {
    username,
    password: hashedPassword,
    isAdmin: false,
    balance: 10000,
  };

  await kv.set(["users", username], user);
}

export async function checkAdmin(username) {
  const user = await kv.get(["users", username]);
  if (user.username === "admin") {
    await kv.set(["users", username], merge(user, { isAdmin: true }));
  }
}
