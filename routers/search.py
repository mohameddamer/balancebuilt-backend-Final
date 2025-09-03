from fastapi import APIRouter, Depends
from database import get_db
import crud
router = APIRouter(prefix="/search", tags=["search"])
@router.get("/")
def search(q: str, db = Depends(get_db)):
    return crud.global_search(db, q)
