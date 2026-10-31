
import pandas as pd
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data and output directories
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def get_student_view(student_id):

    # Load data using absolute paths
    students = pd.read_csv(DATA_DIR / "students.csv")

    registrations = pd.read_csv(DATA_DIR / "registrations.csv")

    timetable = pd.read_csv(OUTPUT_DIR / "exam_timetable.csv")

    rooms = pd.read_csv(OUTPUT_DIR / "hybrid_room_allocation.csv")

    # Find student
    student = students[
        students["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:
        return {
            "success": False,
            "error": "Student ID not found."
        }

    # Get registered subjects
    registered = registrations[
        registrations["student_id"].astype(str) == str(student_id)
    ]

    # Connect registrations with timetable
    exams = registered.merge(
        timetable,
        on="subject_id",
        how="left"
    )

    # Get student's room and seat
    student_rooms = rooms[
        rooms["student_id"].astype(str) == str(student_id)
    ]

    room_columns = [
        "subject_id",
        "slot_id",
        "room_id",
        "seat_number"
    ]

    available_room_columns = [
        col for col in room_columns
        if col in student_rooms.columns
    ]

    if len(available_room_columns) == len(room_columns):

        exams = exams.merge(
            student_rooms[room_columns],
            on=["subject_id", "slot_id"],
            how="left"
        )

    else:
        if "room_id" not in exams.columns:
            exams["room_id"] = None

        if "seat_number" not in exams.columns:
            exams["seat_number"] = None

    # Student information
    student_info = student.iloc[0].to_dict()

    student_info = {
        key: None if pd.isna(value) else value
        for key, value in student_info.items()
    }

    # Select exam information
    exam_columns = [
        "exam_id",
        "subject_id",
        "exam_date",
        "slot_name",
        "start_time",
        "end_time",
        "duration_minutes",
        "room_id",
        "seat_number"
    ]

    existing_exam_columns = [
        col for col in exam_columns
        if col in exams.columns
    ]

    exams = exams[existing_exam_columns]

    # Sort timetable
    sort_columns = [
        col for col in ["exam_date", "start_time"]
        if col in exams.columns
    ]

    if sort_columns:
        exams = exams.sort_values(sort_columns)

    # Convert NaN to None
    exams = exams.astype(object).where(
        pd.notna(exams),
        None
    )

    exam_records = exams.to_dict(orient="records")

    return {
        "success": True,
        "student": student_info,
        "exams": exam_records
    }


if __name__ == "__main__":

    result = get_student_view("CSE6A001")

    print(result)
