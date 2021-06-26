const jwt = require("jsonwebtoken");
const boom = require("@hapi/boom");
const validateFacebookToken = require("../utils/validateFacebookToken");
const validateGoogle = require("../utils/validateGoogleToken");

/**
 * Verifies if a token is valid
 */
async function middleware(req, res, next) {
  const bearerToken = req.headers["authorization"];
  if (!bearerToken) {

    return next( res.json({
      error: {
        message: "Token required",
      },
    }));
  }
  const [bearer, token] = bearerToken.split(" ");
  if (bearer !== "Bearer") {

    return next(res.json({
      error: {
        message: "Invalid token format",
      },
    }));
  }

  try {
    const decoded = await jwt.verify(token, process.env.JWT_SECRET);
    if (decoded) {
      return next();
    }
  } catch (error) {}

  //verify if is google oauth token
  const isGoogleToken = await validateGoogle(token);
  if (isGoogleToken) {
    return next();
  }

  //verify if is facebook oauth token
  const isFacebookToken = validateFacebookToken(token);
  if (isFacebookToken) {
    return next();
  }
  //is not valid

  next(res.json({
    error: {
      message: "Invalid token",
    },
  }));
}

module.exports = middleware;
