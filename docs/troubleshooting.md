# Troubleshooting

This guide helps you resolve common issues when using the Coveo Commerce Demo.

## Setup Issues

### "Permission denied: ./scripts/setup-secure.sh"

**Solution**: Make the script executable:
```bash
chmod +x ./scripts/setup-secure.sh
```

### "Python command not found"

**Problem**: Python not installed or not in PATH.

**Solutions**:
1. Install Python 3.7+ from [python.org](https://python.org)
2. On macOS with Homebrew: `brew install python3`
3. Verify installation: `python3 --version`

### "Module not found: requests"

**Problem**: Virtual environment not activated or dependencies not installed.

**Solution**: 
```bash
source coveo-env/bin/activate
pip install -r requirements.txt
```

Or re-run the setup:
```bash
./scripts/setup-secure.sh
```

## Product Loading Issues

### "Configuration file not found"

**Problem**: `.env` file doesn't exist.

**Solution**:
```bash
cp .env.demo .env
```

### "No items uploaded" or "Upload failed"

**Solutions**:
1. Make sure you're in the right directory
2. Activate the virtual environment: `source coveo-env/bin/activate`
3. Check that the data file exists: `ls data/`
4. Try the interactive loader: `./coveo-loader`

### "Command not found: ./coveo-loader"

**Solutions**:
1. Make the script executable: `chmod +x coveo-loader`
2. Make sure you're in the project root directory
3. Re-run setup: `./scripts/setup-secure.sh`

## Website Issues

### "Search not working" 

**Solutions**:
1. Make sure your web server is running: `python -m http.server 8000`
2. Wait 2-3 minutes after uploading products (Coveo needs time to process)
3. Try refreshing the browser page
4. Check browser console for errors (F12 → Console tab)

### "Products not showing up"

**Solutions**:
1. Wait 2-3 minutes after uploading (processing time)
2. Try refreshing the browser
3. Check that the upload completed successfully (look for "Success!" message)
4. Try loading products again: `./coveo-loader --file full-product-payload-sample.json --operation load`

### "Images not loading"

**Expected behavior**: This is normal for the demo - images are placeholders. The important thing is that product information, search, and cart functionality work.

### "Categories empty"

**Solutions**:
1. Make sure you loaded the sample data: `./coveo-loader --file full-product-payload-sample.json --operation load`
2. Wait a few minutes for processing
3. Check that you're going to the right URLs:
   - Golf: `http://localhost:8000/website/pages/simple-plp-golf.html`
   - Hockey: `http://localhost:8000/website/pages/simple-plp-hockey.html`  
   - Shoes: `http://localhost:8000/website/pages/simple-plp-shoes.html`

### "localhost:8000 not accessible"

**Solutions**:
1. Make sure the web server is running: `python -m http.server 8000` or `python3 -m http.server 8000`
2. Check that port 8000 isn't being used by another application
3. Try a different port: `python -m http.server 8001` and use `http://localhost:8001`

## Getting More Help

If you're still experiencing issues:

1. **Check the terminal output** for error messages
2. **Try the interactive loader**: `./coveo-loader` and follow the prompts
3. **Report issues**: [Create a GitHub issue](https://github.com/rtherien/commerce-docs-demo-environment/issues) with:
   - What you were trying to do
   - What error message you got
   - Your operating system (Mac, Windows, Linux)

## Quick Reset

If everything seems broken, try a complete reset:

```bash
# Remove the virtual environment
rm -rf coveo-env

# Re-run setup
cp .env.demo .env
./scripts/setup-secure.sh

# Load sample data
source coveo-env/bin/activate
./coveo-loader --file full-product-payload-sample.json --operation load

# Start the website
python -m http.server 8000
```

Then go to `http://localhost:8000` in your browser.