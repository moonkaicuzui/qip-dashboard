#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate PNG icons for PWA from scratch using PIL
Since SVG conversion tools are not available, we create simplified PNG versions
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_background(width, height):
    """Create purple gradient background matching SVG design"""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)

    # Gradient colors from SVG: #667eea to #764ba2
    start_color = (102, 126, 234)  # #667eea
    end_color = (118, 75, 162)     # #764ba2

    for y in range(height):
        # Calculate interpolated color for this row
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return image

def add_rounded_corners(image, radius):
    """Add rounded corners to image"""
    # Create a mask for rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw rounded rectangle on mask
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)

    # Apply mask to image
    output = Image.new('RGBA', image.size, (0, 0, 0, 0))
    output.paste(image, (0, 0))
    output.putalpha(mask)

    return output

def create_icon(size, output_path):
    """Create a single PNG icon of specified size"""
    # Create gradient background
    image = create_gradient_background(size, size)

    # Convert to RGBA for transparency support
    image = image.convert('RGBA')

    # Add rounded corners (15.6% radius like SVG rx="80" for 512px)
    radius = int(size * 0.156)
    image = add_rounded_corners(image, radius)

    # Draw on the image
    draw = ImageDraw.Draw(image)

    # Try to load a bold font, fallback to default
    try:
        # Try Arial Black or similar bold font
        font_size = int(size * 0.234)  # 120/512 ratio from SVG
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(size * 0.234))
        except:
            # Fallback to default font
            font = ImageFont.load_default()

    # Draw "QIP" text
    text = "QIP"

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position text (y=200 for 512px = 0.39 ratio)
    x = (size - text_width) // 2
    y = int(size * 0.35) - text_height // 2

    # Draw text with white color
    draw.text((x, y), text, fill='white', font=font)

    # Draw coin stack icon (simplified version)
    coin_center_y = int(size * 0.625)  # 320/512 ratio
    coin_radius = int(size * 0.068)    # 35/512 ratio

    # Draw 3 coins (simplified - ellipses only)
    coins = [
        (size//2 - int(size*0.059), coin_center_y),      # Left coin
        (size//2, coin_center_y - int(size*0.029)),       # Center coin (higher)
        (size//2 + int(size*0.059), coin_center_y)        # Right coin
    ]

    for cx, cy in coins:
        # Gold color #FFD700
        draw.ellipse(
            [(cx - coin_radius, cy - coin_radius//3),
             (cx + coin_radius, cy + coin_radius//3)],
            fill='#FFD700',
            outline='#FFA500'
        )

    # Draw subtitle (simplified - smaller text)
    try:
        subtitle_font_size = int(size * 0.0625)  # 32/512 ratio
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", subtitle_font_size)
    except:
        subtitle_font = ImageFont.load_default()

    subtitle = "Incentive Dashboard"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox[2] - bbox[0]

    x = (size - subtitle_width) // 2
    y = int(size * 0.898)  # 460/512 ratio

    draw.text((x, y), subtitle, fill='white', font=subtitle_font)

    # Save image
    image.save(output_path, 'PNG')
    print(f"✅ Created {output_path} ({size}x{size})")

def main():
    """Generate all required PNG icons"""
    print("🎨 Generating PNG icons for PWA...")

    # Output directory
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)

    # Generate 192x192 icon (for manifest and general use)
    create_icon(192, os.path.join(docs_dir, "icon-192.png"))

    # Generate 512x512 icon (for manifest and high-res displays)
    create_icon(512, os.path.join(docs_dir, "icon-512.png"))

    print("✅ All PNG icons generated successfully!")

if __name__ == "__main__":
    main()
