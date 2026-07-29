from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Doctor
from app.schemas import AppointmentCreate, CancelRequest, RescheduleRequest
from app.booking_service import validate_slot

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("")
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if payload.start_time < datetime.now(timezone.utc) + timedelta(hours=1):
        raise HTTPException(status_code=400, detail="Bookings must be made at least 1 hour in advance")

    end_time = validate_slot(db, doctor, payload.start_time)

    appt = Appointment(
        doctor_id=payload.doctor_id,
        patient_id=payload.patient_id,
        start_time=payload.start_time,
        end_time=end_time,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, payload: CancelRequest, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")

    appt.status = "cancelled"
    appt.cancellation_reason = payload.reason
    db.commit()
    db.refresh(appt)
    return appt


@router.patch("/{appointment_id}/reschedule")
def reschedule_appointment(appointment_id: int, payload: RescheduleRequest, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot reschedule a cancelled appointment")

    doctor = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
    new_end_time = validate_slot(db, doctor, payload.new_start_time, exclude_appointment_id=appt.id)

    appt.start_time = payload.new_start_time
    appt.end_time = new_end_time
    db.commit()
    db.refresh(appt)
    return appt