## What to build

A trend detection system. When a new report is saved, the backend queries the vector/relational database for similar recent reports in the same pharmacy. If a threshold is met (e.g., >3 identical drug-reaction pairs in 30 days), trigger an alert.

## Acceptance criteria

- [ ] Backend query to aggregate similar reactions by drug within a timeframe
- [ ] Logic to evaluate if the cluster meets the alert threshold
- [ ] API includes an 'alerts' field when fetching a report
- [ ] UI displays a warning banner if the report is part of a local cluster

## Blocked by

- Blocked by #1
