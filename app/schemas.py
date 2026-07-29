from datetime import datetime
from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    start_time: datetime

class CancelRequest(BaseModel):
    reason: str


class RescheduleRequest(BaseModel):
    new_start_time: datetime