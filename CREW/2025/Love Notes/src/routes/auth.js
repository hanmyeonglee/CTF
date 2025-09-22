const express = require('express');
const crypto = require('crypto');
const User = require('../models/user');
const jwt = require('jsonwebtoken');
const jwtSecret = crypto.randomBytes(64).toString('hex');
const router = express.Router();

// Register Route
router.post('/register', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {return res.status(400).json({ message: 'Email or password missing' });}
  try {
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }
    const user = new User({ email, password });
    await user.save();
    res.redirect('/login')
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Login Route
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {return res.status(400).json({ message: 'Email or password missing' });}
  try {
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    if (password !== user.password) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign({ userId: user._id }, jwtSecret, { expiresIn: '1h' });

    // Set token as HTTP-only cookie
    res.cookie('token', token, {
      sameSite: 'strict',
      httpOnly: true, 
      secure: true,
      maxAge: 3600000,  // 1 hour expiration time
    });

    res.redirect('/dashboard')
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Logout Route
router.get('/logout', (req, res) => {
  res.clearCookie('token');
  res.redirect('/')
});

// Middleware to protect routes
const protectRoute = (req, res, next) => {
  const token = req.cookies.token;
  if (!token) return res.status(401).json({ message: 'No token, authorization denied' });

  try {
    const decoded = jwt.verify(token, jwtSecret);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Invalid token' });
  }
};

module.exports = { router, protectRoute };

