from uuid import uuid4
from faker import Faker
from datetime import datetime, timedelta
from models.entity import AuthEventType


fake = Faker()


def user():
    user_sample = [
        {
            "email": fake.email(),
            "password": fake.password(),
        } for _ in range(5)
    ]
    return user_sample


def user_history(user_sample):
    user_history_sample = [
        {
            "user_uuid": user.uuid,
            "user_agent": "Linux",
            "event_type": AuthEventType("login"),
        } for _ in range(2) for user in user_sample
    ]
    return user_history_sample
