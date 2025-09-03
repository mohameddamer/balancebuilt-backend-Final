from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sales_orders")
def create_sales_order(payload: dict, db: Session = Depends(get_db)):
    return crud.create_sales_order(db, payload)

@router.get("/sales_orders")
def list_sales_orders(db: Session = Depends(get_db)):
    return db.query(models.SalesOrder).order_by(models.SalesOrder.id).all()

@router.post("/purchase_orders")
def create_purchase_order(payload: dict, db: Session = Depends(get_db)):
    return crud.create_purchase_order(db, payload)

@router.get("/purchase_orders")
def list_purchase_orders(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).order_by(models.PurchaseOrder.id).all()

@router.post("/inventory")
def upsert_inventory(payload: dict, db: Session = Depends(get_db)):
    product_id = int(payload["product_id"])
    warehouse_id = int(payload["warehouse_id"])
    qty = float(payload.get("quantity", 0))
    item = db.query(models.Inventory).filter(
        models.Inventory.product_id==product_id,
        models.Inventory.warehouse_id==warehouse_id
    ).first()
    if item:
        item.quantity = item.quantity + qty
        item.last_updated = datetime.utcnow()
    else:
        item = models.Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=qty)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/inventory")
def list_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()
