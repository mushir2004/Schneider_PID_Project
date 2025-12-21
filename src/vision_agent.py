import os
import json
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

class VisionAgent:
    def __init__(self, db_instance=None):
        """
        initializes the Vision Agent.
        :param db_instance: An instance of ISASymbolDB (The Brain)
        """
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
            
        genai.configure(api_key=api_key)
        # We use the newest Flash model from your list
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.db = db_instance

    def scan_tile(self, image_path):
        """
        Step 1: Ask Gemini to find bounding boxes.
        """
        print(f"  Scanning tile: {os.path.basename(image_path)}...")
        img = Image.open(image_path)
        
        prompt = """
        Analyze this P&ID engineering diagram.
        Locate all equipment and instrument symbols.
        
        Return a STRICT JSON list. Format:
        [
          {"label": "valve", "box_2d": [ymin, xmin, ymax, xmax]},
          {"label": "pump", "box_2d": [ymin, xmin, ymax, xmax]}
        ]
        
        Important:
        - Coordinates must be normalized (0-1000).
        - If you see a valve, just label it "valve".
        - If you see a pump, just label it "pump".
        - If you see a circle with letters, label it "instrument".
        """
        
        try:
            response = self.model.generate_content([prompt, img])
            text = response.text.strip()
            # Clean markdown
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "")
            
            raw_detections = json.loads(text)
            return self._refine_detections(img, raw_detections)
            
        except Exception as e:
            print(f"⚠️  AI Detection Error: {e}")
            return []

    def _refine_detections(self, original_image, detections):
        """
        Step 2: The Agentic Workflow.
        """
        refined_results = []
        width, height = original_image.size

        if not detections:
            return []

        for item in detections:
            # SAFETY CHECK 1: Ensure item is a dictionary
            if not isinstance(item, dict):
                continue

            label = item.get('label', 'unknown')
            box = item.get('box_2d', [])

            # SAFETY CHECK 2: Ensure box has exactly 4 coordinates
            if not isinstance(box, list) or len(box) != 4:
                print(f"   ⚠️ Skipping invalid box format: {box}")
                continue

            # Convert normalized 0-1000 coords to actual pixels
            try:
                ymin, xmin, ymax, xmax = box
                left = (xmin / 1000) * width
                top = (ymin / 1000) * height
                right = (xmax / 1000) * width
                bottom = (ymax / 1000) * height
                
                # SAFETY CHECK 3: Avoid negative or zero-size crops
                if right <= left or bottom <= top:
                    continue

                # Crop the symbol
                symbol_crop = original_image.crop((left, top, right, bottom))
                
                # Save crop temporarily
                temp_crop_path = "temp_crop.png"
                symbol_crop.save(temp_crop_path)

                final_label = label
                confidence = "Low (AI Guess)"
                
                # === THE AGENTIC DECISION ===
                if self.db:
                    match_result = self.db.search_symbol(temp_crop_path)
                    
                    if match_result:
                        # In ChromaDB, larger distance = worse match.
                        # < 10.0 is usually a 'okay' match for unnormalized vectors
                        dist = match_result['confidence_score']
                        match_name = match_result['match']
                        
                        # Adjust this threshold based on your data
                        if dist < 60.0: 
                            final_label = match_name
                            confidence = f"High (Verified by DB: {dist:.2f})"
                        else:
                            confidence = f"Medium (DB match weak: {dist:.2f})"
                
                refined_results.append({
                    "final_label": final_label,
                    "original_ai_label": label,
                    "confidence": confidence,
                    "bbox": [left, top, right, bottom]
                })
            except Exception as e:
                print(f"   ⚠️ Error processing box: {e}")
                continue

        return refined_results