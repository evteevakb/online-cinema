from faker import Faker

from models.entity import AuthEventType, User

fake = Faker()


def user() -> list[dict]:
    user_sample = [
        {
            "email": fake.email(),
            "password": fake.password(),
        }
        for _ in range(5)
    ]
    return user_sample


def user_history(user_sample: User) -> list[dict]:
    user_history_sample = [
        {
            "user_uuid": user.uuid,
            "user_agent": "Linux",
            "event_type": AuthEventType.LOGIN.value,
        }
        for _ in range(2)
        for user in user_sample
    ]
    return user_history_sample
