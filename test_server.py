#!/usr/bin/env python3
"""
🚀 JS-Scanner VPS-Grade Test Server
-----------------------------------
Simulates a production SPA/API environment for comprehensive scanner validation.

Features:
- Multi-threaded (handles 50+ concurrent requests)
- Webpack-style chunking & lazy loading (tests recursion depth 2+)
- Next.js-like structure (tests manifest.js, runtime.js patterns)
- Source maps with real recovery scenarios
- Cloud assets (S3, Azure, GCS, Firebase)
- Real AWS/JWT secrets for TruffleHog validation
- Analytics/CDN scripts for noise filter testing
- HEAD request support for URL validation
- CORS headers for realistic browser behavior
"""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Multi-threading for concurrent scanner requests
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

# --- Production-Grade Mock Application ---

MOCK_FILES = {
    # === ENTRY POINTS ===
    '/': {
        'type': 'text/html',
        'content': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureApp Dashboard</title>
    <script src="/static/js/runtime.js"></script>
    <script src="/static/js/main-abc123.js"></script>
    <script src="/static/js/vendors.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/app.bundle.js"></script>
</body>
</html>"""
    },

    # === WEBPACK RUNTIME (Tests manifest.js fix) ===
    '/static/js/runtime.js': {
        'type': 'application/javascript',
        'content': """// Webpack Runtime - Chunk Loading System
(function(modules) {
    var installedChunks = {};
    function __webpack_require__(chunkId) {
        if(installedChunks[chunkId]) return installedChunks[chunkId].exports;
        var chunk = installedChunks[chunkId] = { exports: {} };
        modules[chunkId].call(chunk.exports, chunk, chunk.exports, __webpack_require__);
        return chunk.exports;
    }
    
    // CRITICAL: Chunk dictionary for lazy loading
    __webpack_require__.e = function(chunkId) {
        var promises = [];
        var chunkMap = {
            "admin": "/static/js/chunks/admin-panel.js",
            "settings": "/static/js/chunks/user-settings.js",
            "dashboard": "/static/js/chunks/dashboard-widgets.js"
        };
        if(chunkMap[chunkId]) {
            promises.push(loadScript(chunkMap[chunkId]));
        }
        return Promise.all(promises);
    };
    
    function loadScript(src) {
        return new Promise(function(resolve) {
            var script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
    
    __webpack_require__.e("admin").then(() => console.log("Admin loaded"));
})({});

//# sourceMappingURL=runtime.js.map"""
    },

    # === MAIN APPLICATION (Tests recursion + cloud assets) ===
    '/static/js/main-abc123.js': {
        'type': 'application/javascript',
        'content': """// Main Application Bundle
const CONFIG = {
    // [TEST] Cloud Asset Detection
    storage: {
        s3: "https://prod-uploads.s3.us-west-2.amazonaws.com/media/",
        s3Backup: "https://backup-bucket.s3.amazonaws.com/archives/",
        azure: "https://prodstorageacct.blob.core.windows.net/assets/images/",
        azureDfs: "https://datalake.dfs.core.windows.net/analytics/",
        gcs: "https://storage.googleapis.com/company-data/reports/",
        gcsApi: "https://storage.cloud.google.com/cdn-assets/js/",
        firebase: "https://company-app-prod.firebaseio.com/users/",
        firebaseStorage: "https://firebasestorage.googleapis.com/v0/b/prod-bucket/o/files"
    },
    
    // [TEST] API Endpoints
    apiEndpoints: {
        auth: "/api/v2/auth/login",
        user: "/api/v2/users/profile",
        admin: "/api/v1/admin/dashboard",
        graphql: "https://api.backend.com/graphql"
    }
};

// [TEST] Secret Detection - Real AWS Key Pattern
const AWS_CREDENTIALS = {
    accessKeyId: "AKIAIOSFODNN7EXAMPLE",
    secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region: "us-east-1"
};

// [TEST] Recursion Level 1 - Dynamic Import
import("/static/js/chunks/admin-panel.js");
require("./chunks/dashboard-widgets.js");

// [TEST] API Calls
fetch(CONFIG.apiEndpoints.auth, {
    method: "POST",
    body: JSON.stringify({ user: "admin" })
});

axios.get("https://api.company.com/v1/data");

//# sourceMappingURL=main-abc123.js.map"""
    },

    # === LAZY-LOADED CHUNKS (Tests Recursion Depth 2) ===
    '/static/js/chunks/admin-panel.js': {
        'type': 'application/javascript',
        'content': """// Admin Panel Chunk - Level 2
console.log("Admin Panel Loaded");

// [TEST] Secret in nested chunk
const ADMIN_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFkbWluIFVzZXIiLCJpYXQiOjE1MTYyMzkwMjIsInJvbGUiOiJhZG1pbiJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

// [TEST] Recursion Level 2 - Nested Import
import("./user-settings.js");

// [TEST] Admin API endpoints
const adminEndpoints = {
    users: "/api/admin/users",
    logs: "/api/admin/audit-logs",
    config: "/api/admin/config"
};

fetch("/api/admin/users");"""
    },

    '/static/js/chunks/user-settings.js': {
        'type': 'application/javascript',
        'content': """// User Settings Chunk - Level 3 (Deepest)
console.log("User Settings Loaded - Recursion Depth 3");

// [TEST] Deep secret (fake Stripe key for testing)
const STRIPE_KEY = "sk_test_51ABCDEfghIJKLmnop123456789FAKE";

// [TEST] Third-party integrations
const integrations = {
    stripe: "https://api.stripe.com/v1/",
    sendgrid: "https://api.sendgrid.com/v3/",
    twilio: "https://api.twilio.com/2010-04-01/"
};"""
    },

    '/static/js/chunks/dashboard-widgets.js': {
        'type': 'application/javascript',
        'content': """// Dashboard Widgets
const widgetConfig = {
    analytics: "https://analytics.company.com/track",
    metrics: "/api/v1/metrics/dashboard"
};

// [TEST] Environment variable leakage
const ENV = {
    API_KEY: "prod_api_key_abc123xyz",
    SENTRY_DSN: "https://abc123@o123456.ingest.sentry.io/789012"
};"""
    },

    # === VENDOR BUNDLE (Tests noise filter) ===
    '/static/js/vendors.js': {
        'type': 'application/javascript',
        'content': """/*! Vendor Bundle - React, Lodash, Axios */
// This should be filtered by noise patterns
(function(){console.log("React vendor");})();
(function(){console.log("Lodash vendor");})();
(function(){console.log("Axios vendor");})();
""" + ("/* filler */" * 50)
    },

    # === APPLICATION BUNDLE (Tests beautification) ===
    '/static/js/app.bundle.js': {
        'type': 'application/javascript',
        'content': """!function(e){var t={};function n(r){if(t[r])return t[r].exports;var o=t[r]={i:r,l:!1,exports:{}};return e[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=e,n.c=t,n.d=function(e,t,r){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:r})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)n.d(r,o,function(t){return e[t]}.bind(null,o));return r},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="",n(n.s=0)}([function(e,t,n){"use strict";const r={apiUrl:"https://api.prod.com",s3Bucket:"https://my-app.s3.amazonaws.com"};console.log("App initialized",r)}]);
//# sourceMappingURL=app.bundle.js.map"""
    },

    # === SOURCE MAPS (Tests recovery) ===
    '/static/js/main-abc123.js.map': {
        'type': 'application/json',
        'content': json.dumps({
            "version": 3,
            "file": "main-abc123.js",
            "sourceRoot": "",
            "sources": ["../../src/main.tsx", "../../src/config.ts", "../../src/api.ts"],
            "names": ["CONFIG", "AWS_CREDENTIALS", "fetch"],
            "mappings": "AAAA;AACA;AACA;...",
            "sourcesContent": [
                "// RECOVERED: Original TypeScript Source\nimport { CONFIG } from './config';\nconst secret = 'RECOVERED_DEV_API_KEY_xyz789';",
                "export const CONFIG = { apiUrl: 'https://staging-api.com' };",
                "export async function callAPI() { /* original code */ }"
            ]
        })
    },

    '/static/js/app.bundle.js.map': {
        'type': 'application/json',
        'content': json.dumps({
            "version": 3,
            "file": "app.bundle.js",
            "sources": ["webpack:///src/index.js"],
            "sourcesContent": ["const config = { s3: 'https://dev-bucket.s3.amazonaws.com' };"]
        })
    },

    # === NOISE/CDN FILES (Should be filtered) ===
    '/static/js/jquery-3.7.1.min.js': {
        'type': 'application/javascript',
        'content': "/*! jQuery v3.7.1 | (c) OpenJS Foundation */\n" + ("(function(window){var jQuery=function(){};})(window);" * 20)
    }
}

class ProductionHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Colorful request logging"""
        method_color = '\033[92m' if self.command == 'GET' else '\033[94m'
        sys.stderr.write(f"{method_color}[{self.command}]\033[0m {args[0]}\n")

    def _send_response(self, path, method="GET"):
        """Handle both GET and HEAD requests"""
        path = path.split('?')[0].split('#')[0]
        
        if path == '/' or path == '':
            path = '/'
        
        if path in MOCK_FILES:
            file_data = MOCK_FILES[path]
            content = file_data['content'].encode('utf-8') if isinstance(file_data['content'], str) else file_data['content']
            
            self.send_response(200)
            self.send_header('Content-Type', file_data['type'])
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            
            if method == "GET":
                self.wfile.write(content)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            if method == "GET":
                self.wfile.write(b"404 Not Found")

    def do_GET(self):
        self._send_response(self.path, method="GET")

    def do_HEAD(self):
        """Critical for scanner's validate_url_exists()"""
        self._send_response(self.path, method="HEAD")

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    PORT = 9999
    HOST = '127.0.0.1'  # localhost only for security
    
    try:
        server = ThreadingHTTPServer((HOST, PORT), ProductionHandler)
        print("\n" + "="*70)
        print("🚀 \033[96mJS-Scanner VPS-Grade Test Server\033[0m")
        print("="*70)
        print(f"   📡 Address:  \033[92mhttp://localhost:{PORT}\033[0m")
        print(f"   🎯 Targets:  {len(MOCK_FILES)} endpoints")
        print(f"   🔧 Features: Recursion (depth 3), Source Maps, Cloud Assets, Secrets")
        print("\n" + "-"*70)
        print("   \033[93mTest Commands:\033[0m")
        print(f"   python -m jsscanner -t test1 -u http://localhost:{PORT}/ --force")
        print(f"   python -m jsscanner -t test2 -u http://localhost:{PORT}/static/js/main-abc123.js --force")
        print("-"*70)
        print("   Press Ctrl+C to stop\n")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[93m🛑 Server stopped gracefully\033[0m")
        server.server_close()
    except OSError as e:
        print(f"\n\033[91m❌ Error: {e}\033[0m")
        print(f"   Hint: Port {PORT} may already be in use. Try: netstat -ano | findstr :{PORT}")
        sys.exit(1)
