# 🔐 Security Guide

## ⚠️ Important: Your Repository Has Exposed Credentials!

Your current `config.json` contains API keys that are tracked in git. Follow these steps to secure your repository:

## 🚨 Immediate Action Required

### 1. Remove Exposed Credentials from Git History

```bash
# Remove config.json from git tracking
git rm --cached config.json

# Commit the removal
git commit -m "🔐 Remove exposed API credentials from version control"

# Push changes
git push origin main
```

### 2. Regenerate Your API Keys

Your current API keys have been exposed in git history. You should:

1. Go to [Coveo Administration Console](https://platform.cloud.coveo.com/)
2. Navigate to **API Keys**
3. **Revoke** your current access token
4. **Create a new** access token
5. Update your local configuration with the new token

## 🛡️ Secure Setup (Going Forward)

### Option 1: Environment Variables (Recommended)

```bash
# Set your credentials as environment variables
export COVEO_ORGANIZATION_ID="your-org-id"
export COVEO_SOURCE_ID="your-source-id"
export COVEO_ACCESS_TOKEN="your-new-api-key"

# Add to your shell profile for persistence
echo 'export COVEO_ORGANIZATION_ID="your-org-id"' >> ~/.bashrc
echo 'export COVEO_SOURCE_ID="your-source-id"' >> ~/.bashrc
echo 'export COVEO_ACCESS_TOKEN="your-new-api-key"' >> ~/.bashrc
```

### Option 2: Local .env File

```bash
# Copy the environment template
cp .env.example .env

# Edit with your actual credentials
nano .env

# The .env file is automatically ignored by git
```

### Option 3: Local config.json (Less Secure)

```bash
# Copy the template
cp config.template.json config.json

# Edit with your credentials
nano config.json

# config.json is now ignored by git
```

## 🔄 Using the Updated Loader

The loader now supports multiple configuration methods with this priority:

1. **Environment variables** (highest priority, most secure)
2. **config.json file** (if environment variables not set)
3. **Error if neither available**

```bash
# The loader will automatically detect and use environment variables
./coveo-loader

# Or specify a custom config file
./coveo-loader --config my-config.json
```

## 🛠️ Quick Secure Setup

Run the secure setup script:

```bash
./scripts/setup-secure.sh
```

This script will:

- Set up Python environment
- Create `.env` file from template
- Guide you through credential setup
- Ensure security best practices

## ✅ Security Checklist

- [ ] Remove `config.json` from git tracking
- [ ] Regenerate API keys in Coveo Console
- [ ] Set up environment variables or `.env` file
- [ ] Test loader with new secure configuration
- [ ] Commit security improvements to git

## 🔍 Verification

Test that credentials are loaded securely:

```bash
# Should show "Loaded credentials from environment variables (secure)"
./coveo-loader --list
```

## 📚 Additional Resources

- [Coveo API Key Management](https://docs.coveo.com/en/1707/cloud-v2-developers/manage-api-keys)
- [Git Security Best Practices](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)
- [Environment Variable Security](https://12factor.net/config)
