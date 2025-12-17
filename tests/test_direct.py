"""
Direct Test Script for New Features
Tests Phase 1, 2, and 3 enhancements without full scanner
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jsscanner.modules.ast_analyzer import ASTAnalyzer
from jsscanner.utils.logger import setup_logger

async def test_string_concatenation():
    """Test Phase 1: String Concatenation"""
    print("\n" + "="*60)
    print("PHASE 1: STRING CONCATENATION TEST")
    print("="*60)
    
    # Test content
    test_code = '''
const API_VERSION = "v1";
const baseUrl = "/api/" + API_VERSION + "/users";
const endpoint = "/data/" + userId + "/profile/" + section;
window.location = "/login?next=" + next + "&token=" + token;
fetch("/products/" + productId + "/reviews");
const templateUrl = `/api/v${version}/items`;
axios.get("/cart/" + cartId + "/items");
const complexUrl = "/api/" + version + "/users/" + userId + "/orders/" + orderId;
'''
    
    # Setup
    config = {
        'ast': {'min_word_length': 4},
        'force_rescan': False
    }
    logger = setup_logger("test")
    paths = {'extracts': Path('test_results/extracts')}
    paths['extracts'].mkdir(parents=True, exist_ok=True)
    
    analyzer = ASTAnalyzer(config, logger, paths)
    
    # Parse and extract
    tree = analyzer._parse_content(test_code)
    endpoints = analyzer._extract_endpoints_sync(tree.root_node, test_code)
    
    print(f"\n✅ Found {len(endpoints)} endpoints:\n")
    for ep in sorted(endpoints):
        print(f"   • {ep}")
    
    # Expected results
    expected = [
        "/api/EXPR/users",
        "/data/EXPR/profile/EXPR",
        "/login",  # May or may not have query params
        "/products/EXPR/reviews",
        "/cart/EXPR/items",
        "/api/EXPR/users/EXPR/orders/EXPR"
    ]
    
    print(f"\n📊 Expected: {len(expected)} endpoints")
    print(f"📊 Found: {len(endpoints)} endpoints")
    
    # Check if key patterns are found
    found_expr = any('EXPR' in ep for ep in endpoints)
    print(f"\n{'✅' if found_expr else '❌'} EXPR placeholder found: {found_expr}")
    
    return endpoints

async def test_enhanced_parameters():
    """Test Phase 2: Enhanced Parameters"""
    print("\n" + "="*60)
    print("PHASE 2: ENHANCED PARAMETER EXTRACTION TEST")
    print("="*60)
    
    test_code = '''
const config = {
    apiKey: "secret123",
    userId: 12345,
    authToken: "abc-xyz",
    sessionId: "session-001"
};

let sessionToken = "token-123";
const maxRetries = 3;
var apiEndpoint = "/api/v1";

const loginForm = `
<input type="text" name="username" id="user-field" />
<input type="password" name="password" />
<input type="email" name="email" />
<textarea name="comments"></textarea>
<select name="country"></select>
`;

function fetchUserData(userId, includeOrders, authToken) {
    return api.get('/users');
}
'''
    
    # Setup
    config = {
        'ast': {'min_word_length': 4},
        'force_rescan': False
    }
    logger = setup_logger("test")
    paths = {'extracts': Path('test_results/extracts')}
    
    analyzer = ASTAnalyzer(config, logger, paths)
    
    # Parse and extract
    tree = analyzer._parse_content(test_code)
    params = analyzer._extract_params_sync(tree.root_node, test_code)
    
    print(f"\n✅ Found {len(params)} parameters:\n")
    for param in sorted(params):
        print(f"   • {param}")
    
    # Check for expected sources
    json_keys = ['apiKey', 'userId', 'authToken', 'sessionId']
    variables = ['sessionToken', 'maxRetries', 'apiEndpoint']
    html_fields = ['username', 'password', 'email', 'comments', 'country']
    func_params = ['includeOrders']  # userId, authToken already in json_keys
    
    found_json = sum(1 for k in json_keys if k in params)
    found_vars = sum(1 for v in variables if v in params)
    found_html = sum(1 for h in html_fields if h in params)
    found_func = sum(1 for f in func_params if f in params)
    
    print(f"\n📊 Results by Source:")
    print(f"   JSON Keys: {found_json}/{len(json_keys)} ({'✅' if found_json >= len(json_keys)-1 else '❌'})")
    print(f"   Variables: {found_vars}/{len(variables)} ({'✅' if found_vars >= len(variables)-1 else '❌'})")
    print(f"   HTML Fields: {found_html}/{len(html_fields)} ({'✅' if found_html >= 3 else '⚠️'})")
    print(f"   Function Params: {found_func}/{len(func_params)} ({'✅' if found_func >= 1 else '⚠️'})")
    
    total_expected = len(json_keys) + len(variables) + len(html_fields) + len(func_params)
    print(f"\n📊 Total Expected: ~{total_expected} parameters")
    print(f"📊 Total Found: {len(params)} parameters")
    
    return params

async def test_wordlist_quality():
    """Test Phase 3: Wordlist Quality"""
    print("\n" + "="*60)
    print("PHASE 3: WORDLIST QUALITY TEST")
    print("="*60)
    
    test_code = '''
<!-- Premium quality products available -->

const imageGallery = `
<img src="product.jpg" alt="Premium leather wallet handcrafted" />
<title>Best Online Shopping Platform</title>
<meta name="description" content="Online marketplace for premium products" />
`;

const productCatalog = {
    electronics: "Electronics Department",
    furniture: "Furniture Section",
    clothing: "Clothing Store"
};

function searchInventory(category, priceRange, availability) {
    const searchQuery = buildQueryString(category);
    return fetchResults(searchQuery);
}

// Stop words test: the and for are but not you all
'''
    
    # Setup
    config = {
        'ast': {'min_word_length': 4},
        'force_rescan': False
    }
    logger = setup_logger("test")
    paths = {'extracts': Path('test_results/extracts')}
    
    analyzer = ASTAnalyzer(config, logger, paths)
    
    # Parse and extract
    tree = analyzer._parse_content(test_code)
    words = analyzer._generate_wordlist_sync(tree.root_node, test_code)
    
    print(f"\n✅ Found {len(words)} quality words:\n")
    for word in sorted(words)[:30]:  # Show first 30
        print(f"   • {word}")
    
    if len(words) > 30:
        print(f"   ... and {len(words) - 30} more")
    
    # Check quality
    good_words = ['premium', 'quality', 'products', 'leather', 'wallet', 'handcrafted',
                  'online', 'shopping', 'platform', 'marketplace', 'electronics',
                  'furniture', 'clothing', 'inventory', 'search']
    
    stop_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all']
    
    found_good = sum(1 for w in good_words if w in words)
    found_bad = sum(1 for w in stop_words if w in words)
    
    print(f"\n📊 Quality Check:")
    print(f"   Good words found: {found_good}/{len(good_words)} ({'✅' if found_good >= 8 else '⚠️'})")
    print(f"   Stop words found: {found_bad}/{len(stop_words)} ({'✅' if found_bad == 0 else '❌'})")
    
    if found_bad > 0:
        print(f"\n⚠️  Stop words that leaked through:")
        for sw in stop_words:
            if sw in words:
                print(f"      • {sw}")
    
    return words

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING NEW FEATURES - PHASES 1, 2, 3")
    print("="*60)
    
    try:
        # Run tests
        endpoints = await test_string_concatenation()
        params = await test_enhanced_parameters()
        words = await test_wordlist_quality()
        
        # Summary
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        print(f"\n✅ Phase 1 (Concatenation): {len(endpoints)} endpoints extracted")
        print(f"✅ Phase 2 (Parameters): {len(params)} parameters extracted")
        print(f"✅ Phase 3 (Wordlist): {len(words)} quality words extracted")
        
        # Overall success
        success_concat = any('EXPR' in ep for ep in endpoints)
        success_params = len(params) >= 10
        success_words = len(words) >= 10
        
        overall = "✅ PASS" if all([success_concat, success_params, success_words]) else "⚠️  PARTIAL"
        
        print(f"\n{'='*60}")
        print(f"Overall Test Result: {overall}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
