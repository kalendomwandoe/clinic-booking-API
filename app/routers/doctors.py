from datetime import datetime, timedelta, date as date_type
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Doctor, Appointment
from app.booking_service import SLOT_MINUTES

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_id}")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.get("/{doctor_id}/availability")
def doctor_availability(doctor_id: int, target_date: date_type, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    booked_times = {
        appt.start_time.time()
        for appt in db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "booked",
        )
        if appt.start_time.date() == target_date
    }

    slots = []
    current = datetime.combine(target_date, doctor.working_hours_start)
    end_of_day = datetime.combine(target_date, doctor.working_hours_end)

    while current + timedelta(minutes=SLOT_MINUTES) <= end_of_day:
        if current.time() not in booked_times:
            slots.append(current.time())
        current += timedelta(minutes=SLOT_MINUTES)

    return {"doctor_id": doctor_id, "date": target_date, "available_slots": slots}