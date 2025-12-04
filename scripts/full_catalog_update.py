#!/usr/bin/env python3
"""
Full Catalog Data Update Script

This script handles full catalog data updates to Coveo using the Stream API.
It supports large file uploads with automatic chunking and can reference your
existing data files like data/complete-payload.json.

Usage:
    python full_catalog_update.py --file data/complete-payload.json
    python full_catalog_update.py --file data/complete-payload.json --delete-old
    python full_catalog_update.py --file data/complete-payload.json --no-verify
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Optional

# Add the src directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from coveo_utils import CoveoUploader, CoveoAPIClient, validate_config, format_file_size


def normalize_json_format(json_data: Dict) -> Dict:
    """
    Normalize JSON format to match Coveo API expectations.
    
    The API expects specific key casing (addOrUpdate vs AddOrUpdate).
    This function converts your data format to the API format.
    """
    normalized = {}
    
    # Handle different casing variations
    if "AddOrUpdate" in json_data:
        normalized["addOrUpdate"] = json_data["AddOrUpdate"]
    elif "addOrUpdate" in json_data:
        normalized["addOrUpdate"] = json_data["addOrUpdate"]
    
    if "Delete" in json_data:
        normalized["delete"] = json_data["Delete"]
    elif "delete" in json_data:
        normalized["delete"] = json_data["delete"]
    
    # Normalize item fields
    items = normalized.get("addOrUpdate", [])
    for item in items:
        # Ensure required fields are present and properly formatted
        if "DocumentId" in item and "documentId" not in item:
            item["documentId"] = item["DocumentId"]
        
        if "ObjectType" in item and "objecttype" not in item:
            item["objecttype"] = item["ObjectType"]
    
    return normalized


def validate_catalog_data(json_data: Dict) -> bool:
    """Validate catalog data format and required fields."""
    
    if not isinstance(json_data, dict):
        print("Error: Data must be a JSON object")
        return False
    
    # Check for required structure
    has_items = False
    for key in ["addOrUpdate", "AddOrUpdate", "addOrMerge"]:
        if key in json_data:
            has_items = True
            items = json_data[key]
            
            if not isinstance(items, list):
                print(f"Error: {key} must be an array")
                return False
            
            # Validate items
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    print(f"Error: Item {i} must be an object")
                    return False
                
                # Check for document ID (either casing)
                doc_id = item.get("documentId") or item.get("DocumentId")
                if not doc_id:
                    print(f"Error: Item {i} missing documentId/DocumentId")
                    return False
                
                # Check for object type (either casing)
                obj_type = item.get("objecttype") or item.get("ObjectType")
                if not obj_type:
                    print(f"Error: Item {i} missing objecttype/ObjectType")
                    return False
            
            break
    
    if not has_items:
        print("Error: No items found. Expected 'addOrUpdate' or 'AddOrUpdate' array")
        return False
    
    return True


def perform_full_update(file_path: str, delete_old: bool = True, 
                       verify_upload: bool = True) -> bool:
    """
    Perform a full catalog update.
    
    Args:
        file_path: Path to the JSON file containing catalog data
        delete_old: Whether to delete old items after update
        verify_upload: Whether to verify the upload was successful
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Starting full catalog update from: {file_path}")
    
    # Validate file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {format_file_size(file_size)}")
    
    try:
        # Load and validate data
        print("Loading and validating catalog data...")
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if not validate_catalog_data(json_data):
            return False
        
        # Normalize format for API
        json_data = normalize_json_format(json_data)
        
        # Count items
        item_count = len(json_data.get("addOrUpdate", []))
        delete_count = len(json_data.get("delete", []))
        print(f"Items to add/update: {item_count}")
        if delete_count > 0:
            print(f"Items to delete: {delete_count}")
        
        # Initialize uploader
        uploader = CoveoUploader()
        
        # Perform upload
        print("\nUploading to Coveo...")
        result = uploader.upload_json_data(json_data, operation_type="update")
        
        if not result["success"]:
            print("Upload failed!")
            return False
        
        print(f"\nUpload completed successfully!")
        print(f"Chunks uploaded: {result['chunks']}")
        print(f"Ordering IDs: {result['ordering_ids']}")
        print(f"Request IDs: {result['request_ids']}")
        
        # Delete old items if requested
        if delete_old and result["ordering_ids"]:
            print("\nDeleting old items...")
            first_ordering_id = result["ordering_ids"][0]
            try:
                uploader.client.delete_old_items(first_ordering_id)
                print("Old items deletion initiated")
            except Exception as e:
                print(f"Warning: Failed to delete old items: {e}")
        
        # Verify upload if requested
        if verify_upload:
            print("\nWaiting for indexing to complete...")
            success = verify_upload_success(uploader.client, result)
            if success:
                print("✓ Upload verification successful")
            else:
                print("⚠ Upload verification found warnings or errors")
                return False
        
        print(f"\n✓ Full catalog update completed successfully!")
        print(f"  - Start time: {result['start_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  - Items processed: {item_count}")
        print(f"  - Chunks uploaded: {result['chunks']}")
        
        return True
        
    except Exception as e:
        print(f"Error during full update: {e}")
        return False


