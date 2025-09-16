<!-- -------------------------------------------------------
  This records the decision to use SQLite for initial storage
  - Captures context, options, decision, and consequences
Notes:
  • Template for future ADRs:
    - Status
    - Context
    - Options
    - Decision
    - Consequences
    - Revisit When
------------------------------------------------------- -->

# Decision: Use SQLite for storage

Status: Accepted (YYYY-MM-DD)
## Context: 
  - Single-user, local dev, small daily tables

## Decision: 
  - SQLite with date 

## Consequences: 
  - +Zero-ops
  - Not multi-user
  –Limited concurrency

## Revisit When: 
  - Data > 1e6 rows or multi-user
