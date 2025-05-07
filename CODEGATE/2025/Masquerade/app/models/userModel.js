const { generateToken } = require("../utils/jwt");
const { v4: uuidv4 } = require('uuid');

const users = new Map();

const role_list = ["ADMIN", "MEMBER", "INSPECTOR", "DEV", "BANNED"];

function checkRole(role) {
    const regex = /^(ADMIN|INSPECTOR)$/i;
    return regex.test(role);
}

const addUser = (password) => {
    const uuid = uuidv4()

    users.set(uuid, { password, role: "MEMBER", hasPerm: false });

    return uuid;
};

const getUser = (uuid) => {
    return users.get(uuid);
};

const getUsers = () => {
    console.log(users);
    return 1;
};

const setRole = (uuid, input) => {
    const user = getUser(uuid);

    if (checkRole(input)) return false;
    if (!role_list.includes(input.toUpperCase())) return false;

    users.set(uuid, { ...user, role: input.toUpperCase() });

    const updated = getUser(uuid);

    const payload = { uuid, ...updated }

    delete payload.password;

    const token = generateToken(payload);

    return token;
};

const setPerm = (uuid, input) => {
    const user = getUser(uuid);

    users.set(uuid, { ...user, hasPerm: input });

    return true;
}

module.exports = { addUser, getUser, setRole, setPerm, getUsers };