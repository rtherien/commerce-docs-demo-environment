# Coveo Commerce API Loader

A Python tool for loading catalog data into Coveo Commerce sources using the Coveo Stream API.

## Quick Start

```bash
# Setup
git clone <your-repo-url>
cd commerce-docs-demo-environment
./scripts/setup.sh

# Configure
cp config.template.json config.json
# Edit config.json with your Coveo credentials

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

Edit `config.json`:

```json
{
  "organization_id": "your-org-id-here",
  "source_id": "your-source-id-here",
  "access_token": "your-api-key-here"
}
```

Find these values in the [Coveo Administration Console](https://platform.cloud.coveo.com/).

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

## Support

- [Coveo Documentation](https://docs.coveo.com/en/p4eb0129/)
- [Issues](https://github.com/rtherien/commerce-docs-demo-environment/issues)
