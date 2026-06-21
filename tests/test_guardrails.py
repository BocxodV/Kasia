import pytest
from app.skills.guardrails import validate_shift_data

def test_valid_shift():
    """
    Test case for a normal valid shift with 8 hours of work, 2 hours of driving, and status 'Work'.
    Should return an empty list of errors.
    """
    data = {
        "work_hours": 8.0,
        "driving_hours": 2.0,
        "status": "Work",
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors = validate_shift_data(data)
    assert errors == []

def test_hours_exceed_24():
    """
    Test case where the sum of work_hours and driving_hours is 25 (exceeds 24 hours).
    Should return an error message about exceeding 24 hours.
    """
    data = {
        "work_hours": 15.0,
        "driving_hours": 10.0,
        "status": "Work",
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors = validate_shift_data(data)
    assert len(errors) == 1
    assert "exceeds the 24-hour daily limit" in errors[0]

def test_l4_with_hours():
    """
    Test case where status is 'L4' (sick leave) but work_hours is specified (8.0).
    Should return an error message stating that no work/driving is allowed on sick leave.
    """
    data = {
        "work_hours": 8.0,
        "driving_hours": 0.0,
        "status": "L4",
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors = validate_shift_data(data)
    assert len(errors) == 1
    assert "work hours and driving hours must be empty or 0" in errors[0]

def test_urlop_with_hours():
    """
    Test case where status is 'Urlop' (vacation) but hours are specified.
    Should return an error message stating that no work/driving is allowed on vacation.
    """
    data = {
        "work_hours": 0.0,
        "driving_hours": 4.0,
        "status": "Urlop",
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors = validate_shift_data(data)
    assert len(errors) == 1
    assert "work hours and driving hours must be empty or 0" in errors[0]

def test_missing_status():
    """
    Test case where status is missing or not one of the allowed values ('Work', 'L4', 'Urlop').
    Should return a safety validation error.
    """
    # Case 1: Status is missing (None)
    data_missing = {
        "work_hours": 8.0,
        "driving_hours": 0.0,
        "status": None,
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors = validate_shift_data(data_missing)
    assert len(errors) == 1
    assert "Invalid or missing status" in errors[0]

    # Case 2: Status is invalid
    data_invalid = {
        "work_hours": 8.0,
        "driving_hours": 0.0,
        "status": "InvalidStatus",
        "date": "2026-06-20",
        "location": "Warsaw"
    }
    errors_invalid = validate_shift_data(data_invalid)
    assert len(errors_invalid) == 1
    assert "Status must be 'Work', 'L4', or 'Urlop'" in errors_invalid[0]
