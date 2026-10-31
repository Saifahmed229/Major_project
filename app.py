
from flask import Flask, jsonify, send_from_directory, request
from pathlib import Path

from scheduler_api import generate_hybrid_schedule
from room_api import generate_room_allocation
from invigilator_api import generate_invigilator_allocation
from timetable_api import generate_timetable
from faculty_api import get_faculty_view
from notification_api import generate_tomorrow_duty_notifications
from student_api import get_student_view
from data_validator import validate_data
from notification_api import generate_tomorrow_duty_notifications

from push_service import save_subscription


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_KEY_FILE = BASE_DIR / "vapid_public.txt"


@app.route("/dashboard")
def dashboard():
    return send_from_directory("../frontend", "index.html")


@app.route("/")
def home():
    return jsonify({
        "message": "Smart Exam Branch Automation API",
        "status": "Backend is running"
    })


@app.route("/api/test")
def test():
    return jsonify({
        "success": True,
        "message": "Flask backend connected successfully"
    })


@app.route("/api/generate-schedule")
def generate_schedule():
    try:
        valid, messages = validate_data()

        if not valid:
            return jsonify({
                "success": False,
                "error": "Input data validation failed.",
                "validation_errors": messages
            }), 400

        return jsonify(generate_hybrid_schedule())

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/allocate-rooms")
def allocate_rooms():
    try:
        return jsonify(generate_room_allocation())
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/allocate-invigilators")
def allocate_invigilators():
    try:
        return jsonify(generate_invigilator_allocation())
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/faculty/<faculty_id>")
def faculty_view(faculty_id):
    try:
        result = get_faculty_view(faculty_id)

        if not result["success"]:
            return jsonify(result), 404

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/timetable")
def timetable():
    try:
        timetable_data = generate_timetable()

        return jsonify({
            "success": True,
            "timetable": timetable_data.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/notifications")
def notifications():
    try:
        notification_data = generate_tomorrow_duty_notifications()

        return jsonify({
            "success": True,
            "notifications": notification_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/student/<student_id>")
def student_view(student_id):
    try:
        result = get_student_view(student_id)

        if not result["success"]:
            return jsonify(result), 404

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================================
# FACULTY PUSH NOTIFICATION APIs
# =====================================================

@app.route("/api/push/public-key", methods=["GET"])
def get_push_public_key():
    try:
        if not PUBLIC_KEY_FILE.exists():
            return jsonify({
                "success": False,
                "error": "VAPID public key file not found."
            }), 500

        public_key = PUBLIC_KEY_FILE.read_text().strip()

        return jsonify({
            "success": True,
            "publicKey": public_key
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/push/subscribe", methods=["POST"])
def subscribe_faculty():
    try:
        data = request.get_json(silent=True) or {}

        faculty_id = data.get("faculty_id")
        subscription = data.get("subscription")

        if not isinstance(faculty_id, str) or not faculty_id.strip():
            return jsonify({
                "success": False,
                "error": "Valid Faculty ID is required."
            }), 400

        if not isinstance(subscription, dict):
            return jsonify({
                "success": False,
                "error": "Valid push subscription is required."
            }), 400

        if not subscription.get("endpoint") or not subscription.get("keys"):
            return jsonify({
                "success": False,
                "error": "Incomplete push subscription."
            }), 400

        save_subscription(faculty_id.strip(), subscription)

        return jsonify({
            "success": True,
            "message": "Faculty subscription saved successfully."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/sw.js")
def service_worker():
    return send_from_directory(
        "../frontend",
        "sw.js",
        mimetype="application/javascript"
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
