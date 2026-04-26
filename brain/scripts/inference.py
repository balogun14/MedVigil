import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import os

# Configuration
MODEL_PATH = "brain/models/medvigil-ner-v1"
# Fallback to BioBERT if local model doesn't exist yet
BASE_MODEL = "dmis-lab/biobert-v1.1"

class MedVigilBrain:
    def __init__(self, model_path=MODEL_PATH):
        if os.path.exists(model_path):
            print(f"Loading custom MedVigil model from {model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        else:
            print(f"Warning: Custom model not found at {model_path}. Using base BioBERT (inference will be limited).")
            self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
            self.model = AutoModelForTokenClassification.from_pretrained(BASE_MODEL)
            
        self.ner_pipeline = pipeline(
            "ner", 
            model=self.model, 
            tokenizer=self.tokenizer, 
            aggregation_strategy="simple"
        )

    def analyze_note(self, text):
        """
        Analyzes a clinical note to extract drugs and ADRs.
        Includes a basic de-identification step.
        """
        # 1. Basic De-identification (Placeholder for regex/NER based PHI stripping)
        # In a production environment, this would be a deep module.
        clean_text = self._deidentify(text)
        
        # 2. Extract Entities
        entities = self.ner_pipeline(clean_text)
        
        results = {
            "original_text": text,
            "clean_text": clean_text,
            "entities": []
        }
        
        for ent in entities:
            results["entities"].append({
                "entity": ent["word"],
                "label": ent["entity_group"],
                "score": float(ent["score"]),
                "start": ent["start"],
                "end": ent["end"]
            })
            
        return results

    def _deidentify(self, text):
        # Basic example: Strip anything that looks like a phone number, date, or name-like patterns
        # This will be expanded in the privacy-guard module.
        import re
        # Simple phone number mask
        text = re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE]', text)
        # Simple date mask (YYYY-MM-DD)
        text = re.sub(r'\d{4}-\d{2}-\d{2}', '[DATE]', text)
        # Simple name mask (Assuming "Patient First Last")
        text = re.sub(r'(?<=Patient )[A-Z][a-z]+ [A-Z][a-z]+', '[NAME]', text)
        return text

if __name__ == "__main__":
    brain = MedVigilBrain()
    sample_note = "Patient was prescribed Metformin 500mg but developed severe lactic acidosis and nausea."
    analysis = brain.analyze_note(sample_note)
    
    print("\n--- Clinical Analysis Results ---")
    for ent in analysis["entities"]:
        print(f"[{ent['label']}] {ent['entity']} (Confidence: {ent['score']:.2f})")
