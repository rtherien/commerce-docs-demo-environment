# Coveo Commerce API Loader

A Python tool for loading catalog data into Coveo Commerce sources using the Coveo Stream API.

## Quick Start

```bash
# Setup (secure)
git clone <your-repo-url>
cd commerce-docs-demo-environment
./scripts/setup-secure.sh

# Configure with environment variables (secure)
cp .env.example .env
# Edit .env with your Coveo credentials

# Use
source coveo-env/bin/activate
./coveo-loader
```

## Usage

```bash
# Interactive mode (recommended)
./coveo-loader

# Command line
./coveo-loader --file full-product-payload-sample.json --operation update
./coveo-loader --list
./coveo-loader --help
```

## Configuration

### Secure Setup (Recommended)

For security, use environment variables:

```bash
# Set environment variables
export COVEO_ORGANIZATION_ID="your-org-id"
export COVEO_SOURCE_ID="your-source-id"
export COVEO_ACCESS_TOKEN="your-api-key"

# Or use .env file
cp .env.example .env
# Edit .env with your credentials
```

### Alternative: Local Config File

```bash
cp config.template.json config.json
# Edit config.json with your credentials
```

⚠️ **Security Note**: Never commit API keys to version control! The loader prioritizes environment variables for security.

Find your credentials in the [Coveo Administration Console](https://platform.cloud.coveo.com/).

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
