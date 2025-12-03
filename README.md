# Sports Store - Coveo Commerce Demo

A simple e-commerce demo using Coveo's Atomic Commerce components with the CDN approach.

## Overview

This demo showcases a sports equipment store with:
- **Search page** - Search all products with filters and facets
- **Product Listing Pages (PLPs)** - Category-specific pages for Shoes, Hockey, and Golf
- **Product Detail Page** - Simple product information display

## Features

- ✅ **Coveo Atomic Commerce Components** - Using the official CDN approach
- ✅ **Product Search & Filtering** - Full-text search with faceted navigation
- ✅ **Category Browsing** - Dedicated pages for different sports categories
- ✅ **Analytics Tracking** - Click tracking and user behavior analytics
- ✅ **Responsive Design** - Works on desktop and mobile devices

## Quick Start

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

