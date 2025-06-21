
const express = require('express');
const cookieParser = require('cookie-parser');
const authRoutes = require('./routes/authRoutes');
const queryRoutes = require('./routes/query');
const cors = require('cors');
const { pool } = require('./controllers/db');

const app = express();

app.use(cors({
  origin: 'https://search-engine-2yu7.onrender.com',
  credentials: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '10mb' }));
app.use(cookieParser());

app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.status(200).json({ status: 'healthy' });
  } catch (err) {
    res.status(500).json({ status: 'unhealthy', error: err.message });
  }
});

app.use('/api/user', authRoutes);
app.use('/api/query' ,queryRoutes);


const PORT = 3000;
app.listen(PORT, async () => {
  try {
    await pool.query('SELECT 1');
    console.log(`Server running on http://localhost:${PORT}`);
    console.log('Database connection verified');
  } catch (err) {
    console.error('Database connection failed:', err);
    process.exit(1);
  }
});