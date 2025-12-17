// Test File 2: Enhanced Parameter Extraction (Phase 2)

// Test 2a: JSON Object Keys
const config = {
    apiKey: "secret123",
    userId: 12345,
    authToken: "abc-xyz",
    sessionId: "session-001",
    refreshToken: "refresh-xyz"
};

const userProfile = {
    username: "john_doe",
    email: "john@example.com",
    firstName: "John",
    lastName: "Doe",
    phoneNumber: "+1234567890"
};

// Test 2b: Variable Declarations
let sessionToken = "token-123";
const maxRetries = 3;
var apiEndpoint = "/api/v1";
let requestTimeout = 5000;
const enableDebug = true;

// Test 2c: HTML Input Fields (embedded in strings)
const loginFormHtml = `
<form action="/login" method="POST">
    <input type="text" name="username" id="user-field" />
    <input type="password" name="password" id="pass-field" />
    <input type="email" name="email" />
    <textarea name="comments" id="user-comments"></textarea>
    <select name="country" id="country-select">
        <option>USA</option>
    </select>
    <input type="submit" name="submitBtn" value="Login" />
</form>
`;

const signupForm = `
<input name="firstName" />
<input name="lastName" />
<input id="date-of-birth" />
<input data-name="phoneNumber" />
<input data-field="address" />
`;

// Test 2d: Function Parameters
function fetchUserData(userId, includeOrders, authToken) {
    return api.get(`/users/${userId}`, {
        params: { includeOrders, authToken }
    });
}

// Expected Parameters:
// From JSON keys: apiKey, userId, authToken, sessionId, refreshToken, username, email, firstName, lastName, phoneNumber
// From variables: sessionToken, maxRetries, apiEndpoint, requestTimeout, enableDebug
// From HTML: username, password, email, comments, country, submitBtn, date-of-birth, phoneNumber, address
// From functions: includeOrders (userId and authToken already extracted)
// Total: ~25-30 unique parameters
