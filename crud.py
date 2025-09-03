from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
import pandas as pd, io, csv, datetime
import models

def row_to_dict(obj):
    if obj is None:
        return None
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

# Generic CRUD
def list_all(db: Session, model, skip=0, limit=100):
    rows = db.scalars(select(model).offset(skip).limit(limit)).all()
    return [row_to_dict(r) for r in rows]

def get_one(db: Session, model, id):
    return row_to_dict(db.get(model, id))

def create_one(db: Session, model, data: dict):
    obj = model(**data)
    db.add(obj); db.commit(); db.refresh(obj)
    return row_to_dict(obj)

def update_one(db: Session, model, id, updates: dict):
    obj = db.get(model, id)
    if not obj: return None
    for k,v in updates.items():
        if hasattr(obj, k): setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return row_to_dict(obj)

def delete_one(db: Session, model, id):
    obj = db.get(model, id)
    if not obj: return False
    db.delete(obj); db.commit()
    return True

# Bulk upload helpers
def upload_csv(db: Session, model, file_content: str):
    reader = csv.DictReader(io.StringIO(file_content))
    objs = []
    for row in reader:
        clean = {k: (v if v != '' else None) for k,v in row.items()}
        obj = model(**clean)
        db.add(obj); objs.append(obj)
    db.commit()
    for o in objs: db.refresh(o)
    return [row_to_dict(o) for o in objs]

def bulk_upload(db: Session, model, file_bytes: bytes, filename: str):
    if filename.lower().endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))
    records = df.to_dict(orient='records')
    objs = []
    for rec in records:
        clean = {k: (None if (isinstance(v, float) and pd.isna(v)) else v) for k,v in rec.items()}
        obj = model(**clean)
        db.add(obj); objs.append(obj)
    db.commit()
    return {"inserted": len(objs)}

# Global search
def global_search(db: Session, query: str, limit: int = 50):
    if not query: return []
    q = f"%{query}%"
    results = []
    vendors = db.scalars(select(models.Vendor).where(models.Vendor.name.ilike(q)).limit(limit)).all()
    results += [{"table":"vendors","row":row_to_dict(v)} for v in vendors]
    customers = db.scalars(select(models.Customer).where(models.Customer.name.ilike(q)).limit(limit)).all()
    results += [{"table":"customers","row":row_to_dict(c)} for c in customers]
    products = db.scalars(select(models.Product).where(or_(models.Product.name.ilike(q), models.Product.sku.ilike(q))).limit(limit)).all()
    results += [{"table":"products","row":row_to_dict(p)} for p in products]
    gls = db.scalars(select(models.GLAccount).where(models.GLAccount.name.ilike(q)).limit(limit)).all()
    results += [{"table":"gl_accounts","row":row_to_dict(g)} for g in gls]
    return results

# ---------------- REPORTS & METRICS ---------------
def report_trial_balance(db: Session, period: str=None):
    jel = models.JournalEntryLine
    stmt = select(jel.account_code, func.coalesce(func.sum(jel.debit),0).label("debit"), func.coalesce(func.sum(jel.credit),0).label("credit")).group_by(jel.account_code)
    if period:
        # journal_entries.date is in JournalEntry; join
        stmt = stmt.join(models.JournalEntry, models.JournalEntry.id == jel.journal_id).where(models.JournalEntry.date.like(f"{period}-%"))
    rows = db.execute(stmt).all()
    return [{"account_code": r[0], "debit": float(r[1]), "credit": float(r[2])} for r in rows]

def report_pnl(db: Session, period: str=None):
    jel = models.JournalEntryLine
    stmt = select(jel.account_code, func.coalesce(func.sum(jel.debit - jel.credit),0).label("amount")).group_by(jel.account_code)
    if period:
        stmt = stmt.join(models.JournalEntry, models.JournalEntry.id == jel.journal_id).where(models.JournalEntry.date.like(f"{period}-%"))
    rows = db.execute(stmt).all()
    types = {g.code: g.type for g in db.scalars(select(models.GLAccount)).all()}
    revenue = 0.0; expense = 0.0
    for code, amt in rows:
        t = types.get(code)
        if t == "Revenue": revenue += float(amt or 0)
        elif t == "Expense": expense += float(amt or 0)
    return {"revenue": revenue, "expense": expense, "net_income": revenue - expense}

def report_net_sales(db: Session, period: str=None):
    # Net sales from sales_orders total_amount (could be net of returns)
    stmt = select(func.coalesce(func.sum(models.SalesOrder.total_amount),0))
    if period:
        stmt = stmt.where(models.SalesOrder.order_date.like(f"{period}-%"))
    val = float(db.execute(stmt).scalar() or 0)
    return {"net_sales": val}

