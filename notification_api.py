
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"


def generate_tomorrow_duty_notifications():

    tomorrow = date.today() + timedelta(days=1)

    timetable_file = OUTPUT_DIR / "exam_timetable.csv"
    duties_file = OUTPUT_DIR / "hybrid_invigilator_duties.csv"

    if not timetable_file.exists() or not duties_file.exists():
        return []

    timetable = pd.read_csv(timetable_file)
    duties = pd.read_csv(duties_file)

    combined = duties.merge(
        timetable[
            ["subject_id", "slot_id", "exam_date",
             "start_time", "end_time"]
        ],
        on=["subject_id", "slot_id"],
        how="left"
    )

    combined["exam_date"] = pd.to_datetime(
        combined["exam_date"], errors="coerce"
    ).dt.date

    tomorrow_duties = combined[
        combined["exam_date"] == tomorrow
    ]

    notifications = []

    for _, duty in tomorrow_duties.iterrows():

        notifications.append({
            "type": "invigilator",
            "title": "Examination Duty Tomorrow!",
            "message": (
                f"You have examination duty tomorrow. "
                f"Subject: {duty['subject_id']}, "
                f"Room: {duty['room_id']}, "
                f"Time: {duty['start_time']} - {duty['end_time']}."
            ),
            "faculty_id": str(duty["faculty_id"]),
            "subject_id": str(duty["subject_id"]),
            "room_id": str(duty["room_id"]),
            "slot_id": str(duty["slot_id"]),
            "exam_date": str(duty["exam_date"])
        })

    return notifications
