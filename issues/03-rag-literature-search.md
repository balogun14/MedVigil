## What to build

A RAG (Retrieval-Augmented Generation) agent that takes the extracted entities from a report and searches FDA labels and PubMed abstracts. The UI will have a "Search Literature" button that triggers this agent and displays whether the reaction is Known, Unknown, or Unlabeled.

## Acceptance criteria

- [ ] API endpoint to trigger RAG search based on a saved report
- [ ] Agent fetches context from configured medical literature sources
- [ ] Agent returns a classification (Known/Unknown) and a short summary
- [ ] UI displays the literature findings attached to the report view

## Blocked by

- Blocked by #1
