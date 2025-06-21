const express = require('express');
const router = express.Router();

const { signup, login, verifyToken } = require('../controllers/user');


router.post('/register', signup);
router.post('/login', login);
router.get('/verify-token', verifyToken);


module.exports = router;
