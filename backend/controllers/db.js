const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
const { z } = require('zod');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  connectionTimeoutMillis: 10000,
  query_timeout: 60000,
  idleTimeoutMillis: 60000,
  max: 5
});

pool.on('error', (err) => {
  console.error('Database error:', err.message);
});

pool.on('connect', () => {
  console.log('New database connection established');
});

const signupSchema = z.object({
  username: z.string().min(1, "Username is required"),
  email: z.string().email("Invalid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

const loginSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string(),
});

pool.query('SELECT NOW()')
  .then(() => console.log('✅ Database connection verified'))
  .catch(err => {
    console.error('❌ Database connection failed:', err.message);
    process.exit(1);
  });

module.exports = {
  signupSchema,
  loginSchema,
  pool,
  queryTimeout: 60000
};