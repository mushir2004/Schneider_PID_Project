import os
from pdf2image import convert_from_path
from PIL import Image
import math

# ================= CONFIGURATION =================
# TODO: PASTE YOUR POPPLER BIN PATH BELOW IF ON WINDOWS
# Example: r"C:\Program Files\poppler-24.07.0\Library\bin"
POPPLER_PATH = r"D:\Release-24.08.0-0\poppler-24.08.0\Library\bin"

INPUT_PDF = "sample_pid.pdf" # Put your P&ID PDF file in the same folder
OUTPUT_FOLDER = "processed_tiles"
DPI = 300  # High resolution is needed for small symbols
TILE_SIZE = 1024 # The size of the chunk we send to AI (1024x1024 pixels)
OVERLAP = 100 # Overlap to ensure symbols on the edge aren't cut off
# =================================================

def setup_folders():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created folder: {OUTPUT_FOLDER}")

def convert_pdf_to_images(pdf_path):
    print(f"Converting PDF: {pdf_path}...")
    try:
        # If POPPLER_PATH is None, it assumes poppler is in system PATH
        # FIND THIS LINE IN convert_pdf_to_images FUNCTION:
# images = convert_from_path(pdf_path, dpi=DPI, poppler_path=POPPLER_PATH)

# CHANGE IT TO THIS (Targeting exactly Page 12 which is a full diagram):
        # Change page 12 to 21
        images = convert_from_path(pdf_path, dpi=DPI, poppler_path=POPPLER_PATH, first_page=21, last_page=21)
        print(f"Successfully converted PDF into {len(images)} page(s).")
        return images
    except Exception as e:
        print(f"Error converting PDF. Did you install Poppler? Error: {e}")
        return []

def tile_image(image, page_num):
    img_width, img_height = image.size
    print(f"Processing Page {page_num} - Size: {img_width}x{img_height}")
    
    # Calculate how many tiles we need
    x_tiles = math.ceil(img_width / (TILE_SIZE - OVERLAP))
    y_tiles = math.ceil(img_height / (TILE_SIZE - OVERLAP))
    
    tile_count = 0
    
    for y in range(y_tiles):
        for x in range(x_tiles):
            # Calculate coordinates
            x1 = x * (TILE_SIZE - OVERLAP)
            y1 = y * (TILE_SIZE - OVERLAP)
            x2 = min(x1 + TILE_SIZE, img_width)
            y2 = min(y1 + TILE_SIZE, img_height)
            
            # Adjust x1/y1 if we hit the edge to keep tile size constant (optional, keeping simple here)
            
            # Crop
            tile = image.crop((x1, y1, x2, y2))
            
            # Save
            tile_filename = f"{OUTPUT_FOLDER}/page_{page_num}_tile_{x}_{y}.png"
            tile.save(tile_filename)
            tile_count += 1
            
            # Store metadata (we will need this later to stitch coordinates back)
            # For now, just printing
            # print(f"Saved {tile_filename} (Coords: {x1},{y1})")

    print(f"Total tiles generated for Page {page_num}: {tile_count}")

def main():
    setup_folders()
    
    # 1. Check if file exists
    if not os.path.exists(INPUT_PDF):
        print(f"ERROR: File '{INPUT_PDF}' not found. Please add a sample PDF to the folder.")
        return

    # 2. Convert PDF to Image
    images = convert_pdf_to_images(INPUT_PDF)
    
    # 3. Tile each page
    for i, img in enumerate(images):
        # Save the full processed page for reference
        img.save(f"{OUTPUT_FOLDER}/full_page_{i+1}.png")
        tile_image(img, page_num=i+1)

    print("\nProcessing Complete! Check the 'processed_tiles' folder.")

if __name__ == "__main__":
    main()