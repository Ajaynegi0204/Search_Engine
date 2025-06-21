const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
  const token = req.cookies?.token || req.headers?.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({
      success: false,
      message: 'Authentication required'
    });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(401).json({
        success: false,
        message: 'Invalid or expired token'
      });
    }

    req.user = {
      userId: decoded.userId,
      username: decoded.username,
      email: decoded.email
    };

    next();
  });
};

module.exports = { verifyToken };