# Coveo Commerce Catalog Management Tool

A comprehensive Python toolkit for managing Coveo commerce catalog data using the Stream API. This tool supports large file uploads with automatic chunking, partial updates, and operation monitoring - specifically designed to work with your existing data files like `data/complete-payload.json`.

## Features

### ✅ Full Catalog Updates
- Upload complete catalog data with automatic chunking for large files (>256MB)
- Support for your existing data format (`AddOrUpdate` arrays)
- Automatic deletion of old items
- Upload verification and monitoring

### ✅ Partial Catalog Updates
- Price updates, inventory changes, field replacements
- Array operations (add/remove items from arrays)
- Dictionary field updates
- Command-line quick operations

### ✅ Operation Monitoring
- Track upload status and indexing progress
- Detailed error reporting and warnings
- Batch and individual item processing status
- Historical operation summaries

### ✅ Large File Support
- Automatic chunking for files exceeding 256MB
- Your 5.6MB `complete-payload.json` will be handled efficiently
- Progress tracking during chunked uploads

## Quick Start

### 1. Setup Configuration

Copy and update the configuration file:

```bash
cp config/coveo-config.json config/coveo-config.json
```

Update `config/coveo-config.json` with your Coveo credentials:

```json
{
  "coveo": {
    "organization_id": "your-org-id-here",
    "api_key": "your-api-key-here",
    "source_id": "your-source-id-here"
  }
}
```

### 2. Install Dependencies

```bash
pip install requests
```

### 3. Test Configuration

```bash
python coveo_catalog_tool.py config test
```

## Usage Examples

### Full Catalog Update

Upload your complete catalog data:

```bash
# Upload your existing complete payload
python coveo_catalog_tool.py full-update --file data/complete-payload.json

# Upload without deleting old items
python coveo_catalog_tool.py full-update --file data/complete-payload.json --no-delete-old

# Upload without verification (faster)
python coveo_catalog_tool.py full-update --file data/complete-payload.json --no-verify
```

### Partial Updates

#### From File
```bash
# Use the sample partial updates
python coveo_catalog_tool.py partial-update --file data/sample-partial-updates.json
```

#### Quick Command Line Operations
```bash
# Update product price
python coveo_catalog_tool.py partial-update --operation update_price --document-id "https://sports.barca.group/pdp/SP00003_00001" --price 29.99

# Update stock status
python coveo_catalog_tool.py partial-update --operation update_stock --document-id "https://sports.barca.group/pdp/SP00003_00001" --in-stock false

# Update product rating
python coveo_catalog_tool.py partial-update --operation update_rating --document-id "https://sports.barca.group/pdp/SP00003_00001" --rating 4.5
```

### Monitoring and Status

```bash
# Monitor a specific operation (you get the ordering ID from upload response)
python coveo_catalog_tool.py monitor --ordering-id 1716387965000

# Get status for last hour
python coveo_catalog_tool.py status --last-hour

# Get status for specific date
python coveo_catalog_tool.py status --date "2023-12-04"
```

### File Management

```bash
# List available data files
python coveo_catalog_tool.py list

# Validate your data files
python coveo_catalog_tool.py validate --file data/complete-payload.json

# Validate all data files
python coveo_catalog_tool.py validate
```

## Understanding Your Data Structure

Your `complete-payload.json` file uses this format:

```json
{
  "AddOrUpdate": [
    {
      "DocumentId": "https://sports.barca.group/pdp/SP00003_00001",
      "FileExtension": "html", 
      "ObjectType": "Product",
      "ec_name": "Aqua Trampoline",
      "ec_price": 3000,
      "ec_brand": "HO Sports"
    }
  ]
}
```

The tool automatically converts this to Coveo API format (`addOrUpdate` with `documentId` and `objecttype`).

## Large File Handling

Your `complete-payload.json` is 5.6MB, which is well under the 256MB chunk limit, so it will upload as a single file. However, if you have larger files, the tool automatically:

1. **Analyzes file size** and determines if chunking is needed
2. **Splits large files** into multiple chunks based on item count
3. **Uploads chunks sequentially** with progress tracking
4. **Aggregates results** from all chunks

## API Rate Limits

The tool respects Coveo API limits:

- **15,000 API calls per day** (production)
- **250 calls per 5 minutes** (burst limit)  
- **96 upload operations per day**
- **256MB max file size** (handled via chunking)

Rate limiting is handled automatically with exponential backoff.

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd commerce-docs-demo-environment
   ```

2. **Open directly in browser**
   Simply open `website/pages/simple-search.html` in your web browser by:
   - Double-clicking the file, or
   - Right-click → "Open with" → your preferred browser, or
   - Drag and drop the file into your browser window

   **Optional: Use a local server**
   If you prefer using a local server (useful for development):
   ```bash
   python3 -m http.server 8000
   # Then visit http://localhost:8000/website/pages/simple-search.html
   ```

## File Structure

```
├── website/
│   ├── pages/
│   │   ├── simple-search.html      # Main search page
│   │   ├── simple-plp-shoes.html   # Shoes category page
│   │   ├── simple-plp-hockey.html  # Hockey category page
│   │   ├── simple-plp-golf.html    # Golf category page
│   │   └── product-detail-simple.html # Product detail page
│   ├── styles/
│   │   └── main.css                # Custom styling
│   └── assets/
│       └── images/                 # Product images
├── data/                           # Sample product data (JSON files)
├── docs/                           # Documentation
├── index.html                      # Landing page
└── README.md                       # This file
```

## Configuration

The demo is pre-configured with:
- **Organization ID**: `coveodocumentationtest`
- **Access Token**: `xx2a24e7d1-8dca-482e-a7c7-d49fe39aac30`
- **Environment**: `prod`
- **Analytics Tracking ID**: `commerce-docs-demo`
- **Currency**: CAD (Canadian Dollars)

## How It Works

### Search Page (`simple-search.html`)
- Uses `type="search"` interface
- Includes search box with recent queries and suggestions
- Shows all products by default
- Supports full-text search and faceted filtering

### Product Listing Pages
- Use `type="product-listing"` interface
- Pre-filtered for specific categories (shoes, hockey, golf)
- Include faceted navigation and sorting
- Show category-specific products

### Product Templates
All pages use the official Coveo product template structure:
- `atomic-product-section-name` - Product name with clickable link
- `atomic-product-section-visual` - Product images
- `atomic-product-section-metadata` - Brand and category information
- `atomic-product-section-emphasized` - Pricing
- `atomic-product-section-children` - Product variants

## Customization

To customize for your own organization:

1. Update the configuration in each HTML file:
   ```javascript
   await searchInterface.initialize({
       accessToken: 'your-access-token',
       organizationId: 'your-org-id',
       // ... other settings
   });
   ```

2. Modify the product template structure as needed
3. Update styling in `website/styles/main.css`
4. Replace product data and images

## Technology Stack

- **Coveo Atomic Commerce v3** - UI components from CDN
- **Vanilla JavaScript** - No additional frameworks
- **HTML5 & CSS3** - Standard web technologies
- **Coveo Commerce API** - Product search and analytics

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

This project is for demonstration purposes only.