def verify_upload_success(client: CoveoAPIClient, result: Dict, 
                         wait_minutes: int = 5) -> bool:
    """
    Verify that the upload was successful by checking logs.
    
    Args:
        client: Coveo API client
        result: Upload result from the uploader
        wait_minutes: How long to wait for processing
        
    Returns:
        True if verification passed, False if there were errors
    """
    import time
    
    # Wait for processing
    print(f"Waiting {wait_minutes} minutes for processing...")
    time.sleep(wait_minutes * 60)
    
    start_time = result["start_time"]
    end_time = datetime.now(timezone.utc)
    
    try:
        # Check batch acceptance
        print("Checking batch acceptance...")
        batch_logs = client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["BATCH_FILE"],
            results=["COMPLETED", "WARNING"]
        )
        
        batch_success = True
        for ordering_id in result["ordering_ids"]:
            found_batch = False
            for log in batch_logs:
                if log.get("meta", {}).get("orderingid") == ordering_id:
                    found_batch = True
                    if log.get("result") == "WARNING":
                        print(f"⚠ Batch warning for ordering ID {ordering_id}: {log.get('meta', {}).get('error', 'Unknown error')}")
                        batch_success = False
                    elif log.get("result") == "COMPLETED":
                        print(f"✓ Batch {ordering_id} accepted successfully")
                    break
            
            if not found_batch:
                print(f"⚠ No batch log found for ordering ID {ordering_id}")
                batch_success = False
        
        # Check individual item processing
        print("Checking item processing...")
        item_logs = client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["UPDATE"],
            results=["WARNING"]
        )
        
        if not item_logs:
            print("✓ No item processing warnings found")
            return batch_success
        else:
            print(f"⚠ Found {len(item_logs)} item processing warnings:")
            for log in item_logs:
                error = log.get("meta", {}).get("error", "Unknown error")
                doc_id = log.get("id", "Unknown document")
                print(f"  - {doc_id}: {error}")
            return False
        
    except Exception as e:
        print(f"Warning: Could not verify upload: {e}")
        return True  # Don't fail the upload due to verification issues


def main():
    """Main function to handle command line execution."""
    parser = argparse.ArgumentParser(
        description="Perform full catalog data updates to Coveo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file data/complete-payload.json
  %(prog)s --file data/complete-payload.json --delete-old
  %(prog)s --file data/complete-payload.json --no-verify
  %(prog)s --file data/my-products.json --no-delete-old --verify
        """
    )
    
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to JSON file containing catalog data"
    )
    
    parser.add_argument(
        "--delete-old",
        action="store_true",
        default=True,
        help="Delete old items after update (default: True)"
    )
    
    parser.add_argument(
        "--no-delete-old",
        action="store_true",
        help="Don't delete old items after update"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true", 
        default=True,
        help="Verify upload success (default: True)"
    )
    
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip upload verification"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/coveo-config.json",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Handle conflicting options
    delete_old = args.delete_old and not args.no_delete_old
    verify_upload = args.verify and not args.no_verify
    
    # Validate configuration
    if not validate_config(args.config):
        print("Configuration validation failed. Please check your config file.")
        sys.exit(1)
    
    # Perform the update
    success = perform_full_update(
        file_path=args.file,
        delete_old=delete_old,
        verify_upload=verify_upload
    )
    
    if success:
        print("\n🎉 Full catalog update completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Full catalog update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()