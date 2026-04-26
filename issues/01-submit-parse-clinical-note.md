## What to build

End-to-end flow for pharmacists to submit a clinical note. The UI accepts text input, sends it to the FastAPI backend where the BioBERT NLP model extracts drugs and adverse effects, saves the structured data to the database, and returns it to the UI for display.

## Acceptance criteria

- [ ] UI provides a text area for narrative input
- [ ] FastAPI endpoint receives text and runs `inference.py`
- [ ] Extracted entities (Drugs, Reactions) are saved to the PostgreSQL database
- [ ] UI displays the extracted entities clearly below the text area

## Blocked by

None - can start immediately
