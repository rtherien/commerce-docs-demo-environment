#!/usr/bin/env python3
"""
Script to update image URLs in payload files with configurable base URL.
This allows different users to use their own image hosting setup.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_path}' not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        return {}


def update_image_urls(payload: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    """Update image URLs in the payload with the new base URL."""
    
    # Mapping of products to their image filenames
    image_mapping = {
        "CVO-scr-001": "red-soccer-shoes.png",      # Red soccer shoes
        "CVO-scr-002": "blue-soccer-shoes.png",     # Blue soccer shoes  
        "CVO-scr-003": "yellow-soccer-shoes.jpg",   # Yellow soccer shoes
        "CVO-scr-004": "black-soccer-shoes.jpg",    # Black soccer shoes
        "CVO-hcs-001": {                            # Hockey sticks (multiple colors)
            "Black": "black-hockey-stick.jpg",
            "Red": "red-hockey-stick.jpg"
        },
        "CVO-gfd-001": "golf-driver.jpg"            # Golf driver
    }
    
    if "addOrUpdate" not in payload:
        return payload
    
    updated_count = 0
    
    for item in payload["addOrUpdate"]:
        if item.get("objecttype") != "Product":
            continue
            
        product_id = item.get("ec_product_id")
        if not product_id:
            continue
            
        # Determine the correct image filename
        image_file = None
        
        if product_id in image_mapping:
            mapping = image_mapping[product_id]
            
            # Handle hockey sticks with different colors
            if isinstance(mapping, dict):
                product_name = item.get("ec_name", "")
                if "Black" in product_name:
                    image_file = mapping["Black"]
                elif "Red" in product_name:
                    image_file = mapping["Red"]
            else:
                image_file = mapping
        
        if image_file:
            new_url = f"{base_url.rstrip('/')}/{image_file}"
            
            # Update both ec_images and ec_thumbnails if they exist
            if "ec_images" in item:
                item["ec_images"] = [new_url]
                updated_count += 1
            
            if "ec_thumbnails" in item:
                item["ec_thumbnails"] = [new_url]
    
    print(f"✅ Updated {updated_count} product image URLs")
    return payload


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update image URLs in payload files")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--payload", default="data/full-product-payload-sample.json", 
                       help="Payload file to update")
    parser.add_argument("--base-url", help="Override base URL for images")
    parser.add_argument("--output", help="Output file (defaults to updating input file)")
    
    args = parser.parse_args()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Load configuration
    config_path = project_root / args.config
    config = load_config(str(config_path))
    
    # Determine base URL
    if args.base_url:
        base_url = args.base_url
    elif "image_base_url" in config:
        base_url = config["image_base_url"]
    else:
        print("❌ No image base URL found. Please:")
        print("   1. Add 'image_base_url' to your config.json, or")
        print("   2. Use --base-url parameter")
        print("\nExample URLs:")
        print("   • GitHub: https://raw.githubusercontent.com/USER/REPO/main/assets")
        print("   • S3: https://your-bucket.s3.amazonaws.com/images")
        print("   • CDN: https://your-cdn-domain.com/images")
        sys.exit(1)
    
    # Load payload file
    payload_path = project_root / args.payload
    if not payload_path.exists():
        print(f"❌ Payload file not found: {payload_path}")
        sys.exit(1)
    
    try:
        with open(payload_path, 'r') as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing payload file: {e}")
        sys.exit(1)
    
    # Update the payload
    print(f"🔄 Updating image URLs with base: {base_url}")
    updated_payload = update_image_urls(payload, base_url)
    
    # Write output
    output_path = project_root / (args.output or args.payload)
    try:
        with open(output_path, 'w') as f:
            json.dump(updated_payload, f, indent=4)
        print(f"💾 Saved updated payload to: {output_path}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()