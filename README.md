# Coveo Commerce API Loader

A professional Python tool for loading catalog data into Coveo Commerce sources using the Coveo Stream API.

## ✨ Features

- 🚀 **Two Operation Types**: Support for both Update and Load operations
- 📁 **Easy File Selection**: Interactive mode to choose from your data payloads
- 🔧 **Command Line Interface**: Batch operations for automation
- 📊 **Payload Analysis**: Automatic analysis and display of payload contents
- ⚡ **Error Handling**: Comprehensive error messages and retry guidance
- 🛡️ **Safety Features**: Confirmations for destructive operations
- 📦 **Professional Structure**: Organized codebase with proper Python packaging

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd commerce-docs-demo-environment

# Run automated setup
./scripts/setup.sh

# Configure credentials
# Edit config.json with your Coveo details

# Start using
source coveo-env/bin/activate
./coveo-loader
```

## 📁 Project Structure

```
commerce-docs-demo-environment/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   └── loader.py                # Main loader implementation
├── data/                        # Payload files
│   ├── full-product-payload-sample.json
│   ├── new-availability.json
│   └── ...
├── assets/                      # Images and media files
├── examples/                    # HTML examples and demos
├── docs/                        # Documentation
│   ├── getting-started.md
│   ├── api.md
│   └── ...
├── scripts/                     # Setup and utility scripts
│   └── setup.sh
├── coveo-loader                 # CLI executable
├── config.json                  # Your configuration (create from template)
├── config.template.json         # Configuration template
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Python project configuration
├── LICENSE                      # MIT License
└── README.md                   # This file
```

## 🔧 Installation

### Option 1: Automated Setup (Recommended)

```bash
./scripts/setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv coveo-env
source coveo-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config.template.json config.json
# Edit config.json with your Coveo credentials

# Make CLI executable
chmod +x coveo-loader
```

## ⚙️ Configuration

Edit `config.json` with your Coveo details:

```json
{
  "organization_id": "your-org-id-here",
  "source_id": "your-source-id-here",
  "access_token": "your-api-key-here"
}
```

**Need help finding these values?** See [Getting Started Guide](docs/getting-started.md#configuration).

## 🎯 Usage

### Interactive Mode (Recommended)

```bash
source coveo-env/bin/activate
./coveo-loader
```

### Command Line Mode

```bash
# Update operation (recommended)
./coveo-loader --file full-product-payload-sample.json --operation update

# Load operation (replaces all data)
./coveo-loader --file full-product-payload-sample.json --operation load

# List available files
./coveo-loader --list

# Help
./coveo-loader --help
```

## 📚 Documentation

- [🚀 Getting Started](docs/getting-started.md) - Setup and first run
- [📖 API Reference](docs/api.md) - Detailed API documentation
- [🔧 Operations Guide](docs/operations.md) - Update vs Load operations
- [📄 Payload Format](docs/payload-format.md) - JSON structure reference
- [🔍 Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🎯 Operation Types

### Update Operations (Recommended)

- ✅ **Safer**: Only updates/adds items included in your payload
- ✅ **Preserves Data**: Existing items not in payload remain unchanged
- ✅ **Efficient**: Better performance and faster processing
- ✅ **Flexible**: Optional cleanup of old items

### Load Operations

- ⚠️ **Replaces Everything**: Completely overwrites all data in your source
- ⚠️ **Resource Intensive**: Requires processing all data at once
- ⚠️ **Delayed Processing**: 15-minute delay for old item removal

## 📊 Examples

### Quick Data Upload

```bash
./coveo-loader --file data/new-availability.json --operation update
```

### Complete Catalog Replacement

```bash
./coveo-loader --file data/full-product-payload-sample.json --operation load
```

### Automated Daily Updates

```bash
#!/bin/bash
source coveo-env/bin/activate
./coveo-loader --file data/daily-updates.json --operation update --delete-old
```

## 🛡️ Security Notes

- Keep your `config.json` secure - it contains API credentials
- Never commit API keys to version control
- Use separate API keys for different environments
- Regularly rotate your API keys

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Coveo Documentation](https://docs.coveo.com/en/p4eb0129/)
- 🐛 [Report Issues](https://github.com/rtherien/commerce-docs-demo-environment/issues)
- 💬 [Coveo Community](https://community.coveo.com/)

---

💡 **Pro Tip**: Always test with small payloads first, especially when learning the API. Use Update operations for most use cases as they're safer and more efficient than Load operations.
