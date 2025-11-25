# Troubleshooting

This guide helps you resolve common issues when using the Coveo Commerce API Loader.

## Common Error Messages

### "Module not found: requests"

**Problem**: Python requests library not installed.

**Solution**: 
```bash
source coveo-env/bin/activate
pip install requests
```

Or run the setup script:
```bash
./scripts/setup.sh
```

### "Configuration file not found"

**Problem**: `config.json` file doesn't exist.

**Solution**:
```bash
cp config.template.json config.json
# Edit config.json with your credentials
```

### "Authentication failed (401)"

**Problem**: Invalid or expired access token.

**Solutions**:
1. Verify your API key in the Coveo Admin Console
2. Generate a new API key if expired
3. Check the `access_token` field in `config.json`

### "Access forbidden (403)"

**Problem**: API key lacks push privileges.

**Solutions**:
1. Go to Coveo Admin Console → **Administration** → **API Keys**
2. Edit your API key to include **Push** privileges
3. Ensure the key has access to your specific source

### "Resource not found (404)"

**Problem**: Incorrect organization ID or source ID.

**Solutions**:
1. Verify `organization_id` in Coveo Admin Console → **Settings** → **Organization**
2. Verify `source_id` in **Content** → **Sources** → click your source
3. Check for typos in `config.json`

### "Payload too large (413)"

**Problem**: File exceeds 256 MB limit.

**Solutions**:
1. Split your payload into smaller files (<256 MB each)
2. Remove unnecessary fields from your items
3. Use multiple smaller update operations instead of one large load

### "Rate limit exceeded (429)"

**Problem**: Too many requests sent to the API.

**Solutions**:
1. Wait for the time specified in the error message
2. Reduce the frequency of your requests
3. Check API limits for your organization type

## API Limits Reference

| Limit | Production | Non-Production |
|-------|------------|----------------|
| Stream API calls/day | 15,000 | 10,000 |
| Burst limit (5 min) | 250 | 150 |
| Max file size | 256 MB | 256 MB |
| Max item size | 3 MB | 3 MB |

## Virtual Environment Issues

### "Command not found: ./coveo-loader"

**Solutions**:
1. Make the script executable: `chmod +x coveo-loader`
2. Use Python directly: `python src/loader.py --help`
3. Re-run setup: `./scripts/setup.sh`

### "Python command not found"

**Problem**: Python not installed or not in PATH.

**Solutions**:
1. Install Python 3.7+ from [python.org](https://python.org)
2. On macOS with Homebrew: `brew install python3`
3. Verify installation: `python3 --version`

## Payload Issues

### "Invalid JSON in payload file"

**Problem**: Malformed JSON in your payload file.

**Solutions**:
1. Validate JSON using an online JSON validator
2. Check for missing commas, quotes, or brackets
3. Ensure UTF-8 encoding for files with special characters

### "No items in payload"

**Problem**: Empty or incorrectly structured payload.

**Solutions**:
1. Ensure payload has `addOrUpdate` array with items
2. Check the [payload format guide](payload-format.md)
3. Verify `documentId` and `objecttype` fields are present

### "DocumentId format error"

**Problem**: Invalid `documentId` format.

**Solutions**:
1. Use proper URI format: `product://unique-id`
2. Ensure IDs are unique within the payload
3. Avoid special characters that aren't URI-encoded

## Network and Connectivity

### "Connection timeout"

**Problem**: Network connectivity issues.

**Solutions**:
1. Check your internet connection
2. Verify firewall isn't blocking HTTPS requests
3. Try again later if Coveo services are experiencing issues

### "SSL Certificate errors"

**Problem**: SSL/TLS certificate validation failing.

**Solutions**:
1. Update your Python requests library: `pip install --upgrade requests`
2. Update certificates: `pip install --upgrade certifi`
3. Check your system date/time is correct

## Performance Issues

### "Upload taking too long"

**Solutions**:
1. Reduce payload size by splitting into smaller files
2. Remove unnecessary fields from items
3. Use update operations instead of load operations
4. Check your internet connection speed

### "High memory usage"

**Solutions**:
1. Process smaller batches of data
2. Use streaming for very large files
3. Close and restart the script between large operations

## Getting More Help

If you're still experiencing issues:

1. **Check logs** in Coveo Admin Console → **Content** → **Logs** → **Log Browser**
2. **Review API documentation**: [Coveo Stream API Docs](https://docs.coveo.com/en/p4eb0129/)
3. **Community support**: [Coveo Community Forum](https://community.coveo.com/)
4. **Contact support**: If you have a Coveo subscription with support

## Debug Mode

To get more detailed error information, edit the script and add debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed HTTP requests and responses for troubleshooting.