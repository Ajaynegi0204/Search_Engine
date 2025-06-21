const { pool, signupSchema, loginSchema } = require('./db');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
const { z } = require('zod');

if (!process.env.JWT_SECRET) {
  throw new Error('JWT_SECRET is not defined in environment variables');
}

const verifyToken = (req, res, next) => {
  try {
    const token = req.cookies.token ||
                 (req.headers.authorization && req.headers.authorization.split(' ')[1]);

    if (!token) {
      return res.status(401).json({
        success: false,
        error: "Unauthorized",
        details: "No authentication token provided"
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    req.user = {
      userId: decoded.userId,
      email: decoded.email,
      username: decoded.username
    };

    next();

  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        error: "Unauthorized",
        details: "Invalid or expired token"
      });
    }
    console.error("Authentication error:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error",
      details: "Could not verify user"
    });
  }
};


module.exports = { verifyToken };