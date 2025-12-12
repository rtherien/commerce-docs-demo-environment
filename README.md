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

### ✅ Secure Configuration
- Environment variable support for API keys
- No hardcoded credentials in code
- `.env` file support with automatic loading

## Quick Start

### 1. Setup Environment

**Create a virtual environment (recommended):**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install requests python-dotenv
```

### 2. Configure API Access

**Create a `.env` file** in the project root:
```bash
# Coveo API Configuration
COVEO_API_KEY=your-new-api-key-here
COVEO_ORGANIZATION_ID=coveodocumentationtest
COVEO_SOURCE_ID=coveodocumentationtest-w33goww7m52uyful5vbormci4y
```

The default setup uses the coveodocumentationtest organization and the commerce-documentation-catalog-source source. You can update the values if you want to use your own org and/or source.

**Important Security Notes:**
- ⚠️ Generate a new API key with appropriate permissions in your Coveo admin console
- ⚠️ Never commit API keys to version control

### 3. Test Configuration

```bash
python3 coveo_catalog_tool.py status --last-hour
```

### 4. VS Code Tasks (Optional)

For easier workflow, VS Code tasks are available to run common operations with interactive prompts:

**To use VS Code tasks:**
1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select from available Coveo tasks:
   - **Coveo: Full Catalog Update** - Upload complete catalog (prompts for file path)
   - **Coveo: Full Catalog Update (No Delete)** - Upload without deleting old items
   - **Coveo: Full Catalog Update (Fast - No Verify)** - Quick upload without verification
   - **Coveo: Partial Update from File** - Run partial updates (prompts for file path)
   - **Coveo: Validate File** - Validate any data file (prompts for file path)
   - **Coveo: Check Status (Last Hour)** - View recent operations
   - **Coveo: List Available Data Files** - See all data files
   - **Coveo: Setup Virtual Environment** - Initial project setup
   - **Coveo: Update Example - Price Change** - Demo price update (prompts for product ID and price)
   - **Coveo: Update Example - Stock Status** - Demo stock update (prompts for product ID and stock status)

**Interactive Features:**
- 📁 **File path prompts** - Specify which data file to use (defaults to `data/complete-payload.json`)
- 🎯 **Product ID prompts** - Enter specific product URLs for individual updates
- 💰 **Price input** - Enter new prices for product updates
- 📦 **Stock status picker** - Choose In Stock/Out of Stock from a dropdown

All tasks automatically activate the virtual environment and deactivate it when complete.

## Usage Examples

### Full Catalog Update

Upload your complete catalog data:

```bash
# Upload your existing complete payload
python3 coveo_catalog_tool.py full-update --file data/complete-payload.json

# Upload without deleting old items
python3 coveo_catalog_tool.py full-update --file data/complete-payload.json --no-delete-old

# Upload without verification (faster)
python3 coveo_catalog_tool.py full-update --file data/complete-payload.json --no-verify
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

## Website Demo

### Quick Launch

1. **For Frontend Demo (HTML Pages)**
   
   The website pages now use placeholder API keys for security. To use them:
   
   **Option 1: Manual Setup (Development)**
   - Open each HTML file in `website/pages/`
   - Replace `accessToken: ""` with your actual API key
   
   **Option 2: Local Server (Recommended)**
   ```bash
   # Create a simple config file for the web pages
   echo 'const COVEO_CONFIG = { accessToken: "your-api-key-here" };' > website/js/config.js
   # Then update HTML files to use this config
   ```
   
   **Option 3: Server-side Rendering (Production)**
   - Use a web server framework (Express.js, Flask, etc.) that can inject environment variables into HTML templates
   - This is recommended for production deployments where you need secure environment variable handling

2. **View in Browser**
   - Open `website/pages/simple-search.html` directly in browser, or
   - Use local server: `python3 -m http.server 8000` then visit http://localhost:8000/website/pages/

### Website Structure

```
├── website/
│   ├── pages/
│   │   ├── simple-search.html           # Main search page  
│   │   ├── simple-plp-adidas.html       # Adidas brand page
│   │   ├── simple-plp-steve-madden.html # Steve Madden brand page
│   │   ├── simple-plp-ecco.html         # Ecco brand page  
│   │   ├── simple-plp-dooney-bourke.html# Dooney & Bourke brand page
│   │   ├── simple-plp-nike.html         # Nike brand page
│   │   └── product-detail-simple.html   # Product detail page
│   ├── styles/
│   │   └── main.css                     # Custom styling
│   └── js/
│       └── cart.js                      # Cart functionality
├── data/                                # Product catalog data
└── config/                              # API configuration
```

## Configuration

The demo now uses environment variables for security:
- **API credentials** are stored in `.env` file (not in Git)
- **Organization ID**: Loaded from `COVEO_ORGANIZATION_ID`
- **Source ID**: Loaded from `COVEO_SOURCE_ID`  
- **Environment**: `prod`
- **Analytics Tracking ID**: `commerce-docs-demo`
- **Currency**: CAD (Canadian Dollars)

## Security Features

- ✅ **API keys in environment variables** (not hardcoded)
- ✅ **`.env` file in `.gitignore`** (credentials not committed)
- ✅ **Automatic environment loading** in Python tools
- ⚠️ **HTML pages require manual API key setup** (browsers can't access env vars)

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

1. **Update your `.env` file** with your credentials:
   ```bash
   COVEO_API_KEY=your-new-api-key
   COVEO_ORGANIZATION_ID=your-org-id  
   COVEO_SOURCE_ID=your-source-id
   ```

2. **For HTML pages**, update the configuration:
   ```javascript
   await searchInterface.initialize({
       accessToken: 'your-access-token',
       organizationId: 'your-org-id',
       // ... other settings
   });
   ```

3. Modify the product template structure as needed
4. Update styling in `website/styles/main.css`
5. Replace product data and images

## Important Files

- **`.env`** - Your API credentials (create this file)
- **`config/coveo-config.json`** - Configuration template with env var placeholders
- **`coveo_catalog_tool.py`** - Main Python tool for catalog management
- **`src/coveo_utils.py`** - Core utilities with environment variable support

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

