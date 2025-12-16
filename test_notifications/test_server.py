#!/usr/bin/env python3
"""
Simple HTTP Server for Testing Discord Notifications
Serves test JavaScript files with known secrets
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path

class TestServerHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve test files"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        """Add CORS headers for testing"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/javascript')
        super().end_headers()

def run_server(port=8000):
    """
    Run the test server
    
    Args:
        port: Port to run the server on (default: 8000)
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestServerHandler)
    
    print(f"\n{'='*60}")
    print(f"🚀 Test Server Started")
    print(f"{'='*60}")
    print(f"Server running on: http://localhost:{port}")
    print(f"\nAvailable test files:")
    print(f"  http://localhost:{port}/test_secrets_aws.js")
    print(f"  http://localhost:{port}/test_secrets_github.js")
    print(f"  http://localhost:{port}/test_secrets_multiple.js")
    print(f"  http://localhost:{port}/test_clean_api.js")
    print(f"\nPress Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run test HTTP server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)
