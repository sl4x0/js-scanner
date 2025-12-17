// Test File 1: String Concatenation (Phase 1)
// This tests the reconstruction of concatenated URLs

// Test 1: Simple concatenation
const API_VERSION = "v1";
const baseUrl = "/api/" + API_VERSION + "/users";

// Test 2: Multiple concatenations
const endpoint = "/data/" + userId + "/profile/" + section;

// Test 3: Login with query parameters
window.location = "/login?next=" + next + "&token=" + token;

// Test 4: fetch with concatenation
fetch("/products/" + productId + "/reviews");

// Test 5: Template literal (already working)
const templateUrl = `/api/v${version}/items`;

// Test 6: Mixed string and variable
axios.get("/cart/" + cartId + "/items");

// Test 7: Complex nested concatenation
const complexUrl = "/api/" + version + "/users/" + userId + "/orders/" + orderId;

// Test 8: Domain concatenation
const fullUrl = "https://api.example.com/" + path + "/endpoint";

// Expected Outputs:
// /api/EXPR/users
// /data/EXPR/profile/EXPR
// /login?next=EXPR&token=EXPR
// /products/EXPR/reviews
// /api/vEXPR/items (template literal)
// /cart/EXPR/items
// /api/EXPR/users/EXPR/orders/EXPR
