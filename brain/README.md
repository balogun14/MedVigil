# MedVigil Brain - Clinical Tagger

This module contains the deep learning "brain" of MedVigil. It is responsible for Named Entity Recognition (NER) to extract Drugs and Adverse Drug Reactions (ADRs) from clinical text.

##  Getting Started

### 1. Install Dependencies
Ensure you have Python 3.9+ and run:
```bash
pip install -r requirements.txt
```

### 2. Prepare the Data
We use the **ADE-Corpus-V2** dataset from Hugging Face. This script downloads and pre-processes it for training.
```bash
python scripts/prepare_data.py
```

### 3. Train the Model
This will fine-tune **BioBERT** on the processed ADE data. 
*Note: This step requires a GPU for reasonable training times.*
```bash
python scripts/train_ner.py
```
The model will be saved to `models/medvigil-ner-v1`.

### 4. Run Inference
Once trained, you can test the model on clinical notes:
```bash
python scripts/inference.py
```

##  Model Architecture
- **Base Model:** `dmis-lab/biobert-v1.1` (Transformer-based)
- **Task:** Token Classification (NER)
- **Labels:** 
  - `B-DRUG / I-DRUG`: Suspect medication
  - `B-EFFECT / I-EFFECT`: Adverse reaction
  - `O`: Outside (non-medical text)

##  Privacy & Compliance
The `MedVigilBrain` class in `inference.py` includes a `_deidentify` method. As per our PRD, this layer ensures that PHI (Protected Health Information) is stripped before full clinical analysis.
