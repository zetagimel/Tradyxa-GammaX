
from PIL import Image
import os
import sys

def optimize_image(image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Error: {image_path} not found.")
            return

        img = Image.open(image_path)
        print(f"Original Size: {img.size}")
        print(f"Original File Size: {os.path.getsize(image_path) / 1024:.2f} KB")

        # Resize if too large (Standard OG is 1200x630)
        # Maintaining aspect ratio if possible, or just center crop/resize.
        # For simplicity, we will resize to fit within 1200x1200, but ideally 1200x630
        
        # WhatsApp prefers < 300KB.
        # Standard recommend: 1200x630
        
        target_size = (1200, 630)
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # If it's transparent PNG, convert to RGB for JPEG optimization if needed, 
        # but user has .png extension in meta tag. 
        # PNG compression is lossless usually, might not get enough size reduction.
        # Let's try to save as PNG optimized first.
        
        output_path = image_path
        
        # Save with optimization
        img.save(output_path, "PNG", optimize=True)
        
        new_size = os.path.getsize(output_path)
        print(f"Optimized PNG Size: {new_size / 1024:.2f} KB")
        
        if new_size > 300 * 1024:
            print("PNG still too big. Converting to JPEG logic might be needed but file extension is PNG.")
            # If we change to JPG, we break the link in index.html unless we update it.
            # Let's stick to PNG and try to resize smaller if needed?
            # Or perhaps just reducing colors (quantize).
            
            img = img.quantize(colors=256) # Reduce to 256 colors (8-bit)
            img.save(output_path, "PNG", optimize=True)
            new_size_q = os.path.getsize(output_path)
            print(f"Quantized PNG Size: {new_size_q / 1024:.2f} KB")
            
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    optimize_image(r"c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\client\public\og-image.png")
