import os
from src.knowledge_base import ISASymbolDB
from tqdm import tqdm # Progress bar

# CONFIGURATION
REFERENCE_IMAGE_FOLDER = "data/isa_reference_images"

def main():
    # 1. Initialize the Brain
    db = ISASymbolDB()
    
    # 2. Check Input Folder
    if not os.path.exists(REFERENCE_IMAGE_FOLDER):
        os.makedirs(REFERENCE_IMAGE_FOLDER)
        print(f"⚠️ Folder '{REFERENCE_IMAGE_FOLDER}' was empty. Created it.")
        print("👉 ACTION: Please paste clean PNG images of ISA symbols there and run this again.")
        return

    # 3. Get all images
    files = [f for f in os.listdir(REFERENCE_IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("⚠️ No images found. Please add symbol images (e.g., 'gate_valve.png').")
        return

    print(f"Found {len(files)} images. Starting ingestion...")

    # 4. Ingest Loop
    for filename in tqdm(files):
        path = os.path.join(REFERENCE_IMAGE_FOLDER, filename)
        
        # Clean filename to get the label (e.g. "gate_valve.png" -> "gate_valve")
        symbol_name = os.path.splitext(filename)[0].lower().replace(" ", "_")
        
        # Logic to guess category based on name (Optional but good for metadata)
        category = "misc"
        if "valve" in symbol_name: category = "valve"
        elif "pump" in symbol_name: category = "pump"
        elif "tank" in symbol_name or "vessel" in symbol_name: category = "vessel"
        elif "indicator" in symbol_name or "transmitter" in symbol_name: category = "instrument"
        
        # Add to DB
        db.add_symbol(path, symbol_name, category)

    print(f"\n🎉 Ingestion Complete. Total Knowledge Base Size: {db.count_symbols()} symbols.")

if __name__ == "__main__":
    main()