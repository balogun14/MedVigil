import os
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm

def prepare_ade_dataset():
    print("Loading ADE-Corpus-V2 from Hugging Face...")
    # Using the drug-ade relation subset as it contains the most granular data
    dataset = load_dataset("ade_corpus_v2", "Ade_corpus_v2_drug_ade_relation")
    
    data = dataset['train']
    processed_records = []
    
    print(f"Processing {len(data)} records...")
    for record in tqdm(data):
        # The dataset provides: sentence, drug, effect, and their spans
        # We want to create a clean CSV for training
        processed_records.append({
            'sentence': record['text'],
            'drug': record['drug'],
            'drug_start': record['indexes']['drug']['start-char'][0],
            'drug_end': record['indexes']['drug']['end-char'][0],
            'effect': record['adverse_effect'],
            'effect_start': record['indexes']['adverse_effect']['start-char'][0],
            'effect_end': record['indexes']['adverse_effect']['end-char'][0]
        })
        
    df = pd.DataFrame(processed_records)
    
    # Save to data folder
    output_path = os.path.join("brain", "data", "ade_processed.csv")
    df.to_csv(output_path, index=False)
    print(f"Successfully saved processed data to {output_path}")

if __name__ == "__main__":
    prepare_ade_dataset()
