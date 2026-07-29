from datetime import datetime, timedelta, timezone


def test_book_appointment_success(client, sample_doctor, sample_patient):
    start_time = datetime.now(timezone.utc) + timedelta(days=2)
    start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)

    response = client.post("/appointments", json={
        "doctor_id": sample_doctor.id,
        "patient_id": sample_patient.id,
        "start_time": start_time.isoformat(),
    })

    assert response.status_code == 200
    assert response.json()["status"] == "booked"


def future_slot(hours_ahead=48, hour=10):
    dt = datetime.now(timezone.utc) + timedelta(hours=hours_ahead)
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def test_double_booking_fails(client, sample_doctor, sample_patient):
    slot = future_slot()
    payload = {"doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat()}

    first = client.post("/appointments", json=payload)
    assert first.status_code == 200

    second = client.post("/appointments", json=payload)
    assert second.status_code == 409


def test_outside_working_hours_fails(client, sample_doctor, sample_patient):
    slot = future_slot(hour=20)  # doctor works 9-17
    response = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    })
    assert response.status_code == 400


def test_past_date_fails(client, sample_doctor, sample_patient):
    slot = datetime.now(timezone.utc) - timedelta(days=1)
    response = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    })
    assert response.status_code == 400


def test_within_one_hour_fails(client, sample_doctor, sample_patient):
    slot = datetime.now(timezone.utc) + timedelta(minutes=30)
    response = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    })
    assert response.status_code == 400


def test_cancel_then_rebook_same_slot(client, sample_doctor, sample_patient):
    slot = future_slot()
    payload = {"doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat()}
    created = client.post("/appointments", json=payload).json()

    cancel = client.patch(f"/appointments/{created['id']}/cancel", json={"reason": "test"})
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    rebook = client.post("/appointments", json=payload)
    assert rebook.status_code == 200


def test_cancel_twice_fails(client, sample_doctor, sample_patient):
    slot = future_slot()
    created = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    }).json()

    client.patch(f"/appointments/{created['id']}/cancel", json={"reason": "first"})
    second = client.patch(f"/appointments/{created['id']}/cancel", json={"reason": "again"})
    assert second.status_code == 400


def test_reschedule_frees_old_slot(client, sample_doctor, sample_patient):
    original = future_slot(hours_ahead=48)
    new_slot = future_slot(hours_ahead=72)

    created = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": original.isoformat(),
    }).json()

    resched = client.patch(f"/appointments/{created['id']}/reschedule", json={"new_start_time": new_slot.isoformat()})
    assert resched.status_code == 200

    rebook_original = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": original.isoformat(),
    })
    assert rebook_original.status_code == 200


def test_reschedule_cancelled_fails(client, sample_doctor, sample_patient):
    slot = future_slot()
    created = client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    }).json()
    client.patch(f"/appointments/{created['id']}/cancel", json={"reason": "no longer needed"})

    resched = client.patch(f"/appointments/{created['id']}/reschedule", json={
        "new_start_time": future_slot(hours_ahead=96).isoformat(),
    })
    assert resched.status_code == 400


def test_availability_excludes_booked_slot(client, sample_doctor, sample_patient):
    slot = future_slot()
    client.post("/appointments", json={
        "doctor_id": sample_doctor.id, "patient_id": sample_patient.id, "start_time": slot.isoformat(),
    })

    response = client.get(f"/doctors/{sample_doctor.id}/availability", params={"target_date": slot.date().isoformat()})
    assert response.status_code == 200
    booked_time = slot.time().isoformat()
    assert booked_time not in [s for s in response.json()["available_slots"]]