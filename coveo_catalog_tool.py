#!/usr/bin/env python3
"""
Coveo Catalog Management Tool

Main interface script that provides a unified command-line tool for managing
your Coveo catalog data. This script can reference files in your repo like
data/complete-payload.json and provides easy access to all catalog operations.

Usage:
    python coveo_catalog_tool.py full-update --file data/complete-payload.json
    python coveo_catalog_tool.py partial-update --operation update_price --document-id "product://001" --price 29.99
    python coveo_catalog_tool.py monitor --ordering-id 1716387965000
    python coveo_catalog_tool.py status --last-hour
"""

import argparse
import os
import sys
import json
from datetime import datetime, timezone, timedelta

# Add the src directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from coveo_utils import CoveoUploader, CoveoAPIClient, validate_config, format_file_size
except ImportError:
    print("Error: Could not import coveo_utils. Make sure you're running from the correct directory.")
    sys.exit(1)

# Import other modules
sys.path.append(os.path.dirname(__file__))

def setup_workspace():
    """Set up the workspace and validate configuration."""
    config_path = "config/coveo-config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("\nTo get started:")
        print("1. Copy config/coveo-config.json.example to config/coveo-config.json")
        print("2. Update the configuration with your Coveo credentials")
        return False
    
    if not validate_config(config_path):
        print("❌ Configuration validation failed")
        print("\nPlease check your configuration file and ensure:")
        print("- organization_id is set to your Coveo organization ID")
        print("- api_key is set to a valid Coveo API key") 
        print("- source_id is set to your catalog source ID")
        return False
    
    return True


def list_data_files():
    """List available data files in the workspace."""
    print("📁 Available data files:")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("  No data directory found")
        return
    
    for file in os.listdir(data_dir):
        if file.endswith('.json'):
            file_path = os.path.join(data_dir, file)
            size = format_file_size(os.path.getsize(file_path))
            print(f"  📄 {file} ({size})")


