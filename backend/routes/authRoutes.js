const express = require('express');
const router = express.Router();

const { signup, login, logout} = require('../controllers/user');
const {verifyToken} = require("../controllers/middleware");


router.post('/register', signup);
router.post('/login', login);
router.post('/logout', logout);
router.get('/verify-token', verifyToken, (req, res) => {
    res.json({ success: true, user: req.user });
});

module.exports = router;
