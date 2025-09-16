<!-- -------------------------------------------------------
This records the decision to use MySQL as the external DB when deploying the AQI predictor as a web application.
  - SQLite is sufficient for local dev, but not for shared, concurrent, or deployed environments.
------------------------------------------------------- -->

# Decision: Use MySQL as external database for deployed web app
**Status:** Accepted (2025-09-12)

---

## Context
- The walking skeleton uses SQLite for local development:
  - Zero configuration, single-file DB, sufficient for demo  
- If a deployed web app is used we need: 
  - Multi-user concurrency, external persistence (not tied to one file on disk) and easy integration with cloud hosting (Docker, AWS RDS, etc.) 
  - Team wants the system to be accessible via a shared web dashboard

---

## Options Considered
1. SQLite only  
   + Simple, no setup  
   – Not safe for multi-user writes  
   – File based DB not practical for deployment

3. MySQL
   + Widely supported in hosting environments 
   + Easy to run in Docker (`mysql` image)
   + Compatible with SQLAlchemy engine in existing code
   – Slight differences in SQL syntax vs SQLite (this is handled in app/features.py)

---

## Decision
- Use MySQL 8 as the external database engine when deploying the AQI web app  
- Retain SQLite for local dev and quick demos  
- Detect engine flavor dynamically in `app/db.py` to keep portability

---

## Consequences
+ Enables multi-user, concurrent access  
+ Smooth path to cloud deployment (e.g., AWS RDS, Azure, GCP)  
+ Still allows use of SQLite locally
– Requires Docker container or hosted MySQL for testing
– Schema must stay consistent across both engines
– Feature code must avoid SQLite/MySQL specifics where possible

---

## Revisit When
- If data grows beyond what MySQL can handle cheaply.  
- If ORM (SQLAlchemy) support changes or project needs advanced DB features not in MySQL.
