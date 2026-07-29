from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Appointment, Doctor

SLOT_MINUTES = 30


def validate_slot(db: Session, doctor: Doctor, start_time: datetime, exclude_appointment_id: int | None = None):
    if start_time < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Cannot book a slot in the past")

    end_time = start_time + timedelta(minutes=SLOT_MINUTES)


    if start_time.time() < doctor.working_hours_start or end_time.time() > doctor.working_hours_end:
        raise HTTPException(
            status_code=400,
            detail=f"Slot must fall within working hours ({doctor.working_hours_start} - {doctor.working_hours_end})"
        )

    conflict_query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.start_time == start_time,
        Appointment.status == "booked",
    )
    if exclude_appointment_id is not None:
        conflict_query = conflict_query.filter(Appointment.id != exclude_appointment_id)

    if conflict_query.first():
        raise HTTPException(status_code=409, detail="This slot is already taken")

    return end_time