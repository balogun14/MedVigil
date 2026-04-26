# PRD: MedVigil - AI Pharmacovigilance Assistant

## Problem Statement
Pharmacists are the first line of defense in detecting Adverse Drug Reactions (ADRs), but the current process is manual, fragmented, and slow. Reporting a single reaction often requires filling out complex forms (like MedWatch or CIOMS) which takes 15-30 minutes. Furthermore, pharmacists lack local tools to detect if a specific drug brand is causing a cluster of reactions in their own pharmacy, and they don't have immediate access to fine-tuned clinical literature to validate if a reaction is a known or emerging signal.

## Solution
MedVigil is an AI assistant that streamlines the entire ADR lifecycle for pharmacists. It uses a **Hybrid Ingestion** system where pharmacists can either fill out a form or simply paste a clinical note. An **NLP-driven Clinical Tagger** automatically maps their narrative to global standards (MedDRA and RxNorm). A **Multi-Agent Intelligence Engine** then analyzes the report by:
1. Performing **RAG-based literature searches** (FDA/EMA/PubMed).
2. Calculating **Causality Scores** (Naranjo Algorithm).
3. Detecting **Local Clusters** (anomalies in the pharmacy's history).
Finally, it generates an anonymized, regulatory-ready **Clinical Investigative Brief** for the pharmacist to review and submit to regulatory bodies.

## User Stories

### 1. ADR Reporting & Ingestion
1. As a pharmacist, I want to paste a clinical narrative into the assistant, so that I don't have to manually type out every symptom and drug name.
2. As a pharmacist, I want the system to automatically strip patient names and phone numbers, so that I remain compliant with data privacy laws (GDPR/NDPR).
3. As a pharmacist, I want to use a structured form for critical data (drug name, dose, onset), so that the report meets regulatory quality standards.
4. As a pharmacist, I want the AI to map my clinical terms (e.g., "itching") to official MedDRA terms (e.g., "Pruritus"), so that the data is standardized for regulators.

### 2. Analysis & Signal Detection
5. As a pharmacist, I want the AI to search the latest medical literature for me, so that I can see if this reaction has been reported globally before.
6. As a pharmacist, I want an automated Naranjo causality score, so that I have a scientific basis for deciding if the drug actually caused the reaction.
7. As a pharmacist, I want to be alerted if I've seen 3 or more similar reactions for the same drug brand this month, so that I can detect a potential batch contamination or safety signal.

### 3. Review & Reporting
8. As a pharmacist, I want a one-page "Clinical Investigative Brief" generated for every report, so that I can easily share findings with hospital management or doctors.
9. As a regulator, I want to receive reports in a structured JSON/XML format mapped to MedDRA/RxNorm, so that I can easily aggregate them at the population level.

## Implementation Decisions

### 1. Major Modules
- **Frontend (MedVigil UI):** A premium React/Next.js dashboard with a focus on "Speed of Entry" (Hybrid Form/Narrative).
- **Clinical Tagger (NLP Module):** A Python-based service using a medical-grade entity extractor (e.g., fine-tuned BioBERT or MedSpacy) to map text to MedDRA/RxNorm IDs.
- **Signal Multi-Agent (Orchestrator):** A LangChain/LangGraph orchestrator that coordinates:
    - **Search Agent:** RAG tool for clinical literature.
    - **Logic Agent:** Python-based causality algorithm (Naranjo).
    - **History Agent:** Vector search or SQL query for local cluster detection.
- **Privacy Layer:** A middleware that uses regex and NER (Named Entity Recognition) to redact PHI before it reaches any LLM.

### 2. Technical Clarifications
- **Anonymized-by-Design:** The database will explicitly *not* have columns for Patient Name or Phone Number. It will use a "Local Patient ID" provided by the pharmacist.
- **Taxonomy Source:** For the MVP, we will use the NIH RxNorm API and a curated subset of MedDRA for mapping.
- **RAG Source:** We will prioritize FDA Drug Labels (DailyMed) and PubMed abstracts.

### 3. Architectural Decisions
- **Next.js + FastAPI:** Next.js for the premium UI and FastAPI for the high-performance NLP/Python agents.
- **Vector Database (Pinecone/Chroma):** To store pharmacy-level report history for the "Local Trend" detection.
- **PostgreSQL:** For structured report storage and regulatory form generation.
