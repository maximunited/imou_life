# Branding Assets for Imou Life Integration

This document outlines the branding asset requirements for the Imou Life custom integration to achieve Bronze tier compliance in Home Assistant's Quality Scale.

## Bronze Tier Requirement: Brands

**Rule**: [Has branding assets available for the integration](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/brands/)

As of Home Assistant 2026.3.0, custom components can include brand icons directly in the integration folder rather than submitting to the centralized brands repository.

## Required Assets

### Icon Files (Required)

Place these files in `custom_components/imou_life/`:

1. **`icon.png`** (256×256 pixels)
   - Standard resolution icon
   - 1:1 aspect ratio (square)
   - PNG format with transparency
   - Optimized/compressed for web

2. **`icon@2x.png`** (512×512 pixels)
   - High-DPI (Retina) version
   - 1:1 aspect ratio (square)
   - PNG format with transparency
   - Optimized/compressed for web

### Logo Files (Optional)

For enhanced branding, you can also include:

3. **`logo.png`** (shortest side: 128-256 pixels)
   - Landscape proportions
   - PNG format with transparency
   - Maintains Imou brand design

4. **`logo@2x.png`** (shortest side: 256-512 pixels)
   - High-DPI version of logo
   - PNG format with transparency

### Dark Mode Variants (Optional)

For dark theme support:
- `dark_icon.png` and `dark_icon@2x.png`
- `dark_logo.png` and `dark_logo@2x.png`

## Technical Specifications

- **Format**: PNG only
- **Interlacing**: Preferred
- **Transparency**: Preferred
- **Compression**: Must be properly optimized for web use
- **Trim**: Minimize empty space around the image
- **Icons**: Must be 1:1 aspect ratio (square)
- **Logos**: Landscape proportions respecting brand design

## Imou Logo Resources

Official Imou branding assets can be obtained from:

1. **[Brandfetch - Imou Global](https://brandfetch.com/imou.com?view=library&library=default&collection=logos)**
   - Official brand assets including logos, colors, fonts
   - Comprehensive style guide
   - High-quality SVG and PNG formats

2. **[BrandLogos.net](https://brandlogos.net/imou-logo-106782.html)**
   - Vector formats (EPS, SVG)
   - High-quality transparent PNG
   - Includes logomark, icons, and logotype

3. **[Icon-icons.com](https://icon-icons.com/icon/imou-logo/248026)**
   - SVG, PNG, ICO, ICNS formats
   - Free download

4. **[SeekLogo](https://seeklogo.com/vector-logo/449578/imou)**
   - PNG (2000×476px)
   - Vector (EPS) format

## Important Constraints

⚠️ **Do NOT use Home Assistant branded images**. This might confuse users into thinking the integration is an official/internal integration.

✅ **Use official Imou branding** to maintain brand recognition and consistency.

## Implementation Steps

1. **Download** the official Imou logo from one of the resources above
2. **Create** square icon versions (256×256 and 512×512)
   - Crop/resize to 1:1 aspect ratio
   - Ensure transparency around the logo
   - Center the logo within the square frame
3. **Optimize** the images using tools like:
   - [TinyPNG](https://tinypng.com/) for compression
   - [ImageOptim](https://imageoptim.com/) for optimization
4. **Save** as `icon.png` and `icon@2x.png`
5. **Place** in `custom_components/imou_life/` directory
6. **Test** by adding the integration in HA and checking the integration page

## Verification

After adding the icons, verify Bronze tier compliance by checking:

- [ ] `icon.png` exists and is 256×256 pixels
- [ ] `icon@2x.png` exists and is 512×512 pixels
- [ ] Both files are PNG format with transparency
- [ ] Images are properly compressed (icon.png < 50KB, icon@2x.png < 100KB)
- [ ] Icons display correctly in Home Assistant UI
- [ ] Icons do not use Home Assistant branding

## References

- [HA Integration Quality Scale: Brands Rule](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/brands/)
- [HA Brands Repository](https://github.com/home-assistant/brands)
- [Creating Integration Brand Guide](https://developers.home-assistant.io/docs/creating_integration_brand/)
- [Imou Global Brand Assets](https://brandfetch.com/imou.com)
