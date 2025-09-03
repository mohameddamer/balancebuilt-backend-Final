import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
import models
from routers import (
    vendors, customers, products, warehouses,
    purchase_orders, purchase_order_lines, sales_orders, sales_order_lines,
    inventory, purchase_requisitions, supplier_contracts,
    gl_accounts, accounts_payable, accounts_receivable,
    budgets, fixed_assets, fx_rates, journal_entries, journal_lines,
    cost_centers, tax_ledger, cash_flow, reconciliation,
    forecasts, calendar_events,
    search, reports
)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="BalanceBuilt ERP API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# create tables
Base.metadata.create_all(bind=engine)

# include routers
app.include_router(vendors.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(purchase_orders.router)
app.include_router(purchase_order_lines.router)
app.include_router(sales_orders.router)
app.include_router(sales_order_lines.router)
app.include_router(inventory.router)
app.include_router(purchase_requisitions.router)
app.include_router(supplier_contracts.router)
app.include_router(gl_accounts.router)
app.include_router(accounts_payable.router)
app.include_router(accounts_receivable.router)
app.include_router(budgets.router)
app.include_router(fixed_assets.router)
app.include_router(fx_rates.router)
app.include_router(journal_entries.router)
app.include_router(journal_lines.router)
app.include_router(cost_centers.router)
app.include_router(tax_ledger.router)
app.include_router(cash_flow.router)
app.include_router(reconciliation.router)
app.include_router(forecasts.router)
app.include_router(calendar_events.router)
app.include_router(search.router)
app.include_router(reports.router)

@app.get("/health")
def health():
    return {"status":"ok"}

# generic upload mapping
crud_table_mapping = {
    "vendors": models.Vendor,
    "customers": models.Customer,
    "products": models.Product,
    "warehouses": models.Warehouse,
    "purchase_orders": models.PurchaseOrder,
    "purchase_order_lines": models.PurchaseOrderLine,
    "sales_orders": models.SalesOrder,
    "sales_order_lines": models.SalesOrderLine,
    "inventory": models.Inventory,
    "purchase_requisitions": models.PurchaseRequisition,
    "supplier_contracts": models.SupplierContract,
    "gl_accounts": models.GLAccount,
    "accounts_payable": models.AccountsPayable,
    "accounts_receivable": models.AccountsReceivable,
    "budgets": models.Budget,
    "fixed_assets": models.FixedAsset,
    "fx_rates": models.FXRate,
    "journal_entries": models.JournalEntry,
    "journal_lines": models.JournalEntryLine,
    "cost_centers": models.CostCenter,
    "tax_ledger": models.TaxLedger,
    "cash_flow": models.CashFlow,
    "reconciliation": models.Reconciliation,
    "forecasts": models.Forecast,
    "calendar_events": models.CalendarEvent
}

@app.post("/upload/{table_name}")
async def upload_table(table_name: str, file: UploadFile = File(...), db = Depends(get_db)):
    if table_name not in crud_table_mapping:
        raise HTTPException(status_code=400, detail="Unknown table")
    model = crud_table_mapping[table_name]
    content = await file.read()
    return __import__("crud").crud.bulk_upload(db, model, content, file.filename) if False else __import__("crud").bulk_upload(db, model, content, file.filename)