def check_file_compatibility(file_path: str) -> bool:
    """Check if a JSON file is compatible with Coveo."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check for required structure
        has_items = False
        for key in ["addOrUpdate", "AddOrUpdate", "partialUpdate", "addOrMerge"]:
            if key in data:
                has_items = True
                break
        
        if not has_items:
            print(f"⚠️  File {file_path} doesn't appear to contain catalog data")
            return False
        
        print(f"✅ File {file_path} appears to be compatible")
        return True
        
    except Exception as e:
        print(f"❌ Error checking file {file_path}: {e}")
        return False


def cmd_full_update(args):
    """Handle full catalog update command."""
    from scripts.full_catalog_update import perform_full_update
    
    if not setup_workspace():
        return False
    
    print("🚀 Starting Full Catalog Update")
    print("=" * 50)
    
    # Check file exists and is compatible
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        print("\n📁 Available files:")
        list_data_files()
        return False
    
    if not check_file_compatibility(args.file):
        return False
    
    # Perform the update
    success = perform_full_update(
        file_path=args.file,
        delete_old=not args.no_delete_old,
        verify_upload=not args.no_verify
    )
    
    return success


def cmd_partial_update(args):
    """Handle partial catalog update command.""" 
    from scripts.partial_catalog_update import perform_partial_update, PartialUpdateBuilder
    
    if not setup_workspace():
        return False
    
    print("🔄 Starting Partial Catalog Update") 
    print("=" * 50)
    
    # Build update data
    if args.file:
        # Load from file
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    else:
        # Build from command line
        if not args.document_id:
            print("❌ --document-id is required for quick operations")
            return False
        
        builder = PartialUpdateBuilder()
        
        if args.operation == "update_price" and args.price is not None:
            builder.update_price(args.document_id, args.price)
        elif args.operation == "update_stock" and args.in_stock is not None:
            builder.update_stock_status(args.document_id, args.in_stock)
        elif args.operation == "update_rating" and args.rating is not None:
            builder.update_rating(args.document_id, args.rating)
        else:
            print(f"❌ Invalid operation or missing parameters")
            return False
        
        data = builder.build()
    
    # Perform the update
    success = perform_partial_update(data, verify_upload=not args.no_verify)
    return success


def cmd_monitor(args):
    """Handle operation monitoring command."""
    from scripts.monitor_operations import OperationMonitor
    
    if not setup_workspace():
        return False
    
    print("🔍 Monitoring Operations")
    print("=" * 50)
    
    monitor = OperationMonitor()
    
    try:
        if args.ordering_id:
            # Monitor specific operation
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)
            
            result = monitor.monitor_operation(
                ordering_id=args.ordering_id,
                start_time=start_time,
                end_time=end_time,
                wait_minutes=args.wait
            )
            
            # Print results
            from scripts.monitor_operations import print_batch_status, print_item_status
            print(f"🔍 Monitoring Operation {args.ordering_id}")
            print_batch_status(result["batch_status"])
            print_item_status(result["item_processing"])
            
            print(f"\n🎯 Overall Result: {result['result']}")
            print(f"📝 Message: {result['message']}")
            
            return result["result"] in ["SUCCESS", "WARNING"]
        
        else:
            print("❌ --ordering-id is required for monitoring")
            return False
            
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return False


def cmd_status(args):
    """Handle status/summary command."""
    from scripts.monitor_operations import OperationMonitor, print_operation_summary
    
    if not setup_workspace():
        return False
    
    print("📊 Operations Status")
    print("=" * 50)
    
    monitor = OperationMonitor()
    
    # Determine time range
    end_time = datetime.now(timezone.utc)
    
    if args.last_hour:
        start_time = end_time - timedelta(hours=1)
    elif args.last_day:
        start_time = end_time - timedelta(days=1)
    elif args.date:
        try:
            date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
            start_time = datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            return False
    else:
        # Default to last hour
        start_time = end_time - timedelta(hours=1)
    
    try:
        summary = monitor.get_operation_summary(start_time, end_time)
        print_operation_summary(summary)
        return True
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False


def cmd_validate(args):
    """Handle file validation command."""
    if not setup_workspace():
        return False
    
    print("🔍 Validating Data Files")
    print("=" * 50)
    
    if args.file:
        files = [args.file]
    else:
        # Validate all JSON files in data directory
        data_dir = "data"
        if not os.path.exists(data_dir):
            print("❌ No data directory found")
            return False
        
        files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) 
                if f.endswith('.json')]
    
    all_valid = True
    for file_path in files:
        print(f"\n📄 Validating {file_path}:")
        
        if not os.path.exists(file_path):
            print(f"  ❌ File not found")
            all_valid = False
            continue
        
        # Check file size
        size = os.path.getsize(file_path)
        print(f"  📏 Size: {format_file_size(size)}")
        
        if size > 256 * 1024 * 1024:  # 256 MB
            print(f"  ⚠️  File exceeds 256MB limit and will be chunked")
        
        # Check JSON validity and structure
        valid = check_file_compatibility(file_path)
        if not valid:
            all_valid = False
    
    return all_valid


def cmd_config(args):
    """Handle configuration commands."""
    config_path = "config/coveo-config.json"
    
    if args.action == "show":
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Mask sensitive values
                if "api_key" in config.get("coveo", {}):
                    config["coveo"]["api_key"] = "***HIDDEN***"
                
                print("📋 Current Configuration:")
                print(json.dumps(config, indent=2))
                
            except Exception as e:
                print(f"❌ Error reading config: {e}")
                return False
        else:
            print(f"❌ Configuration file not found: {config_path}")
            return False
    
    elif args.action == "validate":
        if validate_config(config_path):
            print("✅ Configuration is valid")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    
    elif args.action == "test":
        if not validate_config(config_path):
            print("❌ Configuration validation failed")
            return False
        
        try:
            print("🔧 Testing API connection...")
            client = CoveoAPIClient(config_path)
            
            # Test by creating a file container (this doesn't upload anything)
            upload_uri, file_id, headers = client.create_file_container()
            print("✅ API connection successful")
            print(f"📦 Test file container created: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    return True


def main():
    """Main function with command parsing."""
    parser = argparse.ArgumentParser(
        description="Coveo Catalog Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full catalog update
  %(prog)s full-update --file data/complete-payload.json
  
  # Partial updates
  %(prog)s partial-update --file data/price-updates.json
  %(prog)s partial-update --operation update_price --document-id "product://001" --price 29.99
  
  # Monitoring
  %(prog)s monitor --ordering-id 1716387965000
  %(prog)s status --last-hour
  
  # Validation and setup
  %(prog)s validate --file data/complete-payload.json
  %(prog)s config test
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Full update command
    full_parser = subparsers.add_parser("full-update", help="Perform full catalog update")
    full_parser.add_argument("--file", "-f", required=True, help="JSON file with catalog data")
    full_parser.add_argument("--no-delete-old", action="store_true", help="Don't delete old items")
    full_parser.add_argument("--no-verify", action="store_true", help="Skip verification")
    
    # Partial update command
    partial_parser = subparsers.add_parser("partial-update", help="Perform partial catalog update")
    partial_parser.add_argument("--file", "-f", help="JSON file with partial update data")
    partial_parser.add_argument("--operation", choices=["update_price", "update_stock", "update_rating"], 
                               help="Quick operation type")
    partial_parser.add_argument("--document-id", help="Document ID for quick operations")
    partial_parser.add_argument("--price", type=float, help="New price")
    partial_parser.add_argument("--rating", type=float, help="New rating")
    partial_parser.add_argument("--in-stock", type=bool, help="Stock status")
    partial_parser.add_argument("--no-verify", action="store_true", help="Skip verification")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor specific operation")
    monitor_parser.add_argument("--ordering-id", type=int, required=True, help="Ordering ID to monitor")
    monitor_parser.add_argument("--wait", "-w", type=int, default=2, help="Minutes to wait before checking")
    
    # Status command  
    status_parser = subparsers.add_parser("status", help="Get operations status/summary")
    status_parser.add_argument("--last-hour", action="store_true", help="Last hour summary")
    status_parser.add_argument("--last-day", action="store_true", help="Last 24 hours summary") 
    status_parser.add_argument("--date", help="Specific date summary (YYYY-MM-DD)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate data files")
    validate_parser.add_argument("--file", "-f", help="Specific file to validate")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("action", choices=["show", "validate", "test"], 
                              help="Configuration action")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available data files")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    success = False
    
    try:
        if args.command == "full-update":
            success = cmd_full_update(args)
        elif args.command == "partial-update":
            success = cmd_partial_update(args)
        elif args.command == "monitor":
            success = cmd_monitor(args)
        elif args.command == "status":
            success = cmd_status(args)
        elif args.command == "validate":
            success = cmd_validate(args)
        elif args.command == "config":
            success = cmd_config(args)
        elif args.command == "list":
            if setup_workspace():
                list_data_files()
                success = True
        else:
            parser.print_help()
            success = False
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    
    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()