from fastapi import FastAPI
from app.routers import appointments, doctors, patients

app = FastAPI(title="Clinic Booking API")

app.include_router(appointments.router)
app.include_router(doctors.router)
app.include_router(patients.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}