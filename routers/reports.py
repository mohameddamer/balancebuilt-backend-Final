from fastapi import APIRouter, Depends
from database import get_db
import crud
router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/trial_balance")
def trial_balance(period: str = None, db = Depends(get_db)):
    return crud.report_trial_balance(db, period)

@router.get("/pnl")
def pnl(period: str = None, db = Depends(get_db)):
    return crud.report_pnl(db, period)

@router.get("/net_sales")
def net_sales(period: str = None, db = Depends(get_db)):
    return crud.report_net_sales(db, period)

@router.get("/actual_vs_forecast")
def actual_vs_forecast(metric: str = "net_sales", period: str = None, db = Depends(get_db)):
    return crud.report_actual_vs_forecast(db, metric, period)

@router.get("/ar_aging")
def ar_aging(db = Depends(get_db)):
    return crud.report_ar_aging(db)

@router.get("/inventory_value")
def inventory_value(db = Depends(get_db)):
    return crud.report_inventory_value(db)

@router.get("/inventory_metrics")
def inventory_metrics(db = Depends(get_db)):
    return crud.report_inventory_metrics(db)

@router.get("/top_customers_vendors")
def top_customers_vendors(db = Depends(get_db)):
    return crud.report_top_customers_vendors(db)
