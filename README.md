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

### Step 1: Download and Run Setup

1. **Download the demo**:
   - Go to: https://github.com/rtherien/commerce-docs-demo-environment
   - Click the green "Code" button
   - Select "Download ZIP"
   - Unzip the file somewhere easy to find (like your Desktop)

2. **Open Terminal and navigate to the folder**:
   - Open Terminal (Mac) or Command Prompt (Windows)
   - Navigate to the folder you unzipped

3. **Set up the demo configuration**:
   ```bash
   cp .env.demo .env
   ./scripts/setup-secure.sh
   ```

✅ **That's it!** The demo is pre-configured to work right away - no account setup needed.

### Step 2: Add Sample Products

Time to put some products in your store! We'll start with sample products:

1. **Activate the tool**:
   ```bash
   source coveo-env/bin/activate
   ```
   (You'll see your command prompt change - this is normal!)

2. **Load the sample products**:
   ```bash
   ./coveo-loader --file full-product-payload-sample.json --operation load
   ```

3. **Wait for it to finish**:
   - You'll see messages about uploading products
   - When it says "Success!" you're done
   - This usually takes 1-2 minutes

🎉 **Your store now has products!** Let's see them in action.

### Step 3: Open Your Store

Now for the fun part - seeing your store work:

1. **Start the store**:
   ```bash
   python -m http.server 8000
   ```
   
   **Don't see python?** Try this instead:
   ```bash
   python3 -m http.server 8000
   ```

2. **Open your web browser** and go to:
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

## 📦 Managing Your Products (No Coding Required!)

### The Easy Way: Interactive Menu

The simplest way to manage products is using the interactive menu:

1. **Open Terminal** and navigate to your demo folder
2. **Activate the tool**:
   ```bash
   source coveo-env/bin/activate
   ```
3. **Start the menu**:
   ```bash
   ./coveo-loader
   ```
4. **Follow the prompts**:
   - Pick a file from the list (use arrow keys, press Enter)
   - Choose "Update" or "Load" (see below for which to pick)
   - Wait for it to finish!

### Understanding Update vs Load

**🟢 UPDATE (Recommended - Safe Option)**
- **What it does**: Adds new products and updates existing ones
- **What it keeps**: All your existing products stay
- **When to use**: When you want to add more products or change some details
- **Example**: You have 100 products, add a file with 20 more → You'll have 120 products

**🔴 LOAD (Use Carefully - Replaces Everything)**
- **What it does**: Removes ALL existing products and replaces them
- **What it keeps**: Nothing - completely fresh start  
- **When to use**: When you want to completely start over
- **Example**: You have 100 products, load a file with 20 → You'll have only those 20 products

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

## 🧪 Testing Your Changes

After you add or update products, here's how to see if everything worked:

### 1. Check the Search Page

1. **Go to your store**: `http://localhost:8000`
2. **Try searching**:
   - Type a product name in the search box
   - Try searching for brands, colors, or categories
   - Your new products should appear in results

3. **Test the filters**:
   - Use the filters on the left side
   - Try different categories, prices, brands
   - Make sure your products show up in the right categories

### 2. Check Product Listing Pages (PLPs)

Product Listing Pages show products by category. Test each one:

1. **Golf Products**:
   - Click "Golf" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-golf.html`
   - You should see golf clubs, balls, accessories

2. **Hockey Products**:
   - Click "Hockey" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-hockey.html`
   - You should see sticks, skates, protective gear

3. **Shoes**:
   - Click "Shoes" in the menu, or go to: `http://localhost:8000/website/pages/simple-plp-shoes.html`
   - You should see running shoes, cleats, boots

### 3. Test Individual Product Pages

1. **Click on any product** from search or category pages
2. **Check that you see**:
   - Product images
   - Product name and description
   - Price
   - "Add to Cart" button works
   - Related products at the bottom

### 4. Test the Shopping Cart

1. **Add products to cart** from any page
2. **Check the cart**:
   - Click the cart icon (top right)
   - Your products should be listed
   - Quantities and prices should be correct
   - Try removing items

### Common Issues and Solutions

**❌ Products not showing up?**
- Wait 2-3 minutes after uploading (Coveo needs time to process)
- Try refreshing the browser page
- Make sure the upload completed successfully (look for "Success!" message)

**❌ Images not loading?**
- This is normal for the demo - images are placeholders
- Your real products can use real image URLs

**❌ Search not working?**
- Make sure your web server is running (`python -m http.server 8000`)
- Check the browser console for error messages (F12 → Console tab)

**❌ Categories empty?**
- Make sure your products have the right category field
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

---

## 🤝 Need Help?

### For Non-Technical Users:
- 📧 **Questions about setup**: Create an issue with "help wanted" label
- 🐛 **Something not working**: Describe what you expected vs what happened
- 💡 **Ideas for improvement**: We'd love to hear them!

### For Developers:
- 📖 **Technical docs**: Check the `docs/` folder for troubleshooting
- 🐛 **Issues or bugs**: Report them on GitHub
- 🚀 **Advanced usage**: Check the source code in `tools/`

### Useful Resources:
- [Coveo Commerce Documentation](https://docs.coveo.com/en/p8bg0188/coveo-for-commerce/build-search-interfaces)
- [Report Issues](https://github.com/rtherien/commerce-docs-demo-environment/issues)
- [Ask Questions](https://github.com/rtherien/commerce-docs-demo-environment/discussions)
