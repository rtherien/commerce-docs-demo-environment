# Coveo Commerce Catalog Management Tool

A Python toolkit for managing Coveo commerce catalog data using the Stream API. Features large file uploads with automatic chunking, partial updates, and operation monitoring.

## Quick Start

### 1. Setup Virtual Environment

**Run VS Code Task:**
- Command Palette (`Cmd+Shift+P`) → "Tasks: Run Task" → **Coveo: Setup Virtual Environment**

### 2. Configure API Credentials

Create a `.env` file in the project root:
```bash
COVEO_API_KEY=your-stream-api-key-here
COVEO_FRONTEND_ACCESS_TOKEN=your-frontend-access-token-here
COVEO_ORGANIZATION_ID=coveodocumentationtest
COVEO_SOURCE_ID=coveodocumentationtest-w33goww7m52uyful5vbormci4y
```

⚠️ **Never commit API keys to version control**

### 3. You're Ready!

See the workflows below for common tasks.

## VS Code Tasks

All tasks: Command Palette (`Cmd+Shift+P`) → "Tasks: Run Task" → Select task

**How to run tasks:** Command Palette (`Cmd+Shift+P`) → "Tasks: Run Task" → Select task

### 📤 Upload Complete Catalog
**Task:** `Coveo: Full Catalog Update`
- Prompts for file path (default: `data/complete-payload.json`)
- Automatically chunks large files and verifies upload

**Variants:**
- `Coveo: Full Catalog Update (No Delete)` - Keep existing items
- `Coveo: Full Catalog Update (Fast - No Verify)` - Skip verification

### 💰 Update Product Prices
**Task:** `Coveo: Update Example - Price Change`
- Enter product URL and new price
- Instant partial update

### 📦 Update Stock Status
**Task:** `Coveo: Update Example - Stock Status`
- Enter product URL and select stock status
- Instant partial update

### 📝 Partial Updates from File
**Task:** `Coveo: Partial Update from File`
- Prompts for JSON file with partial updates
- Supports price changes, inventory updates, field replacements

### ✅ Validate Data Files
**Task:** `Coveo: Validate File`
- Checks file structure and compatibility
- Reports file size and potential issues

### 🔍 Check Recent Operations
**Task:** `Coveo: Check Status (Last Hour)`
- View recent uploads and their status
- Only works after performing at least one operation

### 📁 List Data Files
**Task:** `Coveo: List Available Data Files`
- Shows all JSON files in `data/` directory

### 🌐 Start Website Demo
**Task:** `Start Demo Server`

1. **Update HTML files** (one-time):
   ```bash
   python3 update_html_tokens.py
   ```

2. **Run the task** to start the server

3. **Open in browser:**
   - Main Search: http://localhost:8080/
   - Nike: http://localhost:8080/pages/simple-plp-nike.html
   - Adidas: http://localhost:8080/pages/simple-plp-adidas.html
   - Steve Madden: http://localhost:8080/pages/simple-plp-steve-madden.html

4. **Stop:** Press `Ctrl+C` in terminal

---

## Command Line Reference (Advanced)

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests python-dotenv
```

### Catalog Operations
```bash
# Full update
python3 coveo_catalog_tool.py full-update --file data/complete-payload.json

# Partial update
python3 coveo_catalog_tool.py partial-update --file data/partial-update-template.json
python3 coveo_catalog_tool.py partial-update --operation update_price --document-id "URL" --price 29.99

# Monitoring
python3 coveo_catalog_tool.py status --last-hour
python3 coveo_catalog_tool.py monitor --ordering-id 1716387965000

# Validation
python3 coveo_catalog_tool.py validate --file data/complete-payload.json
python3 coveo_catalog_tool.py list
```

### Website Demo
```bash
# Update tokens
python3 update_html_tokens.py

# Start server
python3 scripts/start_demo_server.py
```