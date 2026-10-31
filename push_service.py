
import json
from pathlib import Path
from pywebpush import webpush, WebPushException

BASE_DIR = Path(__file__).resolve().parent.parent

PRIVATE_KEY = BASE_DIR / "private_key.pem"
SUBSCRIPTIONS_FILE = BASE_DIR / "push_subscriptions.json"

VAPID_CLAIMS = {
    "sub": "mailto:admin@example.com"
}


def send_push_notification(subscription, title, message):
    payload = {
        "title": title,
        "message": message
    }

    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(payload),
            vapid_private_key=str(PRIVATE_KEY),
            vapid_claims=VAPID_CLAIMS
        )
        return True

    except WebPushException as error:
        print("Push notification error:", error)
        return False


def save_subscription(faculty_id, subscription):
    if SUBSCRIPTIONS_FILE.exists():
        with open(SUBSCRIPTIONS_FILE, "r") as file:
            subscriptions = json.load(file)
    else:
        subscriptions = {}

    subscriptions.setdefault(faculty_id, [])

    endpoint = subscription.get("endpoint")
    subscriptions[faculty_id] = [
        item for item in subscriptions[faculty_id]
        if item.get("endpoint") != endpoint
    ]

    subscriptions[faculty_id].append(subscription)

    with open(SUBSCRIPTIONS_FILE, "w") as file:
        json.dump(subscriptions, file, indent=4)

    return True


def notify_faculty(faculty_id, title, message):
    if not SUBSCRIPTIONS_FILE.exists():
        return 0

    with open(SUBSCRIPTIONS_FILE, "r") as file:
        subscriptions = json.load(file)

    faculty_subscriptions = subscriptions.get(faculty_id, [])
    sent_count = 0

    for subscription in faculty_subscriptions:
        if send_push_notification(subscription, title, message):
            sent_count += 1

    return sent_count
