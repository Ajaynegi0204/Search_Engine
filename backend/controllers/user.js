const { pool, signupSchema, loginSchema } = require('./db');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
const {z} = require('zod');


if (!process.env.JWT_SECRET) {
  throw new Error('JWT_SECRET is not defined in environment variables');
}

async function signup(req, res) {
  const parsed = signupSchema.safeParse({
    username: req.body.name,
    email: req.body.email,
    password: req.body.password,
  });

  if (!parsed.success) {
    return res.status(400).json({ success: false, message: parsed.error.issues[0].message });
  }

  const { username, email, password } = parsed.data;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await pool.query(
      'INSERT INTO users (username, email, password) VALUES ($1, $2, $3) RETURNING id, username, email',
      [username, email, hashedPassword]
    );

    const user = result.rows[0];
    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, {
      expiresIn: '7d'
    });

    res.status(201).json({ success: true, token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: 'Signup failed' });
  }
}


async function login(req, res) {
  const parsed = loginSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ success: false, message: parsed.error.issues[0].message });
  }

  const { email, password } = parsed.data;

  try {
    const result = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(400).json({ success: false, message: 'User not found' });
    }

    const user = result.rows[0];
    const match = await bcrypt.compare(password, user.password);

    if (!match) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, {
      expiresIn: '7d'
    });

    res.status(200).json({ success: true, token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: 'Login failed' });
  }
}

const verifyToken = (req, res, next) => {
  const token = req.cookies.token ||
                req.headers['authorization']?.split(' ')[1] ||
                req.body.token;

  if (!token) {
    return res.status(401).json({
      error: "Unauthorized",
      details: "No authentication token provided"
    });
  }

  jwt.verify(token, process.env.JWT_SECRET, async (err, decoded) => {
    if (err) {
      return res.status(401).json({
        error: "Unauthorized",
        details: "Invalid or expired token"
      });
    }

    try {
      // Verify user exists in database
      const { rows } = await pool.query(
        'SELECT id FROM users WHERE id = $1',
        [decoded.userId]
      );

      if (rows.length === 0) {
        return res.status(401).json({
          error: "Unauthorized",
          details: "User not found"
        });
      }

      req.user = decoded;
      next();
    } catch (dbErr) {
      console.error("Database verification error:", dbErr);
      res.status(500).json({
        error: "Internal server error",
        details: "Could not verify user"
      });
    }
  });
};
module.exports = { signup, login, verifyToken};

