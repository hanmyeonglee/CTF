const adminGuard = (req, res, next) => {
    if (req.user.role !== "ADMIN") return res.status(403).json({ message: 'Forbidden.' });

    next();
};

const postGuard = (req, res, next) => {
    if (!req.user.hasPerm) return res.status(403).json({ message: 'Forbidden.' });

    next();
};

module.exports = { adminGuard, postGuard };