# OLMS Web App – Complete MVP Project

Operational Logistics Management System web application prototype.

## Main modules
- Dashboard
- Stock On Hand
- PO Import Preview
- PO Import from Excel
- Invoice Import from Excel
- Offshore Selection
- PO Variance Report
- Loadout Summary
- Master Data
- Administration / Audit Log

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run olms_app/app.py
```

The app uses SQLite for the MVP. The database is created automatically on first run.

## Production recommendation
For enterprise deployment, migrate SQLite to PostgreSQL and replace Streamlit authentication placeholders with SSO or role-based login.
Deployment refresh