import enum
from sqlalchemy import Column, Integer, String, Time, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    working_hours_start = Column(Time, nullable=False)
    working_hours_end = Column(Time, nullable=False)

    appointments = relationship("Appointment", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.booked, nullable=False)
    cancellation_reason = Column(String, nullable=True)

    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

