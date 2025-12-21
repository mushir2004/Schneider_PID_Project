import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

class ISASymbolDB:
    """
    A Professional Wrapper around ChromaDB to store and retrieve ISA-5.1 Symbols.
    """
    
    def __init__(self, db_path="./chroma_db"):
        print("Initializing ISA Symbol Knowledge Base...")
        
        # 1. Initialize Vector Database (Persistent)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 2. Initialize the Vision Model (CLIP)
        # We use clip-ViT-B-32. It is lightweight but powerful for industry symbols.
        print("Loading Vision Model (CLIP)...")
        self.model = SentenceTransformer('clip-ViT-B-32')
        
        # 3. Get or Create the Collection
        self.collection = self.client.get_or_create_collection(
            name="isa_standard_symbols",
            metadata={"description": "ISA-5.1 Standard P&ID Symbols"}
        )
        print("Knowledge Base Ready.")

    def _generate_embedding(self, image_path):
        """
        Converts an image file into a vector embedding.
        """
        try:
            img = Image.open(image_path)
            # Encode image to vector
            embedding = self.model.encode(img)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding for {image_path}: {e}")
            return None

    def add_symbol(self, image_path, symbol_name, category="general"):
        """
        Adds a single symbol to the database (Self-Learning Capability).
        """
        embedding = self._generate_embedding(image_path)
        
        if embedding:
            # We use the filename as a unique ID, or you can generate a UUID
            symbol_id = f"{symbol_name}_{category}"
            
            self.collection.upsert(
                ids=[symbol_id],
                embeddings=[embedding],
                metadatas=[{
                    "label": symbol_name,
                    "category": category,
                    "standard": "ISA-5.1",
                    "source_image": image_path
                }],
                documents=[symbol_name] # Optional: helps with debug
            )
            print(f"✅ Successfully learned: {symbol_name} ({category})")
            return True
        return False

    def search_symbol(self, query_image_path, threshold=0.8):
        """
        Given a crop from a P&ID, find the matching ISA symbol.
        """
        embedding = self._generate_embedding(query_image_path)
        if not embedding:
            return None

        # Query the DB
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=1 # We just want the top match
        )
        
        # Check distance (Chroma returns distance, lower is better for L2, 
        # but for Cosine similarity logic we usually interpret closeness)
        if results['ids'] and len(results['ids'][0]) > 0:
            best_match_label = results['metadatas'][0][0]['label']
            distance = results['distances'][0][0]
            
            # Note: In Chroma default (L2), 0.0 is exact match. 
            # You will need to calibrate 'threshold' based on testing.
            return {
                "match": best_match_label,
                "confidence_score": distance, 
                "metadata": results['metadatas'][0][0]
            }
            
        return None

    def count_symbols(self):
        return self.collection.count()