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
    print(data[0])
    for record in tqdm(data):
        # The dataset provides: sentence, drug, effect, and their spans
        try:
            drug_start = record['indexes']['drug']['start_char'][0]
            drug_end = record['indexes']['drug']['end_char'][0]
            effect_start = record['indexes']['effect']['start_char'][0]
            effect_end = record['indexes']['effect']['end_char'][0]
        except IndexError:
            continue

        processed_records.append({
            'sentence': record['text'],
            'drug': record['drug'],
            'drug_start': drug_start,
            'drug_end': drug_end,
            'effect': record['effect'],
            'effect_start': effect_start,
            'effect_end': effect_end
        })
        
    df = pd.DataFrame(processed_records)
    
    # Save to data folder
    output_path = os.path.join("brain", "data", "ade_processed.csv")
    df.to_csv(output_path, index=False)
    print(f"Successfully saved processed data to {output_path}")

if __name__ == "__main__":
    prepare_ade_dataset()
