import os
import pandas as pd
import numpy as np
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    TrainingArguments, 
    Trainer,
    DataCollatorForTokenClassification
)
from datasets import Dataset
import evaluate

# Configuration
MODEL_NAME = "dmis-lab/biobert-v1.1"
OUTPUT_DIR = "brain/models/medvigil-ner-v1"
DATA_PATH = "brain/data/ade_processed.csv"

# Label mapping: 0: O, 1: B-DRUG, 2: I-DRUG, 3: B-EFFECT, 4: I-EFFECT
ID2LABEL = {0: "O", 1: "B-DRUG", 2: "I-DRUG", 3: "B-EFFECT", 4: "I-EFFECT"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

def tokenize_and_align_labels(examples, tokenizer):
    tokenized_inputs = tokenizer(
        examples["sentence"], truncation=True, is_split_into_words=False, padding="max_length", max_length=128
    )
    
    labels = []
    for i, sentence in enumerate(examples["sentence"]):
        # Create a list of 'O' labels for each character
        char_labels = [0] * len(sentence)
        
        # Mark Drug spans
        d_start, d_end = int(examples["drug_start"][i]), int(examples["drug_end"][i])
        char_labels[d_start] = 1 # B-DRUG
        for j in range(d_start + 1, d_end):
            char_labels[j] = 2 # I-DRUG
            
        # Mark Effect spans
        e_start, e_end = int(examples["effect_start"][i]), int(examples["effect_end"][i])
        char_labels[e_start] = 3 # B-EFFECT
        for j in range(e_start + 1, e_end):
            char_labels[j] = 4 # I-EFFECT
            
        # Map char labels to token labels
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        token_labels = []
        for word_idx in word_ids:
            if word_idx is None:
                token_labels.append(-100) # Ignore index
            else:
                # Get the start/end char offset for this token
                span = tokenized_inputs.token_to_chars(i, word_idx)
                if span:
                    # Take the label of the first character in the token
                    token_labels.append(char_labels[span.start])
                else:
                    token_labels.append(0)
        labels.append(token_labels)
        
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

def train():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Run prepare_data.py first.")
        return

    print("Loading preprocessed data...")
    df = pd.read_csv(DATA_PATH)
    dataset = Dataset.from_pandas(df)
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    print("Tokenizing and aligning labels...")
    tokenized_dataset = dataset.map(
        lambda x: tokenize_and_align_labels(x, tokenizer), 
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Split data
    split = tokenized_dataset.train_test_split(test_size=0.1)
    train_data = split["train"]
    val_data = split["test"]
    
    print("Initializing BioBERT for Token Classification...")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(ID2LABEL),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )
    
    metric = evaluate.load("seqeval")
    
    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        
        true_predictions = [
            [ID2LABEL[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [ID2LABEL[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        
        results = metric.compute(predictions=true_predictions, references=true_labels)
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        load_best_model_at_end=True,
        push_to_hub=False,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=val_data,
        processing_class=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=compute_metrics,
    )
    
    print("Starting training...")
    trainer.train()
    
    print(f"Saving final model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)

if __name__ == "__main__":
    train()
