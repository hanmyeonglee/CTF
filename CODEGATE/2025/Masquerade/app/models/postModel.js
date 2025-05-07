const { v4: uuidv4 } = require('uuid');

const posts = new Map();

const getPosts = (user) => {
    const result = [];

    for (const [key, value] of posts) {
        if (value.writer === user.uuid) {
            result.push({ ...value });
        }
    }

    return result;
};

const getPostById = (post_id) => {
    const post = posts.get(post_id);

    return post;
};

const addPost = (user, body) => {
    const uuid = uuidv4();
    const post = { post_id: uuid, writer: user.uuid, title: body.title, content: body.content };

    posts.set(uuid, post);

    return post
};

const deletePost = (post_id) => {
    const result = posts.delete(post_id);

    return result;
};

module.exports = { getPosts, getPostById, addPost, deletePost };