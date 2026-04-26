## What to build

Implement the privacy middleware to redact Protected Health Information (PHI). When a note is submitted, the system must detect and mask names, phone numbers, etc., BEFORE saving to the DB. The UI should display the redacted version alongside the original to verify it worked.

## Acceptance criteria

- [ ] Privacy middleware intercepts text before processing/saving
- [ ] Names, dates, and phone numbers are replaced with tags (e.g., [PHONE])
- [ ] The database only stores the redacted text and extracted medical entities
- [ ] UI shows a toggle to view the redacted text

## Blocked by

- Blocked by #1
