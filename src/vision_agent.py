import os
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM

class VisionAgent:
    def __init__(self, db_instance=None):
        print("\n📥 Initializing Local AI (Microsoft Florence-2-Large)...")
        print("   (Note: First run will download ~1.5GB. Please wait...)\n")
        
        # 1. GPU Setup
        # We know this works because your check_gpu.py passed!
        self.device = "cuda"
        self.torch_dtype = torch.float16 
        
        print(f"🚀 GPU ACTIVE: {torch.cuda.get_device_name(0)}")

        # 2. Load Model
        # We use the 'Large' model because your 8GB GPU can handle it easily.
        model_id = "microsoft/Florence-2-large" 
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True,
                torch_dtype=self.torch_dtype,
                attn_implementation="eager"
            ).to(self.device)
            
            self.processor = AutoProcessor.from_pretrained(
                model_id, 
                trust_remote_code=True
            )
            print("✅ Local AI Model Loaded Successfully.\n")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise e

        self.db = db_instance

    def scan_tile(self, image_path):
        """
        Uses Local GPU AI to find objects.
        """
        print(f"👁️  Scanning: {os.path.basename(image_path)}...")
        
        try:
            image = Image.open(image_path).convert("RGB")
        except:
            return []

        # 3. Prompt for Object Detection
        # <OD> is the special command for Florence-2 to find EVERYTHING
        prompt = "<OD>"

        # 4. Inference (GPU Accelerated)
        inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)

        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=1,
            use_cache=False
        )

        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        
        # 5. Parse Results
        parsed_answer = self.processor.post_process_generation(
            generated_text, 
            task=prompt, 
            image_size=(image.width, image.height)
        )
        
        detections = parsed_answer.get('<OD>', {})
        bboxes = detections.get('bboxes', [])
        labels = detections.get('labels', [])

        # 6. Format
        formatted_results = []
        for bbox, label in zip(bboxes, labels):
            formatted_results.append({
                "label": label, 
                "box_2d": bbox # [x1, y1, x2, y2]
            })

        # 7. Verify with Brain
        return self._refine_detections(image, formatted_results)

    def _refine_detections(self, original_image, detections):
        refined_results = []
        
        for item in detections:
            label = item['label']
            box = item['box_2d']
            x1, y1, x2, y2 = box
            
            # Filter tiny noise (anything smaller than 15x15 pixels)
            if (x2 - x1) < 15 or (y2 - y1) < 15:
                continue

            try:
                symbol_crop = original_image.crop((x1, y1, x2, y2))
                temp_crop_path = "temp_crop.png"
                symbol_crop.save(temp_crop_path)
            except:
                continue

            final_label = label
            confidence = "Low (AI Guess)"
            
            # Ask the Vector DB (The Brain)
            if self.db:
                match_result = self.db.search_symbol(temp_crop_path)
                
                if match_result:
                    dist = match_result['confidence_score']
                    match_name = match_result['match']
                    
                    # Logic: If visual match is strong (< 65), trust the DB.
                    if dist < 65.0: 
                        final_label = match_name
                        confidence = f"High (DB Verified: {dist:.2f})"
                    # Logic: If AI says "valve" and DB says "gate_valve", trust the DB even if match is weak
                    elif "valve" in label or "pump" in label:
                         final_label = match_name
                         confidence = f"Medium (DB Refined: {dist:.2f})"

            refined_results.append({
                "final_label": final_label,
                "original_ai_label": label,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })

        return refined_results