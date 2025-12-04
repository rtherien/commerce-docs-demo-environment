#!/usr/bin/env python3
"""
Coveo Stream API Operation Monitor

This script monitors the status of Stream API operations and provides detailed
reporting on upload success, failures, and indexing status.

Usage:
    python monitor_operations.py --ordering-id 1716387965000
    python monitor_operations.py --request-id "498ef728-1dc2-4b01-be5f-e8f8f1154a99"
    python monitor_operations.py --last-hour
    python monitor_operations.py --date "2023-12-04" --summary
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Add the src directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from coveo_utils import CoveoAPIClient, validate_config


class OperationMonitor:
    """Monitor for Coveo Stream API operations."""
    
    def __init__(self, config_path: str = "config/coveo-config.json"):
        """Initialize the monitor with configuration."""
        self.client = CoveoAPIClient(config_path)
    
    def check_batch_status(self, ordering_id: int, start_time: datetime, 
                          end_time: datetime) -> Dict:
        """
        Check the status of a batch operation.
        
        Args:
            ordering_id: The ordering ID to check
            start_time: Start time for log search
            end_time: End time for log search
            
        Returns:
            Dictionary with batch status information
        """
        print(f"Checking batch status for ordering ID: {ordering_id}")
        
        # Get batch logs
        logs = self.client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["BATCH_FILE"],
            results=["COMPLETED", "WARNING", "ERROR"]
        )
        
        # Find logs for this ordering ID
        batch_logs = [log for log in logs 
                     if log.get("meta", {}).get("orderingid") == ordering_id]
        
        if not batch_logs:
            return {
                "found": False,
                "status": "NOT_FOUND",
                "message": f"No batch logs found for ordering ID {ordering_id}"
            }
        
        batch_log = batch_logs[0]  # Should only be one
        result = batch_log.get("result")
        
        status_info = {
            "found": True,
            "ordering_id": ordering_id,
            "result": result,
            "timestamp": batch_log.get("timestamp"),
            "task": batch_log.get("task"),
            "operation": batch_log.get("operation"),
            "meta": batch_log.get("meta", {})
        }
        
        if result == "COMPLETED":
            status_info["status"] = "SUCCESS"
            status_info["message"] = "Batch was accepted successfully"
        elif result == "WARNING":
            error = batch_log.get("meta", {}).get("error", "Unknown warning")
            status_info["status"] = "WARNING"
            status_info["message"] = f"Batch accepted with warning: {error}"
        elif result == "ERROR":
            error = batch_log.get("meta", {}).get("error", "Unknown error")
            status_info["status"] = "ERROR"
            status_info["message"] = f"Batch failed: {error}"
        else:
            status_info["status"] = "UNKNOWN"
            status_info["message"] = f"Unknown batch result: {result}"
        
        return status_info
    
    def check_item_processing(self, start_time: datetime, end_time: datetime,
                             ordering_id: Optional[int] = None) -> Dict:
        """
        Check the status of individual item processing.
        
        Args:
            start_time: Start time for log search
            end_time: End time for log search
            ordering_id: Optional ordering ID to filter results
            
        Returns:
            Dictionary with item processing information
        """
        print("Checking item processing status...")
        
        # Get item processing logs (warnings/errors only)
        warning_logs = self.client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["UPDATE"],
            results=["WARNING"]
        )
        
        error_logs = self.client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["UPDATE"],
            results=["ERROR"]
        )
        
        all_logs = warning_logs + error_logs
        
        # Filter by ordering ID if provided
        if ordering_id:
            # Note: Individual item logs may have orderingid=0 or the original orderingid
            filtered_logs = []
            for log in all_logs:
                log_ordering_id = log.get("meta", {}).get("orderingid", 0)
                if log_ordering_id == ordering_id or log_ordering_id == 0:
                    filtered_logs.append(log)
            all_logs = filtered_logs
        
        # Process the logs
        warnings = [log for log in all_logs if log.get("result") == "WARNING"]
        errors = [log for log in all_logs if log.get("result") == "ERROR"]
        
        status_info = {
            "total_issues": len(all_logs),
            "warnings": len(warnings),
            "errors": len(errors),
            "warning_details": [],
            "error_details": []
        }
        
        # Process warning details
        for log in warnings:
            status_info["warning_details"].append({
                "document_id": log.get("id", "Unknown"),
                "error": log.get("meta", {}).get("error", "Unknown warning"),
                "timestamp": log.get("timestamp"),
                "ordering_id": log.get("meta", {}).get("orderingid", 0)
            })
        
        # Process error details
        for log in errors:
            status_info["error_details"].append({
                "document_id": log.get("id", "Unknown"),
                "error": log.get("meta", {}).get("error", "Unknown error"),
                "timestamp": log.get("timestamp"),
                "ordering_id": log.get("meta", {}).get("orderingid", 0)
            })
        
        # Determine overall status
        if len(errors) > 0:
            status_info["status"] = "ERROR"
            status_info["message"] = f"Found {len(errors)} errors and {len(warnings)} warnings"
        elif len(warnings) > 0:
            status_info["status"] = "WARNING"
            status_info["message"] = f"Found {len(warnings)} warnings"
        else:
            status_info["status"] = "SUCCESS"
            status_info["message"] = "No processing issues found"
        
        return status_info
    
    def monitor_operation(self, ordering_id: int, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         wait_minutes: int = 5) -> Dict:
        """
        Monitor a complete operation (batch + item processing).
        
        Args:
            ordering_id: The ordering ID to monitor
            start_time: Start time for monitoring (defaults to 1 hour ago)
            end_time: End time for monitoring (defaults to now)
            wait_minutes: Minutes to wait for processing before checking
            
        Returns:
            Dictionary with complete operation status
        """
        if end_time is None:
            end_time = datetime.now(timezone.utc)
        
        if start_time is None:
            start_time = end_time - timedelta(hours=1)
        
        print(f"Monitoring operation {ordering_id} from {start_time} to {end_time}")
        
        # Wait for processing if requested
        if wait_minutes > 0:
            import time
            print(f"Waiting {wait_minutes} minutes for processing...")
            time.sleep(wait_minutes * 60)
            end_time = datetime.now(timezone.utc)  # Update end time
        
        # Check batch status
        batch_status = self.check_batch_status(ordering_id, start_time, end_time)
        
        # Check item processing
        item_status = self.check_item_processing(start_time, end_time, ordering_id)
        
        # Combine results
        overall_status = {
            "ordering_id": ordering_id,
            "monitoring_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "batch_status": batch_status,
            "item_processing": item_status
        }
        
        # Determine overall result
        if not batch_status["found"]:
            overall_status["result"] = "NOT_FOUND"
            overall_status["message"] = "Operation not found"
        elif batch_status["status"] == "ERROR":
            overall_status["result"] = "FAILED"
            overall_status["message"] = "Batch processing failed"
        elif item_status["status"] == "ERROR":
            overall_status["result"] = "FAILED"
            overall_status["message"] = "Item processing failed"
        elif batch_status["status"] == "WARNING" or item_status["status"] == "WARNING":
            overall_status["result"] = "WARNING"
            overall_status["message"] = "Operation completed with warnings"
        else:
            overall_status["result"] = "SUCCESS"
            overall_status["message"] = "Operation completed successfully"
        
        return overall_status
    
    def get_operation_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """
        Get a summary of all operations in a time period.
        
        Args:
            start_time: Start time for summary
            end_time: End time for summary
            
        Returns:
            Dictionary with operation summary
        """
        print(f"Getting operation summary from {start_time} to {end_time}")
        
        # Get all batch operations
        batch_logs = self.client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["BATCH_FILE"],
            results=["COMPLETED", "WARNING", "ERROR"]
        )
        
        # Get all item processing issues
        item_issues = self.client.get_operation_logs(
            start_time=start_time,
            end_time=end_time,
            tasks=["STREAMING_EXTENSION"],
            operations=["UPDATE"],
            results=["WARNING", "ERROR"]
        )
        
        # Process batch operations
        batch_summary = {
            "total_batches": len(batch_logs),
            "successful": len([log for log in batch_logs if log.get("result") == "COMPLETED"]),
            "warnings": len([log for log in batch_logs if log.get("result") == "WARNING"]),
            "errors": len([log for log in batch_logs if log.get("result") == "ERROR"]),
            "operations": []
        }
        
        for log in batch_logs:
            batch_summary["operations"].append({
                "ordering_id": log.get("meta", {}).get("orderingid"),
                "result": log.get("result"),
                "timestamp": log.get("timestamp"),
                "error": log.get("meta", {}).get("error") if log.get("result") != "COMPLETED" else None
            })
        
        # Process item issues
        item_summary = {
            "total_items_with_issues": len(item_issues),
            "warnings": len([log for log in item_issues if log.get("result") == "WARNING"]),
            "errors": len([log for log in item_issues if log.get("result") == "ERROR"]),
            "sample_issues": item_issues[:10]  # Show first 10 issues
        }
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "batch_operations": batch_summary,
            "item_processing": item_summary
        }


def print_batch_status(batch_status: Dict) -> None:
    """Print batch status in a readable format."""
    print("\n📦 Batch Status:")
    if not batch_status["found"]:
        print("  ❌ Batch not found")
        return
    
    status = batch_status["status"]
    if status == "SUCCESS":
        print(f"  ✅ {batch_status['message']}")
    elif status == "WARNING":
        print(f"  ⚠️  {batch_status['message']}")
    elif status == "ERROR":
        print(f"  ❌ {batch_status['message']}")
    else:
        print(f"  ❓ {batch_status['message']}")
    
    print(f"  📊 Ordering ID: {batch_status.get('ordering_id')}")
    print(f"  ⏰ Timestamp: {batch_status.get('timestamp', 'Unknown')}")


def print_item_status(item_status: Dict) -> None:
    """Print item processing status in a readable format."""
    print("\n🔄 Item Processing Status:")
    
    status = item_status["status"]
    total_issues = item_status["total_issues"]
    
    if status == "SUCCESS":
        print("  ✅ All items processed successfully")
    elif status == "WARNING":
        print(f"  ⚠️  {item_status['message']}")
    elif status == "ERROR":
        print(f"  ❌ {item_status['message']}")
    
    if total_issues > 0:
        print(f"  📊 Total issues: {total_issues}")
        print(f"  ⚠️  Warnings: {item_status['warnings']}")
        print(f"  ❌ Errors: {item_status['errors']}")
        
        # Show some warning details
        if item_status["warning_details"]:
            print("\n  Warning Details:")
            for i, warning in enumerate(item_status["warning_details"][:5]):
                print(f"    {i+1}. {warning['document_id']}: {warning['error']}")
            
            if len(item_status["warning_details"]) > 5:
                print(f"    ... and {len(item_status['warning_details']) - 5} more warnings")
        
        # Show some error details
        if item_status["error_details"]:
            print("\n  Error Details:")
            for i, error in enumerate(item_status["error_details"][:5]):
                print(f"    {i+1}. {error['document_id']}: {error['error']}")
            
            if len(item_status["error_details"]) > 5:
                print(f"    ... and {len(item_status['error_details']) - 5} more errors")


def print_operation_summary(summary: Dict) -> None:
    """Print operation summary in a readable format."""
    print(f"\n📈 Operations Summary ({summary['period']['start']} to {summary['period']['end']}):")
    
    batch_ops = summary["batch_operations"]
    print(f"\n📦 Batch Operations:")
    print(f"  Total: {batch_ops['total_batches']}")
    print(f"  ✅ Successful: {batch_ops['successful']}")
    print(f"  ⚠️  Warnings: {batch_ops['warnings']}")
    print(f"  ❌ Errors: {batch_ops['errors']}")
    
    item_proc = summary["item_processing"]
    print(f"\n🔄 Item Processing:")
    print(f"  Items with issues: {item_proc['total_items_with_issues']}")
    print(f"  ⚠️  Warnings: {item_proc['warnings']}")
    print(f"  ❌ Errors: {item_proc['errors']}")
    
    if batch_ops["operations"]:
        print(f"\n📋 Recent Operations:")
        for op in batch_ops["operations"][-5:]:  # Show last 5
            result_emoji = "✅" if op["result"] == "COMPLETED" else ("⚠️" if op["result"] == "WARNING" else "❌")
            print(f"  {result_emoji} {op['ordering_id']} - {op['timestamp']}")
            if op["error"]:
                print(f"     Error: {op['error']}")


def main():
    """Main function to handle command line execution."""
    parser = argparse.ArgumentParser(
        description="Monitor Coveo Stream API operation status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ordering-id 1716387965000
  %(prog)s --ordering-id 1716387965000 --wait 3
  %(prog)s --request-id "498ef728-1dc2-4b01-be5f-e8f8f1154a99"
  %(prog)s --last-hour --summary
  %(prog)s --date "2023-12-04" --summary
  %(prog)s --start "2023-12-04T10:00:00Z" --end "2023-12-04T11:00:00Z"
        """
    )
    
    # Operation identification
    parser.add_argument(
        "--ordering-id",
        type=int,
        help="Ordering ID to monitor"
    )
    
    parser.add_argument(
        "--request-id",
        help="Request ID to monitor (not implemented yet)"
    )
    
    # Time range options
    parser.add_argument(
        "--start",
        help="Start time (ISO format: 2023-12-04T10:00:00Z)"
    )
    
    parser.add_argument(
        "--end", 
        help="End time (ISO format: 2023-12-04T11:00:00Z)"
    )
    
    parser.add_argument(
        "--last-hour",
        action="store_true",
        help="Monitor operations from the last hour"
    )
    
    parser.add_argument(
        "--date",
        help="Monitor operations for a specific date (YYYY-MM-DD)"
    )
    
    # Options
    parser.add_argument(
        "--wait", "-w",
        type=int,
        default=0,
        help="Minutes to wait for processing before checking (default: 0)"
    )
    
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show summary instead of detailed monitoring"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/coveo-config.json",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    if not validate_config(args.config):
        print("Configuration validation failed. Please check your config file.")
        sys.exit(1)
    
    # Parse time arguments
    end_time = datetime.now(timezone.utc)
    start_time = None
    
    if args.end:
        try:
            end_time = datetime.fromisoformat(args.end.replace('Z', '+00:00'))
        except ValueError:
            print(f"Invalid end time format: {args.end}")
            sys.exit(1)
    
    if args.start:
        try:
            start_time = datetime.fromisoformat(args.start.replace('Z', '+00:00'))
        except ValueError:
            print(f"Invalid start time format: {args.start}")
            sys.exit(1)
    elif args.last_hour:
        start_time = end_time - timedelta(hours=1)
    elif args.date:
        try:
            date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
            start_time = datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    elif args.ordering_id:
        # Default to last hour if monitoring specific operation
        start_time = end_time - timedelta(hours=1)
    
    if not start_time:
        parser.error("Must specify a time range or operation to monitor")
    
    # Initialize monitor
    monitor = OperationMonitor(args.config)
    
    try:
        if args.summary:
            # Get summary
            summary = monitor.get_operation_summary(start_time, end_time)
            
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print_operation_summary(summary)
        
        elif args.ordering_id:
            # Monitor specific operation
            result = monitor.monitor_operation(
                ordering_id=args.ordering_id,
                start_time=start_time,
                end_time=end_time,
                wait_minutes=args.wait
            )
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"🔍 Monitoring Operation {args.ordering_id}")
                print_batch_status(result["batch_status"])
                print_item_status(result["item_processing"])
                
                print(f"\n🎯 Overall Result: {result['result']}")
                print(f"📝 Message: {result['message']}")
        
        else:
            # Get item processing status for time range
            item_status = monitor.check_item_processing(start_time, end_time)
            
            if args.json:
                print(json.dumps(item_status, indent=2))
            else:
                print_item_status(item_status)
    
    except Exception as e:
        print(f"Error during monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()