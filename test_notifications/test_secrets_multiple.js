// Test file 3: Multiple secrets in one file
const crypto = require("crypto");

// Configuration object with multiple fake credentials
const config = {
  database: {
    host: "db.example.com",
    username: "admin",
    password: "SuperSecret123!@#Password", // Weak password for testing
    port: 5432,
  },

  stripe: {
    // FAKE Stripe API keys
    publishableKey: "pk_test_51234567890abcdefghijklmnopqrstuvwxyz",
    secretKey: "sk_test_51234567890abcdefghijklmnopqrstuvwxyz",
  },

  jwt: {
    // Fake JWT secret
    secret: "my-super-secret-jwt-key-that-should-not-be-hardcoded",
    expiresIn: "24h",
  },

  slack: {
    // FAKE Slack webhook URL - EXAMPLE ONLY (not a real format)
    webhookUrl: "https://example.com/fake-webhook-url-for-testing-only",
    channel: "#general",
  },

  sendgrid: {
    // FAKE SendGrid API key
    apiKey:
      "SG.1234567890abcdefghijklmnopqrstuvwxyz.ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
  },
};

// API endpoints discovered in this file
const apiEndpoints = [
  "/api/v1/users",
  "/api/v1/products",
  "/api/v1/orders",
  "/api/v1/payments",
  "/api/v1/webhooks/stripe",
  "/api/v1/webhooks/slack",
  "/api/admin/settings",
  "/api/admin/users",
];

// Query parameters
const queryParams = {
  userId: "user_id",
  productId: "product_id",
  orderId: "order_id",
  apiKey: "api_key",
  sessionToken: "session_token",
  refreshToken: "refresh_token",
};

function generateToken(payload) {
  return crypto
    .createHmac("sha256", config.jwt.secret)
    .update(JSON.stringify(payload))
    .digest("hex");
}

module.exports = { config, apiEndpoints, queryParams, generateToken };
