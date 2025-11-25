#!/usr/bin/env python3
"""
Coveo Commerce API Load Operations Script

This script allows you to easily perform load and update operations against
the Coveo Commerce API using payload files from the 'Test payloads' folder.

Based on: https://docs.coveo.com/en/p4eb0129/coveo-for-commerce/full-catalog-data-updates
"""

import json
import os
import sys
import argparse
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin


class CoveoLoader:
    """Handles Coveo Commerce API operations for catalog data updates."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the loader with configuration."""
        # Handle both relative and absolute paths for config
        if not os.path.isabs(config_path):
            # Look for config in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / config_path
        
        self.config = self._load_config(config_path)
        self.base_url = "https://api.cloud.coveo.com/push/v1"
        
        # Set data directory relative to project root
        project_root = Path(__file__).parent.parent
        self.test_payloads_dir = project_root / "data"
        
        # Validate required configuration
        required_keys = ["organization_id", "source_id", "access_token"]
        missing_keys = [key for key in required_keys if not self.config.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file '{config_path}' not found.")
            print("Please create a config.json file with your Coveo settings.")
            print("See config.template.json for an example.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            "Content-Type": content_type,
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config['access_token']}"
        }
    
    def _handle_api_error(self, response: requests.Response, operation: str):
        """Handle API errors with meaningful messages."""
        if response.status_code == 401:
            print(f"❌ Authentication failed. Please check your access token.")
        elif response.status_code == 403:
            print(f"❌ Access forbidden. Check your API key privileges.")
        elif response.status_code == 404:
            print(f"❌ Resource not found. Check your organization ID and source ID.")
        elif response.status_code == 413:
            print(f"❌ Payload too large (>256 MB). Consider splitting your data.")
        elif response.status_code == 429:
            print(f"❌ Rate limit exceeded. Please wait and try again.")
            if 'retry-after' in response.headers:
                print(f"   Retry after {response.headers['retry-after']} seconds.")
        else:
            print(f"❌ {operation} failed with status {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text[:500]}")
        
        response.raise_for_status()
    
    def list_payload_files(self) -> List[str]:
        """List available payload files."""
        if not self.test_payloads_dir.exists():
            print(f"❌ Test payloads directory not found: {self.test_payloads_dir}")
            return []
        
        payload_files = [f.name for f in self.test_payloads_dir.glob("*.json")]
        if not payload_files:
            print(f"❌ No JSON payload files found in {self.test_payloads_dir}")
        
        return sorted(payload_files)
    
    def load_payload_file(self, filename: str) -> Dict[str, Any]:
        """Load and validate a payload file."""
        file_path = self.test_payloads_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Payload file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Loaded payload file: {filename}")
            
            # Display payload info
            if "addOrUpdate" in data:
                add_count = len(data["addOrUpdate"])
                print(f"   📦 Items to add/update: {add_count}")
                
                # Show object type distribution
                object_types = {}
                for item in data["addOrUpdate"]:
                    obj_type = item.get("objecttype", "Unknown")
                    object_types[obj_type] = object_types.get(obj_type, 0) + 1
                
                for obj_type, count in object_types.items():
                    print(f"      • {obj_type}: {count}")
            
            if "delete" in data:
                delete_count = len(data["delete"])
                print(f"   🗑️  Items to delete: {delete_count}")
            
            # Normalize case for API consistency
            if "AddOrUpdate" in data:
                data["addOrUpdate"] = data.pop("AddOrUpdate")
            if "Delete" in data:
                data["delete"] = data.pop("Delete")
                
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in payload file: {e}")
    
    def create_file_container(self, use_virtual_hosted_style: bool = True) -> Dict[str, Any]:
        """Create a file container for update operations."""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/files"
        params = {"useVirtualHostedStyleUrl": str(use_virtual_hosted_style).lower()}
        
        print("📋 Creating file container...")
        response = requests.post(url, headers=self._get_headers(), params=params)
        
        try:
            self._handle_api_error(response, "File container creation")
        except requests.HTTPError:
            return {}
        
        container_data = response.json()
        print(f"✅ File container created with ID: {container_data['fileId']}")
        return container_data
    
    def upload_to_container(self, container_data: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Upload payload to the file container."""
        upload_uri = container_data["uploadUri"]
        required_headers = container_data["requiredHeaders"]
        
        print("📤 Uploading payload to container...")
        
        # Convert payload to JSON bytes
        payload_data = json.dumps(payload, indent=2).encode('utf-8')
        
        response = requests.put(upload_uri, data=payload_data, headers=required_headers)
        
        try:
            self._handle_api_error(response, "Payload upload")
            print(f"✅ Payload uploaded successfully ({len(payload_data)} bytes)")
            return True
        except requests.HTTPError:
            return False
    
    def update_source(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Send file container to update the source."""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/sources/{self.config['source_id']}/stream/update"
        params = {"fileId": file_id}
        
        print("🔄 Sending update to source...")
        response = requests.put(url, headers=self._get_headers(), params=params, json={})
        
        try:
            self._handle_api_error(response, "Source update")
        except requests.HTTPError:
            return None
        
        result = response.json()
        print(f"✅ Update sent successfully!")
        print(f"   📋 Request ID: {result.get('requestId', 'N/A')}")
        print(f"   🔢 Ordering ID: {result.get('orderingId', 'N/A')}")
        
        return result
    
    def delete_old_items(self, ordering_id: int) -> bool:
        """Delete items older than the specified ordering ID."""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/sources/{self.config['source_id']}/stream/deleteolderthan/{ordering_id}"
        
        print("🗑️  Deleting old items...")
        response = requests.post(url, headers=self._get_headers())
        
        try:
            self._handle_api_error(response, "Delete old items")
            print("✅ Old items deletion request sent successfully!")
            return True
        except requests.HTTPError:
            return False
    
    def open_stream(self) -> Optional[Dict[str, Any]]:
        """Open a stream for load operations."""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/sources/{self.config['source_id']}/stream/open"
        
        print("🔓 Opening stream...")
        response = requests.post(url, headers=self._get_headers())
        
        try:
            self._handle_api_error(response, "Stream open")
        except requests.HTTPError:
            return None
        
        stream_data = response.json()
        print(f"✅ Stream opened with ID: {stream_data['streamId']}")
        return stream_data
    
    def upload_to_stream(self, stream_data: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Upload payload to the open stream."""
        upload_uri = stream_data["uploadUri"]
        required_headers = stream_data["requiredHeaders"]
        
        print("📤 Uploading payload to stream...")
        
        # Convert payload to JSON bytes
        payload_data = json.dumps(payload, indent=2).encode('utf-8')
        
        response = requests.put(upload_uri, data=payload_data, headers=required_headers)
        
        try:
            self._handle_api_error(response, "Stream upload")
            print(f"✅ Payload uploaded to stream successfully ({len(payload_data)} bytes)")
            return True
        except requests.HTTPError:
            return False
    
    def close_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Close the stream and complete the load operation."""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/sources/{self.config['source_id']}/stream/{stream_id}/close"
        
        print("🔒 Closing stream...")
        response = requests.post(url, headers=self._get_headers())
        
        try:
            self._handle_api_error(response, "Stream close")
        except requests.HTTPError:
            return None
        
        result = response.json()
        print(f"✅ Stream closed successfully!")
        print(f"   📋 Request ID: {result.get('requestId', 'N/A')}")
        print(f"   🔢 Ordering ID: {result.get('orderingId', 'N/A')}")
        
        return result
    
    def perform_update_operation(self, payload: Dict[str, Any], delete_old: bool = False) -> bool:
        """Perform a complete update operation."""
        print("\n🚀 Starting UPDATE operation...")
        print("=" * 50)
        
        # Step 1: Create file container
        container_data = self.create_file_container()
        if not container_data:
            return False
        
        # Step 2: Upload payload
        if not self.upload_to_container(container_data, payload):
            return False
        
        # Step 3: Update source
        result = self.update_source(container_data["fileId"])
        if not result:
            return False
        
        # Step 4: Delete old items (optional)
        if delete_old:
            ordering_id = result.get("orderingId")
            if ordering_id:
                self.delete_old_items(ordering_id)
        
        print("\n✅ UPDATE operation completed successfully!")
        return True
    
    def perform_load_operation(self, payload: Dict[str, Any]) -> bool:
        """Perform a complete load operation."""
        print("\n🚀 Starting LOAD operation...")
        print("⚠️  Warning: This will replace ALL existing data in your source!")
        print("=" * 50)
        
        # Step 1: Open stream
        stream_data = self.open_stream()
        if not stream_data:
            return False
        
        stream_id = stream_data["streamId"]
        
        try:
            # Step 2: Upload payload
            if not self.upload_to_stream(stream_data, payload):
                return False
            
            # Step 3: Close stream
            result = self.close_stream(stream_id)
            if not result:
                return False
            
            print("\n✅ LOAD operation completed successfully!")
            print("📝 Note: Expect a 15-minute delay for old item removal from the index.")
            return True
            
        except Exception as e:
            print(f"❌ Error during load operation: {e}")
            print(f"⚠️  Stream {stream_id} may need manual cleanup")
            return False
    
    def interactive_mode(self):
        """Run in interactive mode for file selection."""
        print("🎯 Coveo Commerce API Loader")
        print("=" * 40)
        
        # List available payload files
        payload_files = self.list_payload_files()
        if not payload_files:
            return
        
        print("\n📁 Available payload files:")
        for i, filename in enumerate(payload_files, 1):
            print(f"   {i}. {filename}")
        
        # File selection
        try:
            choice = input(f"\nSelect a file (1-{len(payload_files)}): ").strip()
            file_index = int(choice) - 1
            
            if not 0 <= file_index < len(payload_files):
                print("❌ Invalid selection.")
                return
            
            selected_file = payload_files[file_index]
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Operation cancelled.")
            return
        
        # Operation selection
        print("\n🔧 Select operation type:")
        print("   1. Update (recommended - safer, preserves existing data)")
        print("   2. Load (replaces ALL data in source)")
        
        try:
            op_choice = input("\nSelect operation (1-2): ").strip()
            
            if op_choice == "1":
                operation = "update"
                # Ask about deleting old items
                delete_old = input("\nDelete old items after update? (y/N): ").strip().lower() == 'y'
            elif op_choice == "2":
                operation = "load"
                delete_old = False
                # Confirmation for load operation
                confirm = input("\n⚠️  Are you sure you want to REPLACE ALL data? (type 'yes'): ").strip()
                if confirm != "yes":
                    print("❌ Operation cancelled.")
                    return
            else:
                print("❌ Invalid selection.")
                return
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled.")
            return
        
        # Load and execute
        try:
            payload = self.load_payload_file(selected_file)
            
            if operation == "update":
                success = self.perform_update_operation(payload, delete_old)
            else:
                success = self.perform_load_operation(payload)
            
            if success:
                print(f"\n🎉 {operation.upper()} operation completed successfully!")
                print("📊 Check the Coveo Administration Console to monitor indexing progress.")
            else:
                print(f"\n❌ {operation.upper()} operation failed.")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Coveo Commerce API Loader")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--file", help="Payload file to load")
    parser.add_argument("--operation", choices=["update", "load"], default="update",
                       help="Operation type (default: update)")
    parser.add_argument("--delete-old", action="store_true",
                       help="Delete old items after update operation")
    parser.add_argument("--list", action="store_true", help="List available payload files")
    
    args = parser.parse_args()
    
    try:
        loader = CoveoLoader(args.config)
        
        if args.list:
            print("📁 Available payload files:")
            files = loader.list_payload_files()
            for filename in files:
                print(f"   • {filename}")
            return
        
        if args.file:
            # Command-line mode
            try:
                payload = loader.load_payload_file(args.file)
                
                if args.operation == "update":
                    success = loader.perform_update_operation(payload, args.delete_old)
                else:
                    success = loader.perform_load_operation(payload)
                
                sys.exit(0 if success else 1)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
        else:
            # Interactive mode
            loader.interactive_mode()
    
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()