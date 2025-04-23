import uuid
from faker import Faker
from datetime import datetime, timedelta
from services.auth.src.models.entity import AuthEventType
import random
fake = Faker()

user_sample = [
    {
        "uuid": str(uuid.uuid4()),
        "email": fake.email,
        "password": fake.password,
        "roles": "User",
        "created_at": datetime.now(),
        "modified_at": datetime.now()
    } for _ in range(10)
]

user_history_sample = [
    {
        "uuid": str(uuid.uuid4()),
        "user_uuid": user_sample[i],
        "user_agent": "Linux",
        "event_type": AuthEventType("LOGIN"),
        "occurred_at": datetime.now() - timedelta(hours=random.randint(1, 3)),
    } for _ in range(5) for i in range(10)
]
