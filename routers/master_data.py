from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/customers")
def list_customers(db: Session = Depends(get_db)):
    return crud.get_customers(db)

@router.post("/customers")
def add_customer(payload: dict, db: Session = Depends(get_db)):
    return crud.create_customer(db, payload)

@router.get("/vendors")
def list_vendors(db: Session = Depends(get_db)):
    return crud.get_vendors(db)

@router.post("/vendors")
def add_vendor(payload: dict, db: Session = Depends(get_db)):
    return crud.create_vendor(db, payload)

@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@router.post("/products")
def add_product(payload: dict, db: Session = Depends(get_db)):
    return crud.create_product(db, payload)

@router.get("/warehouses")
def list_warehouses(db: Session = Depends(get_db)):
    return crud.get_warehouses(db)

@router.post("/warehouses")
def add_warehouse(payload: dict, db: Session = Depends(get_db)):
    return crud.create_warehouse(db, payload)
