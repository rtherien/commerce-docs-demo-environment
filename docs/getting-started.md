# Getting Started

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd commerce-docs-demo-environment
   ```

2. **Run the setup script**:
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure your credentials**:
   Edit `config.json` with your Coveo organization details.

4. **Start using the loader**:
   ```bash
   source coveo-env/bin/activate
   ./coveo-loader
   ```

## Prerequisites

- Python 3.7 or higher
- A Coveo organization with Commerce features enabled
- A Catalog source in your Coveo organization
- An API key with push privileges

## Installation

### Automated Setup (Recommended)

Use the provided setup script:

```bash
./scripts/setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Set up configuration template
- Make scripts executable

### Manual Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv coveo-env
   source coveo-env/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-core.txt
   ```

3. **Create configuration**:
   ```bash
   cp config.template.json config.json
   # Edit config.json with your details
   ```

## Configuration

### Finding Your Credentials

#### Organization ID
1. Log into [Coveo Administration Console](https://platform.cloud.coveo.com/)
2. Click your organization name → **Settings** → **Organization**
3. Copy the **Organization ID**

#### Source ID  
1. In Admin Console → **Content** → **Sources**
2. Click on your Catalog source
3. Copy the **Source ID** from the URL or source details

#### Access Token
1. In Admin Console → **Administration** → **API Keys**
2. Create a new API key or use an existing one
3. Ensure it has **Push** privileges for your source
4. Copy the generated token

### Configuration File

Edit `config.json`:

```json
{
  "organization_id": "your-org-id-here",
  "source_id": "your-source-id-here", 
  "access_token": "your-api-key-here"
}
```

## First Run

### Interactive Mode

The easiest way to get started:

```bash
source coveo-env/bin/activate
./coveo-loader
```

Follow the prompts to:
1. Select a payload file from the `data/` directory
2. Choose operation type (Update recommended for first use)
3. Confirm and execute

### Command Line Mode

For direct execution:

```bash
source coveo-env/bin/activate
./coveo-loader --file full-product-payload-sample.json --operation update
```

## Verifying Success

After running an operation:

1. **Check the script output** for success messages
2. **Monitor indexing** in Coveo Admin Console:
   - **Content** → **Activity** → **Indexing Status**
3. **Review logs** in **Content** → **Logs** → **Log Browser**
4. **Test search results** to verify data appears

## Next Steps

- Learn about [payload formats](payload-format.md)
- Understand [operation types](operations.md)
- Review [troubleshooting guide](troubleshooting.md)
- Explore [example payloads](../examples/)