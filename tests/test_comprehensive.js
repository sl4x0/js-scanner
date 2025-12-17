// Comprehensive Test File - All Features Combined

// ============================================
// PHASE 1: String Concatenation Tests
// ============================================

// API endpoints with concatenation
const API_BASE = "/api/v2";
const userEndpoint = API_BASE + "/users/" + userId;
const orderEndpoint = "/orders/" + orderId + "/details";

// Authentication endpoints
const loginUrl = "/auth/login?redirect=" + redirectUrl + "&type=" + loginType;
const logoutUrl = "/auth/logout?token=" + authToken;

// Dynamic resource loading
fetch("/resources/" + resourceId + "/data.json");
axios.post("/submit/" + formId + "/response", formData);

// ============================================
// PHASE 2: Enhanced Parameter Extraction
// ============================================

// API Configuration Object
const apiConfig = {
    apiKey: "live_key_123abc",
    secretKey: "sk_live_456def",
    webhookUrl: "https://example.com/webhook",
    apiVersion: "2024-01",
    timeout: 30000,
    retryAttempts: 3,
    enableLogging: true
};

// User Authentication
const authCredentials = {
    username: "admin@example.com",
    password: "encrypted_pass",
    mfaCode: "123456",
    deviceId: "device_abc123",
    sessionToken: "sess_xyz789"
};

// Payment Processing
let cardNumber = "4111111111111111";
let cvv = "123";
let expiryDate = "12/25";
const billingAddress = "123 Main St";
var postalCode = "12345";

// Form with HTML inputs
const checkoutForm = `
<form id="checkout-form">
    <input type="text" name="fullName" placeholder="Full Name" required />
    <input type="email" name="emailAddress" id="email-input" />
    <input type="tel" name="phoneNumber" />
    
    <input type="text" name="cardNumber" id="cc-number" />
    <input type="text" name="cardCvv" maxlength="3" />
    <select name="cardType" id="card-type">
        <option value="visa">Visa</option>
        <option value="mastercard">MasterCard</option>
    </select>
    
    <textarea name="deliveryInstructions" rows="3"></textarea>
    
    <input type="checkbox" name="saveCard" id="save-payment" />
    <input type="checkbox" name="agreeTerms" required />
    
    <button type="submit" name="submitPayment">Complete Purchase</button>
</form>
`;

// Function parameters
function processPayment(orderId, customerId, amount, paymentMethod, metadata) {
    const transactionId = generateTransactionId();
    return submitTransaction(transactionId, amount);
}

// ============================================
// PHASE 3: Wordlist Quality Tests
// ============================================

// HTML with rich content
const pageContent = `
<!DOCTYPE html>
<html>
<head>
    <title>Premium E-Commerce Platform - Buy Quality Products</title>
    <meta name="description" content="Discover premium products with worldwide shipping and excellent customer service" />
    <meta name="keywords" content="ecommerce, shopping, premium, quality, delivery" />
</head>
<body>
    <!-- Main navigation and search functionality -->
    <header>
        <nav aria-label="Primary navigation menu">
            <a href="/products">Browse Products</a>
            <a href="/categories">Shop Categories</a>
            <a href="/deals">Special Deals</a>
        </nav>
        <input type="search" placeholder="Search products catalog" aria-label="Product search" />
    </header>
    
    <!-- Featured products showcase -->
    <section id="featured-products">
        <h2>Featured Premium Collection</h2>
        <div class="product-grid">
            <article class="product-card">
                <img src="luxury-watch.jpg" alt="Swiss crafted luxury timepiece" />
                <h3>Premium Watches</h3>
                <p>Handcrafted Swiss movements with lifetime warranty</p>
            </article>
            
            <article class="product-card">
                <img src="leather-bag.jpg" alt="Italian leather messenger bag" />
                <h3>Designer Accessories</h3>
                <p>Genuine leather goods imported from Italy</p>
            </article>
        </div>
    </section>
    
    <!-- Customer testimonials -->
    <section id="testimonials">
        <!-- Excellent service and fast shipping -->
        <blockquote>
            Outstanding quality products delivered quickly
        </blockquote>
    </section>
</body>
</html>
`;

// Business logic with domain-specific terms
const inventorySystem = {
    warehouseLocation: "midwest",
    stockQuantity: 1500,
    reorderThreshold: 100,
    supplierInfo: "premium_suppliers",
    shippingMethods: ["express", "standard", "overnight"]
};

function calculateShipping(destination, weight, dimensions, priority) {
    const baseRate = getShippingRate(destination);
    const surcharge = calculateSurcharge(weight, dimensions);
    return baseRate + surcharge;
}

// ============================================
// EXPECTED RESULTS SUMMARY
// ============================================

// ENDPOINTS (with EXPR for dynamic parts):
// - /api/v2/users/EXPR
// - /orders/EXPR/details
// - /auth/login?redirect=EXPR&type=EXPR
// - /auth/logout?token=EXPR
// - /resources/EXPR/data.json
// - /submit/EXPR/response
// Total: ~15-20 unique endpoints

// PARAMETERS (from all sources):
// - Config: apiKey, secretKey, webhookUrl, apiVersion, timeout, retryAttempts, enableLogging
// - Auth: username, password, mfaCode, deviceId, sessionToken
// - Payment: cardNumber, cvv, expiryDate, billingAddress, postalCode
// - HTML: fullName, emailAddress, phoneNumber, cardCvv, cardType, deliveryInstructions, saveCard, agreeTerms, submitPayment
// - Variables: userId, orderId, redirectUrl, loginType, authToken, resourceId, formId
// - Functions: customerId, amount, paymentMethod, metadata, transactionId
// Total: ~40-50 unique parameters

// WORDLIST (quality words only):
// - Premium, quality, products, worldwide, shipping, excellent, customer, service
// - discover, ecommerce, shopping, delivery, navigation, search, functionality
// - browse, categories, special, deals, featured, collection, luxury, timepiece
// - handcrafted, swiss, movements, lifetime, warranty, designer, accessories
// - genuine, leather, imported, italy, testimonials, outstanding, delivered
// - quickly, inventory, warehouse, stock, quantity, reorder, threshold
// - supplier, express, standard, overnight, destination, weight, dimensions
// - calculate, surcharge, baseRate
// Total: ~60-80 quality words (NO stop words like: the, and, with, for, from)
