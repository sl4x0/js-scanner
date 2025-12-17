// Test File 3: Wordlist Quality (Phase 3)

// Test 3a: HTML Comments

// Test 3b: Image Alt Text
const imageGallery = `
<img src="product1.jpg" alt="Premium leather wallet" />
<img src="product2.jpg" alt="Handcrafted wooden furniture" />
<img src="banner.jpg" alt="Summer sale collection" />
`;

// Test 3c: Meta Tags
const htmlHead = `
<head>
    <meta name="description" content="Online marketplace for premium products" />
    <meta name="keywords" content="shopping, premium, marketplace, products" />
    <meta property="og:title" content="Premium Marketplace Store" />
    <title>Best Online Shopping Platform</title>
</head>
`;

// Test 3d: Aria Labels and Accessibility
const accessibleContent = `
<button aria-label="Submit payment information">Pay Now</button>
<input aria-label="Search products catalog" placeholder="Search products" />
<div aria-label="Shopping cart summary">Cart Items</div>
`;

// Test 3e: Regular JavaScript with identifiers
const productCatalog = {
    electronics: "Electronics Department",
    furniture: "Furniture Section",
    clothing: "Clothing Store",
    accessories: "Accessories Boutique"
};

function searchInventory(category, priceRange, availability) {
    const searchQuery = buildQueryString(category);
    return fetchResults(searchQuery);
}

// Expected Quality Words (should be extracted):
// premium, quality, products, available, customer, support, contact, information
// shipping, worldwide, tracking, leather, wallet, handcrafted, wooden, furniture
// summer, collection, online, marketplace, shopping, platform, payment
// electronics, department, clothing, accessories, boutique, inventory
// search, catalog, category

// Should NOT Extract (stop words):
// the, and, for, with, available (actually should keep)
// from, into, about, other, these

// Should NOT Extract (too short or invalid):
// a, an, to, in, on, at, by, of

// Should NOT Extract (programming keywords):
// var, let, const, function, return, new, true, false
