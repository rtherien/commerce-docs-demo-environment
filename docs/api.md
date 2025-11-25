# API Reference

## CoveoLoader Class

The main class for interacting with the Coveo Commerce API.

### Constructor

```python
CoveoLoader(config_path: str = "config.json")
```

**Parameters:**
- `config_path` (str): Path to the configuration file. Defaults to "config.json" in the project root.

**Raises:**
- `ValueError`: If required configuration keys are missing.
- `FileNotFoundError`: If the configuration file doesn't exist.

### Methods

#### perform_update_operation(payload, delete_old=False)

Performs an update operation on the Coveo source.

**Parameters:**
- `payload` (dict): The JSON payload containing items to add/update/delete
- `delete_old` (bool): Whether to delete items older than the update

**Returns:**
- `bool`: True if successful, False otherwise

#### perform_load_operation(payload)

Performs a load operation (replaces all data) on the Coveo source.

**Parameters:**
- `payload` (dict): The JSON payload containing items

**Returns:**
- `bool`: True if successful, False otherwise

#### list_payload_files()

Lists available JSON payload files in the data directory.

**Returns:**
- `List[str]`: List of available payload filenames

#### load_payload_file(filename)

Loads and validates a payload file.

**Parameters:**
- `filename` (str): Name of the payload file to load

**Returns:**
- `dict`: The loaded and validated payload

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `ValueError`: If the JSON is invalid

## Configuration

Configuration is provided via a JSON file with the following structure:

```json
{
  "organization_id": "your-organization-id",
  "source_id": "your-source-id", 
  "access_token": "your-api-key"
}
```

## Payload Format

Payloads should follow the Coveo Stream API format:

```json
{
  "addOrUpdate": [
    {
      "documentId": "product://unique-id",
      "objecttype": "Product|Variant|Availability",
      // ... other fields
    }
  ],
  "delete": [
    {
      "documentId": "product://item-to-delete"
    }
  ]
}
```

## Error Handling

The loader handles various API errors:

- **401 Unauthorized**: Invalid access token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Invalid organization/source ID
- **413 Payload Too Large**: File exceeds 256MB limit
- **429 Too Many Requests**: Rate limit exceeded

## Examples

### Basic Usage

```python
from src.loader import CoveoLoader

# Initialize loader
loader = CoveoLoader("config.json")

# Load payload
payload = loader.load_payload_file("sample-data.json")

# Perform update
success = loader.perform_update_operation(payload)
```

### Command Line Usage

```bash
# Interactive mode
./coveo-loader

# Direct file execution
./coveo-loader --file sample-data.json --operation update

# List available files
./coveo-loader --list
```