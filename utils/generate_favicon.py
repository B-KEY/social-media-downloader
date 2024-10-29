from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    # Create directory if it doesn't exist
    favicon_dir = 'static/favicon'
    os.makedirs(favicon_dir, exist_ok=True)
    
    # Sizes for different favicon versions
    sizes = {
        'favicon.ico': (48, 48),
        'favicon-16x16.png': (16, 16),
        'favicon-32x32.png': (32, 32),
        'apple-touch-icon.png': (180, 180)
    }
    
    # Create base image (using largest size)
    size = 180
    background_color = '#121212'  # Dark background
    icon_color = '#ff0000'        # Red icon color
    
    # Create base image
    img = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple download arrow
    margin = size // 4
    arrow_width = size // 8
    
    # Draw arrow stem
    draw.rectangle(
        [(size//2 - arrow_width//2, margin), 
         (size//2 + arrow_width//2, size - margin)],
        fill=icon_color
    )
    
    # Draw arrow head
    points = [
        (size//4, size - margin - arrow_width),           # Left point
        (size//2, size - margin),                         # Bottom point
        (size*3//4, size - margin - arrow_width)          # Right point
    ]
    draw.polygon(points, fill=icon_color)
    
    # Save in different sizes
    for filename, dimensions in sizes.items():
        resized = img.resize(dimensions, Image.Resampling.LANCZOS)
        filepath = os.path.join(favicon_dir, filename)
        
        if filename.endswith('.ico'):
            resized.save(filepath, format='ICO')
        else:
            resized.save(filepath, format='PNG')

if __name__ == '__main__':
    create_favicon()
