#!/usr/bin/env python3
"""
Robust local server for Coveo Commerce Demo Environment.
Serves the website directory and handles all routing properly.
"""

import http.server
import socketserver
import urllib.parse
import os
import sys
import json
import webbrowser
from pathlib import Path

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the demo environment."""
    
    def __init__(self, *args, **kwargs):
        # Change to website directory
        os.chdir(Path(__file__).parent.parent / 'website')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with proper routing."""
        parsed_path = urllib.parse.urlparse(self.path)

        # Serve the data file from the parent directory if requested
        if parsed_path.path == '/data/complete-payload.json':
            # Build the absolute path to the data file
            data_path = Path(__file__).parent.parent / 'data' / 'complete-payload.json'
            if data_path.exists():
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open(data_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File not found')
            return

        # Handle root path
        if parsed_path.path == '/':
            self.path = '/pages/simple-search.html'
            return super().do_GET()

        # Handle pages without .html extension
        if not parsed_path.path.endswith(('.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
            # Check if it's a page request
            if parsed_path.path.startswith('/pages/'):
                self.path = parsed_path.path + '.html' + ('?' + parsed_path.query if parsed_path.query else '')
                return super().do_GET()

        # Handle normal requests
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Custom logging to show useful information."""
        message = format % args
        print(f"🌐 {message}")

def find_free_port(start_port=8080, max_attempts=10):
    """Find a free port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")

def main():
    """Start the demo server."""
    # Check if we're in the right directory
    script_dir = Path(__file__).parent.parent
    if not (script_dir / 'website').exists():
        print("❌ Error: website directory not found!")
        print(f"Expected: {script_dir / 'website'}")
        return 1
    
    try:
        port = find_free_port()
        print(f"🚀 Starting Coveo Commerce Demo Server on port {port}")
        
        # Create server
        with socketserver.TCPServer(("localhost", port), DemoHandler) as httpd:
            server_url = f"http://localhost:{port}"
            
            print(f"""
✅ Demo server running successfully!

🌐 Access your demo at: {server_url}

📱 Available demo pages:
   • Main Search: {server_url}/
   • Nike Products: {server_url}/pages/simple-plp-nike.html
   • Adidas Products: {server_url}/pages/simple-plp-adidas.html
   • Product Detail: {server_url}/pages/product.html?id=PRODUCT_ID

🛒 Features:
   ✅ Product links work correctly
   ✅ Shopping cart functionality
   ✅ Analytics tracking: commerce-docs-demo
   ✅ Local product detail pages

Press Ctrl+C to stop the server
""")
            
            # Auto-open browser
            try:
                webbrowser.open(server_url)
            except Exception:
                pass  # Don't fail if browser opening fails
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == '__main__':
    exit(main())