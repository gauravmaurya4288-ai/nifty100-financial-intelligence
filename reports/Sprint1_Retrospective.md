# Sprint 1 Retrospective

## Project
Nifty100 Financial Intelligence

## Sprint Duration
Day 01 – Day 07

---

# Sprint Goal

Build a complete ETL pipeline capable of loading, validating, and storing Nifty100 financial datasets into SQLite. Ensure data quality through validation rules and prepare the project for financial analytics in Sprint 2.

---

# Objectives Achieved

- Project environment setup completed.
- Folder structure organized for ETL, analytics, database, tests, and reports.
- Raw financial datasets collected and validated.
- Excel loader and normalization pipeline implemented.
- Data Quality (DQ) validation engine developed.
- SQLite database schema designed and created.
- Successfully loaded financial datasets into SQLite.
- SQL verification queries executed to validate data.
- Database prepared for financial ratio calculations.

---

# Major Deliverables

- Project folder structure
- ETL pipeline
- Excel loader
- Data normalization module
- Data Quality validation engine
- SQLite database
- Database schema
- Data loading pipeline
- SQL verification scripts

---

# Technical Challenges

### Database Schema Mismatch

Several SQLite tables contained column mismatches during data loading.

Resolution:
- Updated schema definitions.
- Corrected table structures.
- Rebuilt database.

---

### Excel Header Variations

Multiple Excel files contained title rows before actual headers.

Resolution:
- Applied appropriate skiprows values.
- Standardized column names.
- Cleaned imported datasets.

---

### Import Path Errors

Python modules failed to import due to incorrect package paths.

Resolution:
- Added __init__.py files.
- Standardized package imports.
- Used project root for execution.

---

### Data Loading Errors

Several datasets initially failed to populate SQLite.

Resolution:
- Updated ETL logic.
- Corrected column mappings.
- Reloaded datasets successfully.

---

# Skills Applied

- Python
- Pandas
- SQLite
- SQL
- ETL Pipeline Development
- Data Cleaning
- Data Validation
- Database Design
- Git & GitHub

---

# Key Outcomes

- ETL pipeline successfully implemented.
- SQLite database created and populated.
- Financial datasets validated.
- Database integrity verified.
- Project ready for financial analytics.

---

# Lessons Learned

- Maintain consistent database schemas.
- Validate source data before loading.
- Standardize column names across datasets.
- Verify database contents after every ETL execution.
- Use automated validation to detect data quality issues early.

---

# Sprint Summary

Sprint 1 successfully established the foundation of the Nifty100 Financial Intelligence project by delivering a reliable ETL pipeline, validated financial datasets, and a structured SQLite database. The completed infrastructure provides a stable base for implementing financial ratio calculations, KPI engines, and advanced analytics in Sprint 2.

---

## Sprint Status

✅ Completed Successfully