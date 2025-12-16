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
COVEO_API_KEY=your-stream-api-key-here
COVEO_FRONTEND_ACCESS_TOKEN=your-frontend-access-token-here
COVEO_ORGANIZATION_ID=coveodocumentationtest
COVEO_SOURCE_ID=coveodocumentationtest-w33goww7m52uyful5vbormci4y
```

The default setup uses the coveodocumentationtest organization and the commerce-documentation-catalog-source source. You can update the values if you want to use your own org and/or source.

**Important Security Notes:**
- ⚠️ Generate two API keys with appropriate permissions in your Coveo admin console:
  - `COVEO_API_KEY`: For backend operations (Stream API, catalog management)
  - `COVEO_FRONTEND_ACCESS_TOKEN`: For frontend search interfaces (HTML pages)
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

### Monitoring and Status

```bash
# Monitor a specific operation (you get the ordering ID from upload response)
python coveo_catalog_tool.py monitor --ordering-id 1716387965000

# Get status for last hour
python coveo_catalog_tool.py status --last-hour

# Get status for specific date
python coveo_catalog_tool.py status --date "2023-12-04"
```

## Website Demo

### Quick Launch

1. **For Frontend Demo (HTML Pages)**
   
   The website pages automatically use your frontend access token from the `.env` file:
   
   **Automatic Token Updates (Required - One Time)**
   ```bash
   # Update all HTML files with your frontend token
   python3 update_html_tokens.py
   ```
   
   **Manual Setup (Alternative)**
   - Open each HTML file in `website/pages/`
   - Replace the `accessToken` value with your `COVEO_FRONTEND_ACCESS_TOKEN`

2. **View in Browser**
   - Simply open any HTML file directly in your browser (e.g., double-click `website/pages/simple-search.html`)
   - No local server needed - the HTML files work standalone once tokens are embedded
   - Optional: Use local server if you prefer: `python3 -m http.server 8000` then visit http://localhost:8000/website/pages/

## 🚀 Quick Start with VS Code Task

You can start the demo server easily using a pre-configured VS Code task:

1. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Type `Tasks: Run Task` and select it
3. Choose **Start Demo Server**

This will launch the local server in the background and print the demo URLs in the terminal. You can now open the demo pages in your browser:
- Main Search: http://localhost:8080/
- Nike Products: http://localhost:8080/pages/simple-plp-nike.html
- Adidas Products: http://localhost:8080/pages/simple-plp-adidas.html
- Product Detail: http://localhost:8080/pages/product.html?id=PRODUCT_ID

Press Ctrl+C in the terminal to stop the server.
