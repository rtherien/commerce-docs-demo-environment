# Coveo Commerce Demo Environment

A complete Coveo Commerce implementation featuring a data loader tool and a fully functional e-commerce website with search, product listings, cart functionality, and comprehensive analytics tracking.

## 🌟 What's Included

### 🔧 **Data Loader Tool**

- Upload product data to Coveo Commerce
- Interactive command-line interface
- Safe update and full load operations
- Automatic data validation

### 🛒 **Complete E-commerce Website**

- Search-focused homepage with global product search
- Product listing pages (PLPs) for different categories
- Dynamic product detail pages (PDPs)
- Shopping cart with persistent storage
- Purchase completion with Coveo analytics tracking
- Responsive design for mobile and desktop

---

## 🚀 Quick Setup (5 minutes)

### 1. Download and Setup

```bash
git clone https://github.com/rtherien/commerce-docs-demo-environment.git
cd commerce-docs-demo-environment
./scripts/setup-secure.sh
```

### 2. Get Your Coveo Information

Go to [Coveo Administration Console](https://platform.cloud.coveo.com/) and find:

- **Organization ID**: On your main dashboard
- **Source ID**: Go to Sources → Find your commerce source → Copy the ID
- **API Key**: Go to API Keys → Create New Key (select "Push" permission)

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit this file with your Coveo info
```

Your `.env` file should look like:

```env
COVEO_ORGANIZATION_ID=your-org-name
COVEO_SOURCE_ID=your-source-id-here
COVEO_ACCESS_TOKEN=your-api-key-here
COVEO_IMAGE_BASE_URL=../assets/images  # For local development
```

> 💡 **Image Configuration**: The demo uses flexible image hosting. For local development, use `../assets/images`. For GitHub hosting, use `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/website/assets/images`. See [Image Hosting Guide](docs/image-hosting.md) for details.

### 4. Load Sample Data

```bash
source coveo-env/bin/activate
./coveo-loader --file full-product-payload-sample.json --operation load
```

> 💡 **New Template System**: We now use `full-product-payload-sample.json` which automatically uses your configured image URLs. No more manual URL updates needed!

### 5. Run the Website

```bash
# Start local web server (required for Coveo APIs)
python -m http.server 8000
# or
npx serve .
```

Open `http://localhost:8000` in your browser. You'll be redirected to the sports store demo.

---

## 📋 Data Loader Usage

### Interactive Mode (Recommended)

```bash
./coveo-loader
```

1. Pick a data file from the list
2. Choose "Update" (safe) or "Load" (replaces everything)
3. Done!

### Command Line Mode

```bash
# See available data files
./coveo-loader --list

# Upload specific file (safe update)
./coveo-loader --file full-product-payload-sample.json --operation update

# Replace all data (careful!)
./coveo-loader --file full-product-payload-sample.json --operation load
```

### Data File Format

Place your product data files (JSON format) in the `data/` folder. See `data/full-product-payload-sample.json` for the expected format.

---

## 🛒 E-commerce Website Features

### 🏠 Homepage Search (`website/pages/index.html`)

- Global search functionality across all products
- Advanced faceting and filtering capabilities
- Sort options and pagination
- Direct add-to-cart from search results

### 📱 Product Categories

Navigate through product categories via dropdown menu:

- **Golf Equipment** (`website/pages/plp-golf.html`)
- **Hockey Equipment** (`website/pages/plp-hockey.html`)
- **Athletic Shoes** (`website/pages/plp-shoes.html`)

### 🔍 Product Detail Pages (`website/pages/pdp.html`)

- Dynamic URL-based product lookup (`pdp.html?id=PRODUCT_ID`)
- Full product information and images
- Related products recommendations
- Add to cart functionality

### 🛒 Shopping Cart System

- **Persistent cart** using localStorage
- Add/remove items with quantity controls
- Real-time price calculations (CAD)
- Slide-out cart sidebar
- **Complete purchase simulation** with Coveo analytics

### 📊 Analytics & Tracking

The website tracks comprehensive e-commerce events:

- **Page Views**: Navigation and browsing
- **Product Views**: Product detail page visits
- **Add to Cart**: Cart interactions
- **Purchase Events**: Completed transactions
- **Search Events**: Query interactions
- **Facet Usage**: Filter selections

---

## 📁 Repository Structure

```
├── index.html                    # Landing page with auto-redirect
├── coveo-loader                  # Data upload CLI tool
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
├── website/                      # Complete e-commerce website
│   ├── pages/
│   │   ├── index.html           # Main search homepage
│   │   ├── pdp.html             # Product detail page template
│   │   ├── plp-golf.html        # Golf equipment listing
│   │   ├── plp-hockey.html      # Hockey equipment listing
│   │   └── plp-shoes.html       # Athletic shoes listing
│   ├── styles/
│   │   └── main.css             # Complete website styling
│   ├── js/
│   │   ├── cart.js              # Shopping cart functionality
│   │   └── coveo-analytics.js   # Analytics tracking
│   └── assets/
│       └── images/              # Product images and assets
├── tools/                        # Development and data tools
│   └── data_loader/
│       └── loader.py            # Python data loader implementation
├── data/
│   └── *.json                   # Product data files
├── scripts/
│   ├── setup.sh                 # Basic setup script
│   └── setup-secure.sh          # Secure setup with virtual env
└── docs/                        # Documentation files
```

---

## 🔧 Technical Implementation

### Coveo Configuration

- **Organization ID**: `coveodocumentationtest` (demo)
- **Tracking ID**: `commerce-docs-demo`
- **Environment**: Production
- **Currency**: Canadian Dollar (CAD)
- **Platform**: Coveo Cloud

### Cart Management

- **Persistence**: localStorage for cross-session cart
- **Structure**: JSON-based with product metadata
- **Updates**: Real-time UI synchronization
- **Checkout**: Simulated transaction flow

### Analytics Integration

- **Platform**: Coveo Atomic Commerce Analytics
- **Events**: Complete e-commerce event tracking
- **Correlation**: Proper user journey tracking
- **Error Handling**: Graceful fallbacks for analytics failures

---

## 🌐 Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **Requirements**: ES6+ JavaScript support
- **Design**: Fully responsive (mobile and desktop)
- **Dependencies**: JavaScript enabled required for functionality

---

## ⚠️ Important Notes

### Data Operations

- **Update**: Safely adds/changes products, preserves existing data
- **Load**: Completely replaces ALL products with new data
- **Security**: API keys stored locally and never committed to git

### Local Development

- **Web Server Required**: Coveo APIs require serving over HTTP/HTTPS
- **Python Option**: `python -m http.server 8000`
- **Node.js Options**: `npx serve .` or `npx http-server`
- **Access**: Open `http://localhost:8000` after starting server

---

## 📚 Documentation & Resources

- 📖 **Getting Started**: [docs/getting-started.md](docs/getting-started.md)
- 🔧 **API Documentation**: [docs/api.md](docs/api.md)
- 🚀 **Image Hosting**: [docs/image-hosting.md](docs/image-hosting.md)
- 🔍 **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

### External Resources

- [Coveo Commerce Documentation](https://docs.coveo.com/en/p8bg0188/coveo-for-commerce/build-search-interfaces)
- [Coveo Analytics Events](https://docs.coveo.com/en/p9499444/coveo-for-commerce/event-tracking-with-atomic)
- [Product Listing Pages](https://docs.coveo.com/en/p8dg0472/coveo-for-commerce/build-product-listing-pages)
- [Authentication Guide](https://docs.coveo.com/en/o8ld0051/coveo-for-commerce/authenticate-commerce-requests)

---

## 🆘 Support & Contributing

- 🐛 **Report Issues**: [GitHub Issues](https://github.com/rtherien/commerce-docs-demo-environment/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/rtherien/commerce-docs-demo-environment/discussions)
- 📧 **Questions**: Create an issue with the `question` label

---

## ✅ Key Features Demonstrated

- ✅ **Search Interface**: Full-text search with Coveo Atomic
- ✅ **Product Listing Pages**: Category-specific product displays
- ✅ **Product Detail Pages**: Individual product views with details
- ✅ **Shopping Cart**: Complete cart functionality with persistence
- ✅ **Purchase Tracking**: Full e-commerce analytics pipeline
- ✅ **Responsive Design**: Mobile and desktop compatibility
- ✅ **Navigation System**: Dropdown menu and category organization
- ✅ **Event Tracking**: Comprehensive user interaction analytics
- ✅ **Data Management**: Product upload and management tools

This demo provides a complete, production-ready foundation for Coveo Commerce implementations.
