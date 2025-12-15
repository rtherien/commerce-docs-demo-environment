#!/usr/bin/env python3
"""
Generate HTML files with environment variables
"""

import os
import re

def load_env_file(env_file_path='.env'):
    """Load environment variables from .env file"""
    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def update_html_files():
    """Update HTML files to use environment variable for access token"""
    env_vars = load_env_file()
    
    access_token = env_vars.get('COVEO_FRONTEND_ACCESS_TOKEN')
    if not access_token:
        print("❌ COVEO_FRONTEND_ACCESS_TOKEN not found in .env file")
        return False
    
    html_files = [
        'website/pages/simple-search.html',
        'website/pages/simple-plp-adidas.html',
        'website/pages/simple-plp-steve-madden.html',
        'website/pages/simple-plp-ecco.html',
        'website/pages/simple-plp-dooney-bourke.html',
        'website/pages/simple-plp-nike.html'
    ]
    
    # Pattern to find the hardcoded access token (including empty strings)
    pattern = r'accessToken:\s*["\'][^"\']*["\']'
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