from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/appointments")
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == patient_id,
            Appointment.status == "booked",
            Appointment.start_time >= datetime.now(timezone.utc),
        )
        .order_by(Appointment.start_time.asc())
        .all()
    )