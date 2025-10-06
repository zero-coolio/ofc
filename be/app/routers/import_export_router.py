from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.database import get_session
from app.security import get_current_user
from app.models import User
from app.services import import_export_service as svc

router = APIRouter(prefix="/io", tags=["import-export"])

@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    content = (await file.read()).decode("utf-8", errors="ignore")
    try:
        created = svc.import_transactions_csv(session, user_id=user.id, csv_text=content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"imported": created}

@router.get("/export/csv")
def export_csv(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    csv_text = svc.export_transactions_csv(session, user_id=user.id)
    return StreamingResponse(iter([csv_text]), media_type="text/csv", headers={
        "Content-Disposition": 'attachment; filename="transactions.csv"'
    })
