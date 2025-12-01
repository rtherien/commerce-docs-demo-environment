# Coveo Commerce Demo Environment

A simple, ready-to-use online store that shows how Coveo Commerce works. Perfect for testing, learning, and demonstrating Coveo's e-commerce search features.

## 🌟 What You'll Get

### 🛒 **A Complete Online Store**
- A working website with search functionality
- Product pages for golf, hockey, and shoes
- Shopping cart that remembers your items
- Mobile-friendly design

### 🔧 **Easy Product Management**
- Simple tool to add your products to the store
- No coding required - just follow the steps
- Two ways to update: safely add products or replace everything

---

## 🚀 Easy Setup Guide (Anyone Can Do This!)

### Step 1: Setup Configuration

1. **Get your demo API key**:
   - Access the coveodocumentationtest organization and create an API key for the commerce-documentation-catalog-source source.

2. **Set up the configuration**:
   - Copy the demo configuration:
   ```bash
   cp .env.demo .env
   ```
   - Open the `.env` file in any text editor
   - Replace `your-source-api-key-here` with the API Token you created
   - Save the file

3. **Run the setup**:
   ```bash
   ./scripts/setup-secure.sh
   ```

✅ **Setup complete!** You're ready to explore the demo store.

### Step 2: View the Demo Store

The demo already has products loaded! Let's see them:

1. **Open the development environment**:
   ```bash
   source coveo-env/bin/activate
   ```
   (You'll see your command prompt change - this is normal!)

2. **Start the store**:
   ```bash
   python -m http.server 8000
   ```
   
   **Don't see python?** Try this instead:
   ```bash
   python3 -m http.server 8000
   ```

3. **Open your web browser** and go to:
   ```
   http://localhost:8000
   ```

4. **Explore the features**:
   - Search for products in the search box
   - Browse categories (Golf, Hockey, Shoes) from the menu
   - Click on products to see detail pages
   - Add items to your cart and test checkout

🎉 **You're now exploring a live Coveo Commerce demo!**
   ```
   http://localhost:8000
   ```

3. **You should see**:
   - A working online store
   - A search box you can type in
   - Products you can click on
   - Categories in the menu (Golf, Hockey, Shoes)

🎉 **Congratulations!** Your Coveo Commerce demo is running!

---

## 📦 Want to Add Your Own Products? (Optional!)

The demo store already has products, but you can experiment by adding your own:

### Quick Product Loading

1. **Activate the tool**:
   ```bash
   source coveo-env/bin/activate
   ```

2. **Use the interactive menu**:
   ```bash
   ./coveo-loader
   ```

3. **Follow the prompts**:
   - Pick a file from the list (use arrow keys, press Enter)
   - Choose "Update" to safely add products, or "Load" to replace everything
   - Wait for it to finish!

### Understanding Your Options

**🟢 UPDATE (Recommended - Safe Option)**
- **What it does**: Adds new products and updates existing ones
- **What it keeps**: All existing demo products stay
- **When to use**: When you want to experiment with adding more products
- **Example**: Demo has 50 products, add a file with 20 more → You'll have 70 products

**🔴 LOAD (Use Carefully - Replaces Everything)**
- **What it does**: Removes ALL existing products and replaces them
- **What it keeps**: Nothing - completely fresh start  
- **When to use**: When you want to completely start over with your own product set
- **Example**: Demo has 50 products, load a file with 20 → You'll have only those 20 products

### Command Line Method (For Advanced Users)

If you prefer typing commands:

```bash
# See what product files are available
./coveo-loader --list

# Add products safely (recommended)
./coveo-loader --file your-products.json --operation update

# Replace all products (be careful!)
./coveo-loader --file your-products.json --operation load
```

### Adding Your Own Products

1. **Create a product file**:
   - Look at `data/full-product-payload-sample.json` to see the format
   - Copy that file and modify it with your products
   - Save it in the `data/` folder

2. **Upload your products**:
   - Use the interactive menu method above
   - Choose your file from the list
   - Select "Update" to add them safely

---

## 🧪 Exploring the Demo Features

Here's what you can test in the demo store:

### 1. Search Functionality

1. **Go to your store**: `http://localhost:8000`
2. **Try searching**:
   - Type product names like "golf", "hockey stick", or "shoes"
   - Try searching for brands, colors, or categories
   - Notice how results appear instantly and are highly relevant

3. **Test the filters**:
   - Use the filters on the left side
   - Try different categories, prices, brands
   - See how the results update dynamically

### 2. Product Listing Pages (PLPs)

Explore products organized by category:

1. **Golf Products**:
   - Click "Golf" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-golf.html`
   - Browse golf clubs, balls, accessories

2. **Hockey Products**:
   - Click "Hockey" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-hockey.html`
   - Explore sticks, skates, protective gear

3. **Shoes**:
   - Click "Shoes" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-shoes.html`
   - Check out running shoes, cleats, boots

### 3. Product Detail Pages

1. **Click on any product** from search or category pages
2. **Explore the features**:
   - Product images and descriptions
   - Price and availability
   - "Add to Cart" functionality
   - Related products recommendations at the bottom

### 4. Shopping Cart Experience

1. **Add products to cart** from any page
2. **Test the cart features**:
   - Click the cart icon (top right)
   - View your selected products
   - Adjust quantities
   - Remove items
   - Experience the checkout flow

### If You Added Your Own Products

After uploading new products, wait 2-3 minutes for processing, then:

- **Search for your new products** by name, brand, or category
- **Check the appropriate category pages** to ensure they appear correctly
- **Test that product detail pages** load properly
- **Verify cart functionality** works with your products

### Common Issues and Solutions

**❌ Products not showing up after upload?**
- Wait 2-3 minutes after uploading (Coveo needs time to process)
- Try refreshing the browser page
- Make sure the upload completed successfully (look for "Success!" message)
- Verify your API key is correct in the `.env` file

**❌ "Authentication failed" or "Access denied"?**
- Double-check the API Token in your `.env` file
- Make sure you created the API key for the correct source
- Contact the demo provider if you need help creating the API key

**❌ Images not loading?**
- This is normal for the demo - images are placeholders
- Focus on the search, filtering, and cart functionality

**❌ Search not working?**
- Make sure your web server is running (`python -m http.server 8000`)
- Check the browser console for error messages (F12 → Console tab)

**❌ Categories empty?**
- The demo should have products by default
- If you uploaded your own data, make sure products have the right category field
- Check the sample file to see how categories should be formatted

---

## 💡 What This Demo Shows

This online store demonstrates all the key features of Coveo Commerce:

### 🔍 **Smart Search**
- Search for products by name, brand, color, or description
- Intelligent suggestions and auto-complete
- Fast, relevant results every time

### 🏷️ **Product Categories**
- **Golf Equipment**: Clubs, balls, bags, and accessories
- **Hockey Equipment**: Sticks, skates, helmets, and gear
- **Athletic Shoes**: Running, training, and sport-specific footwear

### 🛒 **Shopping Experience**
- Product detail pages with full information
- Shopping cart that remembers your selections
- Mobile-friendly design that works on any device

### 📊 **Behind the Scenes**
- Every click and search is tracked for analytics
- Real-time inventory and product updates
- Scalable system that grows with your business

