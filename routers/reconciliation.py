from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import crud, models
from database import get_db

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])

@router.get("/")
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_all(db, models.Reconciliation, skip, limit)

@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_one(db, models.Reconciliation, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return item

@router.post("/")
def create_item(payload: dict, db: Session = Depends(get_db)):
    return crud.create_one(db, models.Reconciliation, payload)

@router.put("/{item_id}")
def update_item(item_id: int, updates: dict, db: Session = Depends(get_db)):
    row = crud.update_one(db, models.Reconciliation, item_id, updates)
    if not row:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return row

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_one(db, models.Reconciliation, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return {"ok": True}

@router.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()
    return crud.bulk_upload(db, models.Reconciliation, content, file.filename)
