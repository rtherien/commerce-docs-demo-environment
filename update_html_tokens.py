#!/usr/bin/env python3
"""
Generate HTML files with environment variables
"""

import os
import re
from dotenv import load_dotenv

def update_html_files():
    """Update HTML files to use environment variable for access token"""
    load_dotenv()
    
    access_token = os.getenv('COVEO_API_KEY')
    if not access_token:
        print("❌ COVEO_API_KEY not found in environment variables")
        return False
    
    html_files = [
        'website/pages/simple-search.html',
        'website/pages/simple-plp-adidas.html',
        'website/pages/simple-plp-steve-madden.html',
        'website/pages/simple-plp-ecco.html',
        'website/pages/simple-plp-dooney-bourke.html',
        'website/pages/simple-plp-nike.html'
    ]
    
    # Pattern to find the hardcoded access token
    pattern = r'accessToken:\s*["\'][^"\']+["\']'
    replacement = f'accessToken: "{access_token}"'
    
    for file_path in html_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace the access token
            updated_content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return True

if __name__ == "__main__":
    update_html_files()