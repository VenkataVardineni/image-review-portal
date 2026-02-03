# Image Flagging Guide

## Which Images Will Be Flagged?

Images are automatically flagged as **"flagged"** if their predicted label contains any of these keywords:
- `inappropriate`
- `nsfw`
- `violence`

## Mock Classifier Behavior (for Testing)

When `MOCK_CLASSIFIER=true`, the system **analyzes the actual image content** using computer vision heuristics. The classifier examines:

- **Color distribution** (RGB values, brightness, contrast)
- **Skin-tone detection** (detects high percentage of skin-like colors)
- **Red/violence detection** (identifies blood-like or violent content)
- **Nature/landscape detection** (greens and blues for safe landscapes)
- **Image brightness and patterns**

Here's what gets flagged based on image analysis:

### ✅ Will be FLAGGED:

**Inappropriate/NSFW content:**
- Images with very dark content (< 30 brightness) with reddish tones
- Images with >40% skin-tone pixels that are dark and have unusual aspect ratios
- Images with low color variation and high skin-tone percentage
- **Note**: The classifier analyzes actual pixel colors, not filenames

**Violent content:**
- Images with >30% red-dominant pixels (blood-like colors)
- High red values with low green/blue ratios
- Example: Images with significant red/violent content

**Fallback to filename** (if image analysis fails):
- Filenames containing: `inappropriate`, `nsfw`, `explicit`, `adult`, `porn`, `weapon`, `gun`, `knife`, `violence`, `blood`

### ✅ Will be SAFE:

**Landscape/Nature:**
- Images with >40% green and blue pixels (nature scenes)
- High green/blue color distribution
- Example: Photos of nature, landscapes, outdoor scenes

**Portraits:**
- Square or portrait aspect ratios (0.7-1.3) with moderate brightness
- Well-lit images with balanced colors
- Example: Normal portrait photos, family pictures

**Bright/Safe Images:**
- Very bright images (>200 brightness) - well-lit, safe content
- Bright and colorful images with high color variation
- Example: Well-lit photos, colorful images

**Default:**
- Images that don't match flagged patterns → `safe_image` (safe)

## Testing Examples

The classifier now analyzes **actual image content**, so you can test with real images:

**To test flagging:**
- Upload images with dark, reddish tones → **FLAGGED** (inappropriate)
- Upload images with high red content (blood-like) → **FLAGGED** (violence)
- Upload images with high skin-tone percentage in dark/unusual formats → **FLAGGED** (inappropriate)

**To test safe images:**
- Upload bright, colorful images → **SAFE**
- Upload nature/landscape photos (greens, blues) → **SAFE** (landscape)
- Upload normal portraits → **SAFE** (portrait)
- Upload well-lit photos → **SAFE**

**Note**: The classifier analyzes pixel colors and patterns, so actual image content matters more than filenames. If image analysis fails, it falls back to filename checking.

## Real Classifier API

When using a real classifier API (with `MOCK_CLASSIFIER=false`), the flagging depends on:
1. The label returned by the classifier API
2. Whether that label contains any of the flagged keywords: `inappropriate`, `nsfw`, `violence`

You can configure additional flagged classes via the `FLAGGED_CLASSES` environment variable:
```bash
FLAGGED_CLASSES="inappropriate,nsfw,violence,explicit,adult"
```

