#!/usr/bin/env python3
"""
Script to update DocumentId URLs in the complete payload for local demo environment.
Maintains Coveo's DocumentId format requirements (must contain :// text).
"""

import json
import re
import argparse
import shutil
from pathlib import Path

def extract_product_id(url):
    """Extract product ID from various URL formats."""
    # Handle sports.barca.group URLs
    if 'sports.barca.group' in url:
        match = re.search(r'/pdp/([^/?#]+)', url)
        if match:
            return match.group(1)
    
    # Handle other URL formats
    match = re.search(r'[?&]id=([^&]+)', url)
    if match:
        return match.group(1)
    
    # Fallback: use last path segment
    path_parts = url.rstrip('/').split('/')
    return path_parts[-1] if path_parts else 'unknown'

def update_document_ids(input_file, base_url, backup=True):
    """Update all DocumentId fields in the payload."""
    input_path = Path(input_file)
    
    if backup:
        backup_path = input_path.parent / f"{input_path.stem}-backup.json"
        print(f"Creating backup: {backup_path}")
        shutil.copy2(input_file, backup_path)
    
    print(f"Loading payload from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    
    if 'AddOrUpdate' not in payload:
        raise ValueError("Invalid payload format - 'AddOrUpdate' key not found")
    
    updated_count = 0
    
    for item in payload['AddOrUpdate']:
        if 'DocumentId' in item:
            original_url = item['DocumentId']
            product_id = extract_product_id(original_url)
            
            # Create new localhost URL with product ID parameter
            new_url = f"{base_url}?id={product_id}"
            
            # Store original URL for reference in product page
            item['DocumentId'] = new_url
            item['original_url'] = original_url  # Add original URL as metadata
            
            updated_count += 1
    
    print(f"Updated {updated_count} DocumentId fields")
    
    # Save updated payload
    print(f"Saving updated payload to: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    
    print("✅ DocumentId URLs updated successfully!")
    return updated_count

def main():
    parser = argparse.ArgumentParser(description='Update DocumentId URLs in Coveo payload')
    parser.add_argument('--input-file', default='data/complete-payload.json',
                      help='Input JSON file path (default: data/complete-payload.json)')
    parser.add_argument('--base-url', required=True,
                      help='Base URL for new DocumentId URLs (e.g., http://localhost:8080/pages/product.html)')
    parser.add_argument('--backup', action='store_true',
                      help='Create backup of original file')
    
    args = parser.parse_args()
    
    try:
        update_document_ids(args.input_file, args.base_url, args.backup)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())