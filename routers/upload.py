from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import csv, io
import models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/customers")
async def upload_customers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created = []
    for row in reader:
        c = models.Customer(name=row.get("name"), email=row.get("email"), phone=row.get("phone"))
        db.add(c); created.append(c)
    db.commit()
    return {"created": len(created)}

@router.post("/products")
async def upload_products(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created = 0
    for row in reader:
        p = models.Product(name=row.get("name"), category=row.get("category"), unit_price=float(row.get("unit_price",0)), unit_cost=float(row.get("unit_cost",0)))
        db.add(p); created += 1
    db.commit()
    return {"created": created}

@router.post("/inventory")
async def upload_inventory(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    processed = 0
    for row in reader:
        pid = int(row.get("product_id"))
        wid = int(row.get("warehouse_id"))
        qty = float(row.get("quantity",0))
        item = db.query(models.Inventory).filter(models.Inventory.product_id==pid, models.Inventory.warehouse_id==wid).first()
        if item:
            item.quantity += qty
            item.last_updated = datetime.utcnow()
        else:
            item = models.Inventory(product_id=pid, warehouse_id=wid, quantity=qty)
            db.add(item)
        processed += 1
    db.commit()
    return {"processed": processed}
