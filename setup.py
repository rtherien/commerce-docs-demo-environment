#!/usr/bin/env python3
"""
Setup script for Coveo Catalog Management Tool

This script helps you set up the tool with your Coveo credentials and validates
that everything is working correctly.
"""

import json
import os
import sys

def create_config_file():
    """Create the configuration file with user input."""
    print("🔧 Setting up Coveo Configuration")
    print("=" * 50)
    
    config = {
        "coveo": {
            "api_base_url": "https://api.cloud.coveo.com",
            "use_virtual_hosted_style_url": True
        },
        "limits": {
            "max_file_size_mb": 256,
            "max_item_size_mb": 3,
            "api_calls_per_day": 15000,
            "api_calls_per_5min": 250,
            "upload_timeout_minutes": 60
        },
        "default_settings": {
            "chunk_large_files": True,
            "verify_uploads": True,
            "delete_old_items": True,
            "compress_uploads": False,
            "retry_attempts": 3,
            "retry_delay_seconds": 5
        },
        "data_paths": {
            "complete_payload": "data/complete-payload.json",
            "catalog_schema": "data/catalog-schema.json",
            "partial_updates": "data/",
            "temp_directory": "temp/"
        }
    }
    
    print("Please provide your Coveo credentials:")
    print("(You can find these in your Coveo Administration Console)")
    print()
    
    # Get organization ID
    org_id = input("Organization ID: ").strip()
    if not org_id:
        print("❌ Organization ID is required")
        return False
    config["coveo"]["organization_id"] = org_id
    
    # Get API key
    api_key = input("API Key: ").strip()
    if not api_key:
        print("❌ API Key is required")
        return False
    config["coveo"]["api_key"] = api_key
    
    # Get source ID
    source_id = input("Source ID: ").strip()
    if not source_id:
        print("❌ Source ID is required")
        return False
    config["coveo"]["source_id"] = source_id
    
    # Create config directory if it doesn't exist
    os.makedirs("config", exist_ok=True)
    
    # Write configuration file
    config_path = "config/coveo-config.json"
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False


def test_configuration():
    """Test the configuration by connecting to the API."""
    print("\n🧪 Testing API Connection")
    print("=" * 50)
    
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from coveo_utils import CoveoAPIClient, validate_config
        
        # Validate configuration
        if not validate_config("config/coveo-config.json"):
            print("❌ Configuration validation failed")
            return False
        
        print("✅ Configuration file is valid")
        
        # Test API connection
        print("🔌 Testing API connection...")
        client = CoveoAPIClient("config/coveo-config.json")
        
        # Create a test file container (doesn't upload anything)
        upload_uri, file_id, headers = client.create_file_container()
        print("✅ API connection successful!")
        print(f"📦 Test file container created: {file_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("\nPlease check:")
        print("- Your organization ID is correct")
        print("- Your API key has the required permissions")
        print("- Your source ID exists and is accessible")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking Dependencies")
    print("=" * 50)
    
    try:
        import requests
        print("✅ requests library is available")
        return True
    except ImportError:
        print("❌ requests library is missing")
        print("Please install it with: pip install requests")
        return False


def show_next_steps():
    """Show the user what they can do next."""
    print("\n🚀 Setup Complete! What's Next?")
    print("=" * 50)
    
    print("\n1. List your data files:")
    print("   python coveo_catalog_tool.py list")
    
    print("\n2. Validate your data:")
    print("   python coveo_catalog_tool.py validate --file data/complete-payload.json")
    
    print("\n3. Try a full catalog update:")
    print("   python coveo_catalog_tool.py full-update --file data/complete-payload.json")
    
    print("\n4. Try a partial update:")
    print("   python coveo_catalog_tool.py partial-update --file data/sample-partial-updates.json")
    
    print("\n5. Monitor operations:")
    print("   python coveo_catalog_tool.py status --last-hour")
    
    print("\n📚 Read the full README.md for more examples and advanced usage!")


def main():
    """Main setup function."""
    print("🎯 Coveo Catalog Management Tool Setup")
    print("=" * 60)
    
    # Check if config already exists
    if os.path.exists("config/coveo-config.json"):
        print("⚠️  Configuration file already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and run setup again.")
        sys.exit(1)
    
    # Create configuration
    if not create_config_file():
        print("\n❌ Configuration setup failed.")
        sys.exit(1)
    
    # Test configuration
    if not test_configuration():
        print("\n❌ API test failed. Please check your configuration.")
        print("You can re-run this setup script or edit config/coveo-config.json manually.")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Setup completed successfully!")


if __name__ == "__main__":
    main()