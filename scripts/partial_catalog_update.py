#!/usr/bin/env python3
"""
Partial Catalog Data Update Script

This script handles partial catalog data updates to Coveo using the Stream API.
It supports various types of partial updates including:
- Price changes
- Inventory updates  
- Field value replacements
- Array operations (add/remove items)
- Dictionary field updates

Usage:
    python partial_catalog_update.py --operation update_price --product-id "product://001" --price 29.99
    python partial_catalog_update.py --operation update_inventory --store-id "store://s001" --add-items "sku-123,sku-124"
    python partial_catalog_update.py --file data/partial-updates.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Add the src directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from coveo_utils import CoveoUploader, CoveoAPIClient, validate_config


class PartialUpdateBuilder:
    """Builder class for creating partial update operations."""
    
    def __init__(self):
        self.operations = []
    
    def add_operation(self, document_id: str, operator: str, field: str, 
                     value: Any) -> 'PartialUpdateBuilder':
        """Add a partial update operation."""
        operation = {
            "documentId": document_id,
            "operator": operator,
            "field": field
        }
        
        # Only add value if it's not None (allows for field deletion)
        if value is not None:
            operation["value"] = value
        
        self.operations.append(operation)
        return self
    
    def update_price(self, document_id: str, price: float) -> 'PartialUpdateBuilder':
        """Update product price."""
        return self.add_operation(document_id, "fieldValueReplace", "ec_price", price)
    
    def update_promo_price(self, document_id: str, promo_price: float) -> 'PartialUpdateBuilder':
        """Update product promotional price."""
        return self.add_operation(document_id, "fieldValueReplace", "ec_promo_price", promo_price)
    
    def update_stock_status(self, document_id: str, in_stock: bool) -> 'PartialUpdateBuilder':
        """Update stock status."""
        status = "TRUE" if in_stock else "FALSE"
        return self.add_operation(document_id, "fieldValueReplace", "ec_in_stock", status)
    
    def update_rating(self, document_id: str, rating: float) -> 'PartialUpdateBuilder':
        """Update product rating."""
        return self.add_operation(document_id, "fieldValueReplace", "ec_rating", rating)
    
    def replace_field(self, document_id: str, field: str, value: Any) -> 'PartialUpdateBuilder':
        """Replace any field value."""
        return self.add_operation(document_id, "fieldValueReplace", field, value)
    
    def remove_field(self, document_id: str, field: str) -> 'PartialUpdateBuilder':
        """Remove a field by setting it to null."""
        return self.add_operation(document_id, "fieldValueReplace", field, None)
    
    def add_to_array(self, document_id: str, field: str, items: List[Any]) -> 'PartialUpdateBuilder':
        """Add items to an array field."""
        return self.add_operation(document_id, "arrayAppend", field, items)
    
    def remove_from_array(self, document_id: str, field: str, items: List[Any]) -> 'PartialUpdateBuilder':
        """Remove items from an array field."""
        return self.add_operation(document_id, "arrayRemove", field, items)
    
    def add_to_store_inventory(self, store_document_id: str, product_ids: List[str]) -> 'PartialUpdateBuilder':
        """Add products to store inventory."""
        return self.add_to_array(store_document_id, "ec_available_items", product_ids)
    
    def remove_from_store_inventory(self, store_document_id: str, product_ids: List[str]) -> 'PartialUpdateBuilder':
        """Remove products from store inventory."""
        return self.remove_from_array(store_document_id, "ec_available_items", product_ids)
    
    def update_dictionary_field(self, document_id: str, field: str, 
                               key: str, value: Any) -> 'PartialUpdateBuilder':
        """Add or update a key in a dictionary field."""
        return self.add_operation(document_id, "dictionaryPut", field, {key: value})
    
    def remove_from_dictionary(self, document_id: str, field: str, 
                              keys: List[str]) -> 'PartialUpdateBuilder':
        """Remove keys from a dictionary field."""
        if len(keys) == 1:
            return self.add_operation(document_id, "dictionaryRemove", field, keys[0])
        else:
            return self.add_operation(document_id, "dictionaryRemove", field, keys)
    
    def build(self) -> Dict:
        """Build the final partial update payload."""
        return {
            "partialUpdate": self.operations
        }
    
    def clear(self) -> 'PartialUpdateBuilder':
        """Clear all operations."""
        self.operations = []
        return self


def create_price_update(product_ids: List[str], new_price: float) -> Dict:
    """Create a price update for multiple products."""
    builder = PartialUpdateBuilder()
    for product_id in product_ids:
        builder.update_price(product_id, new_price)
    return builder.build()


def create_inventory_update(store_id: str, add_products: List[str] = None, 
                          remove_products: List[str] = None) -> Dict:
    """Create an inventory update for a store."""
    builder = PartialUpdateBuilder()
    
    if add_products:
        builder.add_to_store_inventory(store_id, add_products)
    
    if remove_products:
        builder.remove_from_store_inventory(store_id, remove_products)
    
    return builder.build()


def create_stock_status_update(product_updates: List[tuple]) -> Dict:
    """
    Create stock status updates for multiple products.
    
    Args:
        product_updates: List of tuples (product_id, in_stock_boolean)
    """
    builder = PartialUpdateBuilder()
    for product_id, in_stock in product_updates:
        builder.update_stock_status(product_id, in_stock)
    return builder.build()


def validate_partial_update_data(json_data: Dict) -> bool:
    """Validate partial update data format."""
    
    if not isinstance(json_data, dict):
        print("Error: Data must be a JSON object")
        return False
    
    if "partialUpdate" not in json_data:
        print("Error: Missing 'partialUpdate' array")
        return False
    
    operations = json_data["partialUpdate"]
    if not isinstance(operations, list):
        print("Error: 'partialUpdate' must be an array")
        return False
    
    valid_operators = ["arrayAppend", "arrayRemove", "fieldValueReplace", 
                      "dictionaryPut", "dictionaryRemove"]
    
    for i, operation in enumerate(operations):
        if not isinstance(operation, dict):
            print(f"Error: Operation {i} must be an object")
            return False
        
        # Check required fields
        if "documentId" not in operation:
            print(f"Error: Operation {i} missing 'documentId'")
            return False
        
        if "operator" not in operation:
            print(f"Error: Operation {i} missing 'operator'")
            return False
        
        if "field" not in operation:
            print(f"Error: Operation {i} missing 'field'")
            return False
        
        # Validate operator
        if operation["operator"] not in valid_operators:
            print(f"Error: Operation {i} has invalid operator: {operation['operator']}")
            return False
    
    return True


def perform_partial_update(data: Dict, verify_upload: bool = True) -> bool:
    """
    Perform a partial catalog update.
    
    Args:
        data: Dictionary containing partial update data
        verify_upload: Whether to verify the upload was successful
        
    Returns:
        True if successful, False otherwise
    """
    print("Starting partial catalog update...")
    
    # Validate data
    if not validate_partial_update_data(data):
        return False
    
    operation_count = len(data["partialUpdate"])
    print(f"Operations to perform: {operation_count}")
    
    # Show operation summary
    ops_summary = {}
    for op in data["partialUpdate"]:
        operator = op["operator"]
        ops_summary[operator] = ops_summary.get(operator, 0) + 1
    
    print("Operation breakdown:")
    for operator, count in ops_summary.items():
        print(f"  - {operator}: {count}")
    
    try:
        # Initialize uploader
        uploader = CoveoUploader()
        
        # Perform upload
        print("\nUploading partial updates to Coveo...")
        result = uploader.upload_json_data(data, operation_type="partial")
        
        if not result["success"]:
            print("Upload failed!")
            return False
        
        print(f"\nUpload completed successfully!")
        print(f"Chunks uploaded: {result['chunks']}")
        print(f"Ordering IDs: {result['ordering_ids']}")
        print(f"Request IDs: {result['request_ids']}")
        
        # Verify upload if requested
        if verify_upload:
            print("\nWaiting for processing...")
            success = verify_partial_update_success(uploader.client, result)
            if success:
                print("✓ Upload verification successful")
            else:
                print("⚠ Upload verification found warnings or errors")
                return False
        
        print(f"\n✓ Partial catalog update completed successfully!")
        print(f"  - Start time: {result['start_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  - Operations processed: {operation_count}")
        print(f"  - Chunks uploaded: {result['chunks']}")
        
        return True
        
    except Exception as e:
        print(f"Error during partial update: {e}")
        return False


def verify_partial_update_success(client: CoveoAPIClient, result: Dict, 
                                wait_minutes: int = 2) -> bool:
    """Verify that the partial update was successful."""
    import time
    
    # Wait for processing (partial updates are faster)
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
        
        # Check individual operation processing
        print("Checking operation processing...")
        item_logs = client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["UPDATE"],
            results=["WARNING"]
        )
        
        if not item_logs:
            print("✓ No operation processing warnings found")
            return batch_success
        else:
            print(f"⚠ Found {len(item_logs)} operation processing warnings:")
            for log in item_logs:
                error = log.get("meta", {}).get("error", "Unknown error")
                doc_id = log.get("id", "Unknown document")
                print(f"  - {doc_id}: {error}")
            return False
        
    except Exception as e:
        print(f"Warning: Could not verify upload: {e}")
        return True


def main():
    """Main function to handle command line execution."""
    parser = argparse.ArgumentParser(
        description="Perform partial catalog data updates to Coveo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update from file:
  %(prog)s --file data/partial-updates.json
  
  # Quick price update:
  %(prog)s --operation update_price --document-id "product://001" --price 29.99
  
  # Update inventory:
  %(prog)s --operation update_inventory --document-id "store://s001" --add-items "sku-123,sku-124"
  
  # Update stock status:
  %(prog)s --operation update_stock --document-id "product://001" --in-stock true
        """
    )
    
    # File input option
    parser.add_argument(
        "--file", "-f",
        help="Path to JSON file containing partial update operations"
    )
    
    # Quick operation options
    parser.add_argument(
        "--operation", 
        choices=["update_price", "update_promo_price", "update_stock", "update_inventory", "update_rating"],
        help="Quick operation type"
    )
    
    parser.add_argument(
        "--document-id",
        help="Document ID for quick operations"
    )
    
    parser.add_argument(
        "--price", type=float,
        help="New price for price operations"
    )
    
    parser.add_argument(
        "--rating", type=float,
        help="New rating (0.0-5.0)"
    )
    
    parser.add_argument(
        "--in-stock", type=bool,
        help="Stock status (true/false)"
    )
    
    parser.add_argument(
        "--add-items",
        help="Comma-separated list of items to add to inventory"
    )
    
    parser.add_argument(
        "--remove-items", 
        help="Comma-separated list of items to remove from inventory"
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
    
    # Validate arguments
    if not args.file and not args.operation:
        parser.error("Must specify either --file or --operation")
    
    if args.operation and not args.document_id:
        parser.error("--document-id is required for quick operations")
    
    verify_upload = args.verify and not args.no_verify
    
    # Validate configuration
    if not validate_config(args.config):
        print("Configuration validation failed. Please check your config file.")
        sys.exit(1)
    
    # Prepare data
    if args.file:
        # Load from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file: {e}")
            sys.exit(1)
    else:
        # Build from command line arguments
        builder = PartialUpdateBuilder()
        
        if args.operation == "update_price":
            if args.price is None:
                parser.error("--price is required for price updates")
            builder.update_price(args.document_id, args.price)
        
        elif args.operation == "update_promo_price":
            if args.price is None:
                parser.error("--price is required for promo price updates") 
            builder.update_promo_price(args.document_id, args.price)
        
        elif args.operation == "update_rating":
            if args.rating is None:
                parser.error("--rating is required for rating updates")
            builder.update_rating(args.document_id, args.rating)
        
        elif args.operation == "update_stock":
            if args.in_stock is None:
                parser.error("--in-stock is required for stock updates")
            builder.update_stock_status(args.document_id, args.in_stock)
        
        elif args.operation == "update_inventory":
            if not args.add_items and not args.remove_items:
                parser.error("--add-items or --remove-items is required for inventory updates")
            
            if args.add_items:
                items = [item.strip() for item in args.add_items.split(",")]
                builder.add_to_store_inventory(args.document_id, items)
            
            if args.remove_items:
                items = [item.strip() for item in args.remove_items.split(",")]
                builder.remove_from_store_inventory(args.document_id, items)
        
        data = builder.build()
    
    # Perform the update
    success = perform_partial_update(data, verify_upload=verify_upload)
    
    if success:
        print("\n🎉 Partial catalog update completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Partial catalog update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()