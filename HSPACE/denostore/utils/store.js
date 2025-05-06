import kv from "./db.js";
import { getUser } from "./auth.js";

export const STORE_LIST = [
    { "name": "Apple", "price": 100 },
    { "name": "Banana", "price": 50 },
    { "name": "Cherry", "price": 200 },
    { "name": "Durian", "price": 500 },
    { "name": "Elderberry", "price": 1000 },
    { "name": "Fig", "price": 2000 },
    { "name": "Flag", "price": 100000 },
];

export function initStore(username) {
    const store = {};
    STORE_LIST.forEach((item) => {
        store[item.name] = 0;
    });
    kv.set(["store", username], store);
}

export async function getStore(username) {
    return await kv.get(["store", username]);
}

export async function buyItem(username, item, quantity) {
    const user = (await getUser(username)).value;
    const store = (await getStore(username)).value;
    const itemPrice = STORE_LIST.find((i) => i.name === item).price;

    if (!store[item]) {
        store[item] = 0;
    }

    if (user.balance < itemPrice * quantity) {
        throw new Error("Not enough balance");
    }

    store[item] += parseInt(quantity);
    user.balance -= itemPrice * parseInt(quantity);

    await kv.set(["store", username], store);
    await kv.set(["users", username], user);
}

export async function sellItem(username, item, quantity) {
    const user = (await getUser(username)).value;
    const store = (await getStore(username)).value;
    const itemPrice = STORE_LIST.find((i) => i.name === item).price;

    if (!store[item] || store[item] < quantity) {
        throw new Error("Not enough items");
    }

    store[item] -= parseInt(quantity);
    user.balance += itemPrice * parseInt(quantity);

    await kv.set(["users", username], user);
    await kv.set(["store", username], store);
}
