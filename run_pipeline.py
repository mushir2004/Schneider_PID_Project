import os
import time
import json
from src.knowledge_base import ISASymbolDB
from src.vision_agent import VisionAgent

# CONFIG
INPUT_TILES_FOLDER = "processed_tiles" # Root folder
OUTPUT_FILE = "final_output.json"

def main():
    # 1. Initialize DB
    try:
        db = ISASymbolDB()
        print(f" Brain loaded with {db.count_symbols()} symbols.")
    except:
        db = None

    # 2. Initialize Agent
    try:
        agent = VisionAgent(db_instance=db)
    except Exception as e:
        print(f" Error: {e}")
        return

    # 3. Get Images
    if not os.path.exists(INPUT_TILES_FOLDER):
        print(f" Error: Folder '{INPUT_TILES_FOLDER}' not found.")
        return

    tile_files = [f for f in os.listdir(INPUT_TILES_FOLDER) if f.endswith(".png") and "tile" in f]
    tile_files.sort()

    print(f" Starting Extraction on {len(tile_files)} tiles...")
    
    # Load existing data if we crashed before
    all_results = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            try:
                all_results = json.load(f)
                print(f"   (Resuming... already have {len(all_results)} tiles saved)")
            except:
                pass

    # 4. Run Loop
    for i, filename in enumerate(tile_files):
        # Skip if already processed
        if any(r['tile'] == filename for r in all_results):
            continue

        full_path = os.path.join(INPUT_TILES_FOLDER, filename)
        print(f"\n[{i+1}/{len(tile_files)}] Processing {filename}...")
        
        # SCAN
        results = agent.scan_tile(full_path)
        
        # SAVE RESULTS MEMORY
        tile_data = {
            "tile": filename,
            "symbols": results
        }
        all_results.append(tile_data)

        # WRITE TO FILE IMMEDIATELY (So we don't lose data)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_results, f, indent=4)

        # REPORT
        if results:
            print(f" Found {len(results)} symbols!")
            for res in results:
                print(f"   -> {res['final_label']} ({res['confidence']})")
        else:
            print("   No symbols found.")

        # SLEEP (Crucial for Free Tier)
        print(" Cooling down (20s)...")
        time.sleep(20) 

if __name__ == "__main__":
    main()