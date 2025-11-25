# Image Hosting Options

This project supports multiple free image hosting solutions for production use.

## Option 1: JSDelivr CDN (Recommended) ⭐

**Current setup** - Uses GitHub repo as source with JSDelivr CDN delivery.

**URL Format:**

```
https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/assets/image.jpg
```

**Advantages:**

- ✅ 100% Free forever
- ✅ Global CDN (fast worldwide)
- ✅ Production-ready (99.9% uptime)
- ✅ No CORS issues
- ✅ Easy setup (already configured)
- ✅ Version controlled images

**Setup:**

```json
{
  "image_base_url": "https://cdn.jsdelivr.net/gh/YOUR-USERNAME/YOUR-REPO@main/assets"
}
```

## Option 2: GitHub Pages

Host images directly on GitHub Pages for more control.

**URL Format:**

```
https://USERNAME.github.io/REPO/image.jpg
```

**Setup:**

1. Enable GitHub Pages in repo settings
2. Use the included GitHub Action (`.github/workflows/deploy-images.yml`)
3. Update config:

```json
{
  "image_base_url": "https://YOUR-USERNAME.github.io/YOUR-REPO"
}
```

## Option 3: Other Free CDNs

### Cloudflare R2 (Free tier)

- 10GB storage free
- Good for larger catalogs

### Firebase Hosting

- 1GB storage + 10GB bandwidth free
- Easy deployment

## Updating Image URLs

After changing the `image_base_url` in config.json, run:

```bash
source coveo-env/bin/activate
python scripts/update-image-urls.py
```

## Production Recommendations

For **demo/documentation** projects: **Use JSDelivr** (current setup)
For **enterprise production**: Consider **Cloudflare R2** or **AWS S3 + CloudFront**
For **startups**: **JSDelivr** is perfectly fine for production!

## Testing Image URLs

Test any image URL by opening it directly in your browser:

```
https://cdn.jsdelivr.net/gh/rtherien/commerce-docs-demo-environment@main/assets/red-soccer-shoes.png
```
