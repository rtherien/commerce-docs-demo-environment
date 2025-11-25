# Image Hosting Configuration

This demo supports flexible image hosting for maximum portability. Instead of hardcoding image URLs, we use template-based configuration.

## How It Works

1. **Template Files**: Product data files use `{{IMAGE_BASE_URL}}` placeholders instead of hardcoded URLs
2. **Runtime Replacement**: The data loader automatically replaces these placeholders with your configured base URL
3. **Environment Configuration**: You control the image URLs through the `COVEO_IMAGE_BASE_URL` environment variable

## Configuration Options

### Option 1: Local Development (Default)
```bash
COVEO_IMAGE_BASE_URL=../assets/images
```
- Images served from local website/assets/images folder
- Works immediately after cloning the repository
- Perfect for development and testing

### Option 2: GitHub Hosting
```bash
COVEO_IMAGE_BASE_URL=https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/website/assets/images
```
- Images served from GitHub's raw content CDN
- Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual values
- Works for public repositories without additional setup

### Option 3: Custom CDN
```bash
COVEO_IMAGE_BASE_URL=https://your-cdn.com/assets
```
- Use any CDN or image hosting service
- Best performance for production environments

## Files Structure

```
data/
├── product-data-template.json    # Template with {{IMAGE_BASE_URL}} placeholders
└── full-product-payload-sample.json  # Legacy file with hardcoded URLs (kept for reference)
```

## Usage

1. **Choose your hosting method** and set `COVEO_IMAGE_BASE_URL` in your `.env` file
2. **Load the template file** using the data loader:
   ```bash
   ./coveo-loader --file product-data-template.json --operation load
   ```
3. **The loader automatically replaces** `{{IMAGE_BASE_URL}}` with your configured URL

## Example Replacement

Template file contains:
```json
"ec_images": ["{{IMAGE_BASE_URL}}/red-soccer-shoes.png"]
```

With `COVEO_IMAGE_BASE_URL=../assets/images`, becomes:
```json
"ec_images": ["../assets/images/red-soccer-shoes.png"]
```

With `COVEO_IMAGE_BASE_URL=https://cdn.example.com/images`, becomes:
```json
"ec_images": ["https://cdn.example.com/images/red-soccer-shoes.png"]
```

## Benefits

- **Zero Configuration**: Works immediately with relative paths
- **Portable**: Easy to fork/clone without manual URL updates
- **Flexible**: Switch between local, GitHub, or CDN hosting
- **Production Ready**: Use CDN URLs for optimal performance

## Migration from Hardcoded URLs

If you have existing files with hardcoded URLs, you can create template versions by:

1. Copy your data file
2. Replace all image URLs with `{{IMAGE_BASE_URL}}/filename.ext`
3. Set your preferred `COVEO_IMAGE_BASE_URL`
4. Load the template file instead

## Current Images

Your demo includes these product images:
- `red-soccer-shoes.png`
- `blue-soccer-shoes.png` 
- `yellow-soccer-shoes.jpg`
- `black-soccer-shoes.jpg`
- `black-hockey-stick.jpg`
- `red-hockey-stick.jpg`
- `golf-driver.jpg`

All located in: `website/assets/images/`