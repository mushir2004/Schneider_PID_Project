import os
import json
from src.knowledge_base import ISASymbolDB
from src.vision_agent import VisionAgent

# CONFIG
INPUT_TILES_FOLDER = "processed_tiles" # Root folder
OUTPUT_FILE = "final_output.json"

def main():
    print("="*50)
    print("   SCHNEIDER ELECTRIC - LOCAL AGENTIC AI")
    print("="*50)

    # 1. Initialize DB
    try:
        db = ISASymbolDB()
        print(f"🧠 Brain loaded with {db.count_symbols()} symbols.")
    except:
        print("⚠️  Warning: DB not loaded.")
        db = None

    # 2. Initialize Agent (This triggers the download)
    try:
        agent = VisionAgent(db_instance=db)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 3. Get Images
    if not os.path.exists(INPUT_TILES_FOLDER):
        print(f"❌ Error: Folder '{INPUT_TILES_FOLDER}' not found.")
        return

    tile_files = [f for f in os.listdir(INPUT_TILES_FOLDER) if f.endswith(".png") and "tile" in f]
    tile_files.sort()

    print(f"🚀 Starting Extraction on {len(tile_files)} tiles...")
    
    all_results = []

    # 4. Run Loop (FAST MODE - No Sleep)
    for i, filename in enumerate(tile_files):
        full_path = os.path.join(INPUT_TILES_FOLDER, filename)
        
        # SCAN
        results = agent.scan_tile(full_path)
        
        # SAVE
        if results:
            print(f"   ✅ Found {len(results)} symbols in {filename}")
            for res in results:
                print(f"      -> {res['final_label']} ({res['confidence']})")
            
            tile_data = {
                "tile": filename,
                "symbols": results
            }
            all_results.append(tile_data)
        else:
            print(f"   (No symbols in {filename})")

        # Write to file instantly
        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_results, f, indent=4)

    print("\n PROCESSING COMPLETE!")
    print(f" Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()