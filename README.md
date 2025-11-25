# Coveo Commerce API Loader

A Python tool for loading catalog data into Coveo Commerce sources using the Coveo Stream API.

## Quick Start

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd commerce-docs-demo-environment
./scripts/setup-secure.sh

# 2. Get your Coveo API credentials (see configuration section below)

# 3. Set up your credentials securely
cp .env.example .env
nano .env  # Add your actual Coveo credentials

# 4. Run the loader
source coveo-env/bin/activate
source .env
./coveo-loader
```

## Usage Examples

### Basic Usage

```bash
# Activate environment and load credentials
source coveo-env/bin/activate
source .env  # if using .env file

# Interactive mode (recommended for beginners)
./coveo-loader

# List available data files
./coveo-loader --list

# Load specific file with update operation (safe)
./coveo-loader --file full-product-payload-sample.json --operation update

# Load specific file with load operation (replaces all data)
./coveo-loader --file full-product-payload-sample.json --operation load

# Get help
./coveo-loader --help
```

### Advanced Usage

```bash
# Update with old item cleanup
./coveo-loader --file my-data.json --operation update --delete-old

# Use custom config file
./coveo-loader --config my-custom-config.json --file data.json

# With environment variables set globally
export COVEO_ACCESS_TOKEN="your-token"
./coveo-loader --file data.json  # Will use env vars automatically
```

## 🔐 API Key Configuration

### Step 1: Get Your Coveo Credentials

1. Go to [Coveo Administration Console](https://platform.cloud.coveo.com/)
2. **Organization ID**: Found in the URL or main dashboard
3. **Source ID**: Go to **Sources** → Select your commerce source → Copy the Source ID
4. **Access Token**: Go to **API Keys** → **Create API Key** → Select appropriate privileges:
   - `Push` (required for data loading)
   - `Source Edit` (required for source operations)
   - `Analytics Data` (optional, for analytics)

### Step 2: Secure Configuration (Choose One Method)

#### Method 1: Environment Variables (Most Secure)

```bash
# Set in your terminal session
export COVEO_ORGANIZATION_ID="your-organization-id"
export COVEO_SOURCE_ID="your-source-id-12345"
export COVEO_ACCESS_TOKEN="xx1234567-abcd-1234-efgh-987654321xyz"
export COVEO_IMAGE_BASE_URL="https://your-cdn.com/assets"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export COVEO_ORGANIZATION_ID="your-org-id"' >> ~/.bashrc
echo 'export COVEO_SOURCE_ID="your-source-id"' >> ~/.bashrc
echo 'export COVEO_ACCESS_TOKEN="your-token"' >> ~/.bashrc
source ~/.bashrc
```

#### Method 2: .env File (Recommended for Development)

```bash
# Copy template and edit
cp .env.example .env
nano .env

# Your .env file should look like:
COVEO_ORGANIZATION_ID=your-organization-id
COVEO_SOURCE_ID=your-source-id-12345
COVEO_ACCESS_TOKEN=xx1234567-abcd-1234-efgh-987654321xyz
COVEO_IMAGE_BASE_URL=https://your-cdn.com/assets

# Load environment variables
source .env
```

#### Method 3: Local Config File (Legacy)

```bash
cp config.template.json config.json
nano config.json

# Edit config.json with your actual values
```

### Step 3: Verify Configuration

```bash
# Activate environment
source coveo-env/bin/activate

# Load your credentials (if using .env)
source .env

# Test connection
./coveo-loader --list

# Should show: "✅ Loaded credentials from environment variables (secure)"
```

### 🚨 Security Best Practices

- ✅ **DO**: Use environment variables or `.env` files
- ✅ **DO**: Add `.env` and `config.json` to `.gitignore` (already done)
- ✅ **DO**: Regenerate API keys if accidentally exposed
- ❌ **DON'T**: Commit API keys to version control
- ❌ **DON'T**: Share API keys in chat/email/screenshots
- ❌ **DON'T**: Use production keys in development/testing

### 🔄 Using Your Keys

```bash
# Load environment and run
source coveo-env/bin/activate
source .env  # if using .env file
./coveo-loader

# Or with environment variables already set
./coveo-loader --file your-data.json --operation update
```

## Operation Types

- **Update** (recommended): Adds/updates items in payload, preserves existing data
- **Load**: Replaces ALL data in source with payload content

## Project Structure

```
├── src/           # Python source code
├── data/          # JSON payload files
├── assets/        # Images
├── examples/      # HTML demos
├── docs/          # Documentation
└── scripts/       # Setup tools
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Troubleshooting](docs/troubleshooting.md)
- [🔐 Security Guide](SECURITY.md) - **Important: Securing API credentials**

## Support

- [Coveo Documentation](https://docs.coveo.com/en/p4eb0129/)
- [Issues](https://github.com/rtherien/commerce-docs-demo-environment/issues)
