#!/usr/bin/env python3
"""
Coveo Stream API Utilities

This module provides utility functions for interacting with the Coveo Stream API,
including support for large file uploads, file chunking, and error handling.
"""

import json
import os
import sys
import time
import gzip
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import math
from dotenv import load_dotenv


class CoveoAPIClient:
    """Client for interacting with the Coveo Stream API."""
    
    def __init__(self, config_path: str = "config/coveo-config.json"):
        """Initialize the client with configuration."""
        self.config = self._load_config(config_path)
        self.base_url = self.config["coveo"]["api_base_url"]
        self.org_id = self.config["coveo"]["organization_id"]
        self.api_key = self.config["coveo"]["api_key"]
        self.source_id = self.config["coveo"]["source_id"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file with environment variable substitution."""
        # Load environment variables from .env file
        load_dotenv()
        
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
                
            # Replace environment variable placeholders
            import re
            def replace_env_vars(match):
                var_name = match.group(1)
                env_value = os.getenv(var_name)
                if env_value is None:
                    raise ValueError(f"Environment variable {var_name} is not set")
                return env_value
            
            # Replace ${VAR_NAME} with actual environment variable values
            config_content = re.sub(r'\$\{([^}]+)\}', replace_env_vars, config_content)
            
            return json.loads(config_content)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except ValueError as e:
            if "Environment variable" in str(e):
                print(f"❌ {e}")
                print("Make sure you have a .env file with all required environment variables.")
                print("Required variables: COVEO_API_KEY, COVEO_ORGANIZATION_ID, COVEO_SOURCE_ID")
            raise e
    
    def _retry_request(self, func, *args, **kwargs) -> requests.Response:
        """Retry a request with exponential backoff."""
        max_retries = self.config["default_settings"]["retry_attempts"]
        delay = self.config["default_settings"]["retry_delay_seconds"]
        
        for attempt in range(max_retries):
            try:
                response = func(*args, **kwargs)
                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", delay))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        
        return response
    
    def create_file_container(self) -> Tuple[str, str, Dict]:
        """
        Create a file container for uploading data.
        
        Returns:
            Tuple of (upload_uri, file_id, required_headers)
        """
        url = f"{self.base_url}/push/v1/organizations/{self.org_id}/files"
        params = {"useVirtualHostedStyleUrl": self.config["coveo"]["use_virtual_hosted_style_url"]}
        
        response = self._retry_request(requests.post, url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data["uploadUri"], data["fileId"], data["requiredHeaders"]
    
    def upload_to_container(self, upload_uri: str, required_headers: Dict, 
                          data: bytes) -> None:
        """Upload data to the file container."""
        upload_headers = required_headers.copy()
        
        response = self._retry_request(requests.put, upload_uri, headers=upload_headers, data=data)
        response.raise_for_status()
    
    def update_source(self, file_id: str) -> Tuple[int, str]:
        """
        Send the file container to update the source.
        
        Returns:
            Tuple of (ordering_id, request_id)
        """
        url = f"{self.base_url}/push/v1/organizations/{self.org_id}/sources/{self.source_id}/stream/update"
        params = {"fileId": file_id}
        
        response = self._retry_request(requests.put, url, headers=self.headers, params=params, json={})
        response.raise_for_status()
        
        data = response.json()
        return data["orderingId"], data["requestId"]
    
    def partial_update_source(self, file_id: str) -> Tuple[int, str]:
        """
        Send the file container for partial update.
        
        Returns:
            Tuple of (ordering_id, request_id)
        """
        url = f"{self.base_url}/push/v1/organizations/{self.org_id}/sources/{self.source_id}/stream/update"
        params = {"fileId": file_id}
        
        response = self._retry_request(requests.put, url, headers=self.headers, params=params, json={})
        response.raise_for_status()
        
        data = response.json()
        return data["orderingId"], data["requestId"]
    
    def merge_source(self, file_id: str) -> Tuple[int, str]:
        """
        Send the file container for merge operation.
        
        Returns:
            Tuple of (ordering_id, request_id)
        """
        url = f"{self.base_url}/push/v1/organizations/{self.org_id}/sources/{self.source_id}/stream/merge"
        params = {"fileId": file_id}
        
        response = self._retry_request(requests.put, url, headers=self.headers, params=params, json={})
        response.raise_for_status()
        
        data = response.json()
        return data["orderingId"], data["requestId"]
    
    def delete_old_items(self, ordering_id: int) -> None:
        """Delete items older than the specified ordering ID."""
        url = f"{self.base_url}/push/v1/organizations/{self.org_id}/sources/{self.source_id}/stream/deleteolderthan/{ordering_id}"
        
        response = self._retry_request(requests.post, url, headers=self.headers)
        response.raise_for_status()
    
    def get_operation_logs(self, start_time: datetime, end_time: datetime, 
                          tasks: List[str], operations: List[str], 
                          results: Optional[List[str]] = None) -> List[Dict]:
        """
        Get logs for monitoring operation status.
        
        Args:
            start_time: Start time for log query
            end_time: End time for log query  
            tasks: List of tasks to filter (e.g., ["STREAMING_EXTENSION"])
            operations: List of operations to filter (e.g., ["BATCH_FILE", "UPDATE"])
            results: List of results to filter (e.g., ["COMPLETED", "WARNING"])
        """
        url = f"{self.base_url}/logs/v1/organizations/{self.org_id}"
        params = {
            "from": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        payload = {
            "tasks": tasks,
            "operations": operations,
            "sourcesIds": [self.source_id]
        }
        
        if results:
            payload["results"] = results
            
        response = self._retry_request(requests.post, url, headers=self.headers, 
                                     params=params, json=payload)
        response.raise_for_status()
        
        return response.json()


class FileChunker:
    """Handles file chunking for large uploads."""
    
    def __init__(self, max_chunk_size_mb: int = 256):
        """Initialize the chunker with max chunk size."""
        self.max_chunk_size = max_chunk_size_mb * 1024 * 1024  # Convert to bytes
    
    def needs_chunking(self, data: bytes) -> bool:
        """Check if data needs to be chunked."""
        return len(data) > self.max_chunk_size
    
    def chunk_json_data(self, json_data: Dict) -> List[Dict]:
        """
        Chunk JSON data by splitting the items array.
        
        Args:
            json_data: Dictionary containing the JSON data
            
        Returns:
            List of chunked dictionaries
        """
        if "addOrUpdate" in json_data:
            items_key = "addOrUpdate"
        elif "AddOrUpdate" in json_data:
            items_key = "AddOrUpdate"
        elif "partialUpdate" in json_data:
            items_key = "partialUpdate"
        elif "addOrMerge" in json_data:
            items_key = "addOrMerge"
        else:
            # If no recognized key, return as single chunk
            return [json_data]
        
        items = json_data[items_key]
        if not items:
            return [json_data]
        
        # Estimate items per chunk based on average item size
        total_size = len(json.dumps(json_data, separators=(',', ':')).encode('utf-8'))
        items_count = len(items)
        avg_item_size = total_size / items_count
        items_per_chunk = max(1, int(self.max_chunk_size / avg_item_size * 0.9))  # 90% safety margin
        
        chunks = []
        for i in range(0, items_count, items_per_chunk):
            chunk_items = items[i:i + items_per_chunk]
            chunk = {items_key: chunk_items}
            
            # Copy other top-level keys if they exist
            for key, value in json_data.items():
                if key != items_key:
                    chunk[key] = value
            
            chunks.append(chunk)
        
        return chunks
    
    def estimate_json_size(self, data: Dict) -> int:
        """Estimate the size of JSON data when serialized."""
        return len(json.dumps(data, separators=(',', ':')).encode('utf-8'))


class CoveoUploader:
    """High-level uploader that handles the complete upload process."""
    
    def __init__(self, config_path: str = "config/coveo-config.json"):
        """Initialize the uploader."""
        self.client = CoveoAPIClient(config_path)
        self.chunker = FileChunker(self.client.config["limits"]["max_file_size_mb"])
        self.config = self.client.config
    
    def upload_json_file(self, file_path: str, operation_type: str = "update") -> Dict:
        """
        Upload a JSON file with automatic chunking if needed.
        
        Args:
            file_path: Path to the JSON file
            operation_type: Type of operation ("update", "partial", "merge")
            
        Returns:
            Dictionary with operation results
        """
        print(f"Loading data from: {file_path}")
        
        # Load and validate JSON data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in data file: {e}")
        
        # Prepare data for serialization
        json_bytes = json.dumps(json_data, separators=(',', ':')).encode('utf-8')
        
        # Check if chunking is needed
        if self.chunker.needs_chunking(json_bytes):
            print(f"File size ({len(json_bytes) / 1024 / 1024:.1f} MB) exceeds limit. Chunking...")
            return self._upload_chunked_data(json_data, operation_type)
        else:
            print(f"Uploading single file ({len(json_bytes) / 1024 / 1024:.1f} MB)...")
            return self._upload_single_chunk(json_bytes, operation_type)
    
    def upload_json_data(self, json_data: Dict, operation_type: str = "update") -> Dict:
        """
        Upload JSON data directly with automatic chunking if needed.
        
        Args:
            json_data: Dictionary containing the JSON data
            operation_type: Type of operation ("update", "partial", "merge")
            
        Returns:
            Dictionary with operation results
        """
        # Prepare data for serialization
        json_bytes = json.dumps(json_data, separators=(',', ':')).encode('utf-8')
        
        # Check if chunking is needed
        if self.chunker.needs_chunking(json_bytes):
            print(f"Data size ({len(json_bytes) / 1024 / 1024:.1f} MB) exceeds limit. Chunking...")
            return self._upload_chunked_data(json_data, operation_type)
        else:
            print(f"Uploading single chunk ({len(json_bytes) / 1024 / 1024:.1f} MB)...")
            return self._upload_single_chunk(json_bytes, operation_type)
    
    def _upload_single_chunk(self, data: bytes, operation_type: str) -> Dict:
        """Upload a single chunk of data."""
        start_time = datetime.now(timezone.utc)
        
        # Create file container
        upload_uri, file_id, required_headers = self.client.create_file_container()
        
        # Upload data to container
        self.client.upload_to_container(upload_uri, required_headers, data)
        
        # Send to source based on operation type
        if operation_type == "update":
            ordering_id, request_id = self.client.update_source(file_id)
        elif operation_type == "partial":
            ordering_id, request_id = self.client.partial_update_source(file_id)
        elif operation_type == "merge":
            ordering_id, request_id = self.client.merge_source(file_id)
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")
        
        return {
            "success": True,
            "operation_type": operation_type,
            "chunks": 1,
            "ordering_ids": [ordering_id],
            "request_ids": [request_id],
            "start_time": start_time,
            "file_ids": [file_id]
        }
    
    def _upload_chunked_data(self, json_data: Dict, operation_type: str) -> Dict:
        """Upload data in chunks."""
        start_time = datetime.now(timezone.utc)
        
        # Split data into chunks
        chunks = self.chunker.chunk_json_data(json_data)
        print(f"Split into {len(chunks)} chunks")
        
        ordering_ids = []
        request_ids = []
        file_ids = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"Uploading chunk {i}/{len(chunks)}...")
            
            # Serialize chunk
            chunk_bytes = json.dumps(chunk, separators=(',', ':')).encode('utf-8')
            
            # Create file container
            upload_uri, file_id, required_headers = self.client.create_file_container()
            
            # Upload chunk to container
            self.client.upload_to_container(upload_uri, required_headers, chunk_bytes)
            
            # Send to source
            if operation_type == "update":
                ordering_id, request_id = self.client.update_source(file_id)
            elif operation_type == "partial":
                ordering_id, request_id = self.client.partial_update_source(file_id)
            elif operation_type == "merge":
                ordering_id, request_id = self.client.merge_source(file_id)
            
            ordering_ids.append(ordering_id)
            request_ids.append(request_id)
            file_ids.append(file_id)
            
            print(f"Chunk {i} uploaded successfully. Ordering ID: {ordering_id}")
        
        return {
            "success": True,
            "operation_type": operation_type,
            "chunks": len(chunks),
            "ordering_ids": ordering_ids,
            "request_ids": request_ids,
            "start_time": start_time,
            "file_ids": file_ids
        }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def validate_config(config_path: str) -> bool:
    """Validate the configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = [
            "coveo.organization_id",
            "coveo.api_key", 
            "coveo.source_id"
        ]
        
        for key in required_keys:
            keys = key.split('.')
            value = config
            for k in keys:
                value = value.get(k)
                if value is None:
                    print(f"Error: Missing required configuration: {key}")
                    return False
            
            if isinstance(value, str) and value.startswith("YOUR_"):
                print(f"Error: Please update configuration value: {key}")
                return False
        
        return True
    except Exception as e:
        print(f"Error validating configuration: {e}")
        return False


if __name__ == "__main__":
    # Test the utilities
    if not validate_config("config/coveo-config.json"):
        print("Configuration validation failed")
        sys.exit(1)
    
    client = CoveoAPIClient()
    print("Coveo API client initialized successfully")
    
    # Test file container creation (commented out to avoid API calls)
    # upload_uri, file_id, headers = client.create_file_container()
    # print(f"File container created: {file_id}")