def report_actual_vs_forecast(db: Session, metric: str="net_sales", period: str=None):
    # Actual from sales_orders or pnl; forecast from Forecast table
    actual = 0.0
    if metric == "net_sales":
        actual = report_net_sales(db, period)["net_sales"]
    elif metric == "net_profit":
        actual = report_pnl(db, period)["net_income"]
    # forecast
    stmt = select(models.Forecast.value).where(models.Forecast.metric == metric)
    if period:
        stmt = stmt.where(models.Forecast.period == period)
    forecast_vals = [r for r,_ in enumerate(db.execute(stmt).all())]  # placeholder; we'll sum below
    # proper sum
    forecast_rows = db.execute(select(func.coalesce(func.sum(models.Forecast.value),0)).where(models.Forecast.metric==metric) if not period else select(func.coalesce(func.sum(models.Forecast.value),0)).where(models.Forecast.metric==metric).where(models.Forecast.period==period)).all()
    forecast = float(forecast_rows[0][0] if forecast_rows else 0)
    return {"metric": metric, "actual": actual, "forecast": forecast, "variance": actual - forecast}

def report_ar_aging(db: Session):
    ars = db.scalars(select(models.AccountsReceivable)).all()
    today = datetime.date.today()
    buckets = {"0-30":0,"31-60":0,"61-90":0,"90+":0}
    for a in ars:
        if not a.due_date: continue
        days = (today - a.due_date).days
        amt = float(a.amount or 0)
        if days <=30: buckets["0-30"] += amt
        elif days <=60: buckets["31-60"] += amt
        elif days <=90: buckets["61-90"] += amt
        else: buckets["90+"] += amt
    return buckets

def report_inventory_value(db: Session):
    rows = db.execute(select(models.Product.id, models.Product.name, func.coalesce(func.sum(models.Inventory.quantity),0).label("qty"), models.Product.cost).join(models.Inventory, models.Inventory.product_id==models.Product.id).group_by(models.Product.id)).all()
    out = []
    for pid,name,qty,cost in rows:
        out.append({"product_id": pid, "product": name, "quantity": float(qty), "unit_cost": float(cost or 0), "value": float((cost or 0) * (qty or 0))})
    return out

def report_inventory_metrics(db: Session):
    # turnover = COGS / average inventory value (COGS approximated by journal entries to Expense GLs)
    gls = db.scalars(select(models.GLAccount)).all()
    expense_codes = [g.code for g in gls if g.type == "Expense"]
    jel = models.JournalEntryLine
    cogs_stmt = select(func.coalesce(func.sum(jel.debit - jel.credit),0)).where(jel.account_code.in_(expense_codes))
    cogs = float(db.execute(cogs_stmt).scalar() or 0)
    inv_val_rows = db.execute(select(func.coalesce(func.sum(models.Product.cost * models.Inventory.quantity),0))).all()
    inv_val = float(inv_val_rows[0][0] or 0) if inv_val_rows else 0
    turnover = (cogs / inv_val) if inv_val else None
    return {"cogs": cogs, "inventory_value": inv_val, "turnover": turnover}

# Additional reports: top customers/vendors, purchase/sales report
def report_top_customers_vendors(db: Session, top_n: int = 10):
    ar_agg = db.execute(select(models.AccountsReceivable.customer_id, func.sum(models.AccountsReceivable.amount)).group_by(models.AccountsReceivable.customer_id).order_by(func.sum(models.AccountsReceivable.amount).desc()).limit(top_n)).all()
    top_customers = []
    for cid, amt in ar_agg:
        c = db.get(models.Customer, cid)
        top_customers.append({"customer_id": cid, "customer_name": c.name if c else None, "amount": float(amt or 0)})
    ap_agg = db.execute(select(models.AccountsPayable.vendor_id, func.sum(models.AccountsPayable.amount)).group_by(models.AccountsPayable.vendor_id).order_by(func.sum(models.AccountsPayable.amount).desc()).limit(top_n)).all()
    top_vendors = []
    for vid, amt in ap_agg:
        v = db.get(models.Vendor, vid)
        top_vendors.append({"vendor_id": vid, "vendor_name": v.name if v else None, "amount": float(amt or 0)})
    return {"top_customers": top_customers, "top_vendors": top_vendors}

# Calendar events
def list_calendar_events(db: Session, start: str = None, end: str = None):
    q = select(models.CalendarEvent)
    if start:
        q = q.where(models.CalendarEvent.start >= start)
    if end:
        q = q.where(models.CalendarEvent.end <= end)
    rows = db.scalars(q).all()
    return [row_to_dict(r) for r in rows]

# Convenience wrappers for router compatibility
def get_vendors(db: Session, skip=0, limit=100): return db.scalars(select(models.Vendor).offset(skip).limit(limit)).all()
def create_vendor(db: Session, data): return create_one(db, models.Vendor, data)
# ... similar wrappers could be created as needed in routers
