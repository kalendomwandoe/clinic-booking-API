import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from app.database import Base, get_db

from datetime import time
from app.models import Doctor, Patient


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_doctor(db_session):
    doctor = Doctor(name="Dr. Wanjiru", working_hours_start=time(9, 0), working_hours_end=time(17, 0))
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture()
def sample_patient(db_session):
    patient = Patient(name="John Otieno", email="john@example.com")
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient