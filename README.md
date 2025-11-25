# Coveo Commerce API Loader

A Python script to easily perform load and update operations against the Coveo Commerce API using your test payload files.

## Features

- 🚀 **Two Operation Types**: Support for both Update and Load operations
- 📁 **Easy File Selection**: Interactive mode to choose from your Test payloads folder
- 🔧 **Command Line Interface**: Batch operations for automation
- 📊 **Payload Analysis**: Automatic analysis and display of payload contents
- ⚡ **Error Handling**: Comprehensive error messages and retry guidance
- 🛡️ **Safety Features**: Confirmations for destructive operations

## What's the Difference?

### Update Operations (Recommended)
- **Safer**: Only updates/adds items included in your payload
- **Preserves Data**: Existing items not in payload remain unchanged
- **Efficient**: Better performance and faster processing
- **Flexible**: Optional cleanup of old items

### Load Operations
- **Replaces Everything**: Completely overwrites all data in your source
- **Resource Intensive**: Requires processing all data at once
- **Delayed Processing**: 15-minute delay for old item removal

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Coveo Organization** with Commerce features enabled
3. **Catalog Source** created in your Coveo organization
4. **API Key** with push privileges to your source

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create configuration** from template:
   ```bash
   cp config.template.json config.json
   ```
4. **Edit config.json** with your Coveo settings

## Configuration

Edit `config.json` with your Coveo details:

```json
{
  "organization_id": "your-org-id-here",
  "source_id": "your-source-id-here", 
  "access_token": "your-api-key-here"
}
```

### Finding Your Configuration Values

#### Organization ID
1. Go to [Coveo Administration Console](https://platform.cloud.coveo.com/)
2. Click your organization name → **Settings** → **Organization**
3. Copy the **Organization ID**

#### Source ID  
1. In Admin Console → **Content** → **Sources**
2. Click on your Catalog source
3. Copy the **Source ID** from the URL or source details

#### Access Token
1. In Admin Console → **Administration** → **API Keys**
2. Create a new API key or use existing one
3. Ensure it has **Push** privileges for your source
4. Copy the generated token

## Usage

### Interactive Mode (Recommended)

Simply run the script without arguments for guided operation:

```bash
python coveo-loader.py
```

The script will:
1. 📁 **List available payload files** from your Test payloads folder
2. 🎯 **Let you select** which file to use
3. 🔧 **Choose operation type** (Update or Load)
4. 📊 **Show payload summary** before execution
5. ✅ **Execute and report** results

### Command Line Mode

For automation or scripting:

```bash
# Update operation (recommended)
python coveo-loader.py --file full-product-payload-sample.json --operation update

# Load operation (replaces all data)
python coveo-loader.py --file full-product-payload-sample.json --operation load

# Update with old item cleanup
python coveo-loader.py --file new-availability.json --operation update --delete-old

# List available files
python coveo-loader.py --list

# Use custom config file
python coveo-loader.py --config my-config.json --file test-data.json
```

## Examples

### Adding New Products
```bash
# Use update operation to add new products without affecting existing ones
python coveo-loader.py --file patch-payload-new-product.json --operation update
```

### Updating Availability Data
```bash
# Update store availability information
python coveo-loader.py --file new-availability.json --operation update
```

### Complete Data Replacement
```bash
# ⚠️ Warning: This replaces ALL data in your source
python coveo-loader.py --file full-product-payload-sample.json --operation load
```

## Payload File Requirements

Your JSON payload files should follow this structure:

```json
{
  "addOrUpdate": [
    {
      "documentId": "product://unique-id",
      "objecttype": "Product",
      "ec_name": "Product Name",
      "ec_product_id": "SKU123",
      // ... other product fields
    }
    // ... more items
  ],
  "delete": [
    {
      "documentId": "product://item-to-delete"
    }
    // ... items to delete (optional)
  ]
}
```

### Supported Object Types
- **Product**: Main product information
- **Variant**: Product variations (size, color, etc.)
- **Availability**: Store/location inventory data

## Monitoring Results

After running operations:

1. **Check Script Output**: Look for ✅ success messages and any error details
2. **Monitor Indexing**: 
   - Go to [Coveo Administration Console](https://platform.cloud.coveo.com/)
   - **Content** → **Activity** → **Indexing Status**
   - Look for your source and recent operations
3. **Review Logs**: **Content** → **Logs** → **Log Browser** for detailed indexing logs
4. **Test Search**: Verify your data appears in search results

## Troubleshooting

### Common Issues

#### "Authentication failed" (401)
- ❌ **Problem**: Invalid or expired access token
- ✅ **Solution**: Generate new API key in Coveo Admin Console

#### "Access forbidden" (403) 
- ❌ **Problem**: API key lacks push privileges
- ✅ **Solution**: Update API key permissions to include Push access

#### "Resource not found" (404)
- ❌ **Problem**: Incorrect organization ID or source ID  
- ✅ **Solution**: Verify IDs in Coveo Admin Console

#### "Payload too large" (413)
- ❌ **Problem**: File exceeds 256 MB limit
- ✅ **Solution**: Split payload into smaller files

#### "Rate limit exceeded" (429)
- ❌ **Problem**: Too many requests
- ✅ **Solution**: Wait and retry (script shows retry time)

### API Limits

| Limit | Production | Non-Production |
|-------|------------|----------------|
| Stream API calls/day | 15,000 | 10,000 |
| Burst limit (5 min) | 250 | 150 |
| Max file size | 256 MB | 256 MB |
| Max item size | 3 MB | 3 MB |

### Getting Help

1. **Check the [Coveo Documentation](https://docs.coveo.com/en/p4eb0129/)**
2. **Review API logs** in the Coveo Admin Console
3. **Verify your payload** structure matches examples
4. **Test with smaller datasets** first

## Advanced Usage

### Custom Configuration Paths
```bash
python coveo-loader.py --config /path/to/custom-config.json
```

### Automation Scripts
```bash
#!/bin/bash
# Daily catalog update
python coveo-loader.py --file daily-updates.json --operation update --delete-old
```

### Multiple Sources
Create separate config files for different sources:
```bash
python coveo-loader.py --config prod-config.json --file prod-data.json
python coveo-loader.py --config staging-config.json --file test-data.json
```

## File Structure

```
commerce-docs-demo-environment/
├── coveo-loader.py           # Main script
├── config.json              # Your configuration (create from template)
├── config.template.json     # Configuration template
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── commerce-docs-demo-environment/
    └── Test payloads/        # Your payload files
        ├── full-product-payload-sample.json
        ├── new-availability.json
        ├── patch-payload-new-product.json
        └── ...
```

## Security Notes

- **Keep your `config.json` secure** - it contains your API credentials
- **Never commit API keys** to version control
- **Use separate API keys** for different environments (dev/staging/prod)
- **Regularly rotate** your API keys

## License

This script is provided as-is for educational and demonstration purposes. Please review Coveo's API terms and usage policies.

---

💡 **Pro Tip**: Always test with small payloads first, especially when learning the API. Use the Update operation for most use cases as it's safer and more efficient than Load operations.

# Original Demo Environment
Coveo Commerce Documentation Demo Environment
