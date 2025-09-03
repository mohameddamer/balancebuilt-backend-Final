BalanceBuilt ERP - backend

Run locally:
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. copy .env.example to .env and configure DATABASE_URL
5. uvicorn app:app --reload --port 10000
6. (optional) python seed_data.py
