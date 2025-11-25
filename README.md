# Coveo Commerce Data Loader

A simple tool to upload product data to your Coveo Commerce search.

## 🚀 Quick Setup (5 minutes)

### 1. Download and Setup

```bash
git clone <your-repo-url>
cd commerce-docs-demo-environment
./scripts/setup-secure.sh
```

### 2. Get Your Coveo Information

Go to [Coveo Administration Console](https://platform.cloud.coveo.com/) and find:

- **Organization ID**: On your main dashboard
- **Source ID**: Go to Sources → Find your commerce source → Copy the ID
- **API Key**: Go to API Keys → Create New Key (select "Push" permission)

### 3. Add Your Information

```bash
cp .env.example .env
nano .env  # Edit this file with your Coveo info
```

Your `.env` file should look like:

```
COVEO_ORGANIZATION_ID=your-org-name
COVEO_SOURCE_ID=your-source-id-here
COVEO_ACCESS_TOKEN=your-api-key-here
COVEO_IMAGE_BASE_URL=https://your-website.com/images
```

### 4. Run It!

```bash
source coveo-env/bin/activate
./coveo-loader
```

## 📋 How to Use

### Simple Mode (Recommended)

1. Run `./coveo-loader`
2. Pick a data file from the list
3. Choose "Update" (safe) or "Load" (replaces everything)
4. Done!

### Command Line

```bash
# See available data files
./coveo-loader --list

# Upload specific file (safe update)
./coveo-loader --file full-product-payload-sample.json --operation update

# Replace all data (careful!)
./coveo-loader --file full-product-payload-sample.json --operation load
```

## 📁 Your Data Files

Put your product data files (JSON format) in the `data/` folder. The tool will find them automatically.

## ⚠️ Important Notes

- **Update**: Adds/changes products, keeps existing ones
- **Load**: Replaces ALL products with your file
- Your API keys are safe and not shared in the code

## 🆘 Need Help?

- Check [Coveo Documentation](https://docs.coveo.com/en/p4eb0129/)
- Create an [Issue](https://github.com/rtherien/commerce-docs-demo-environment/issues)
