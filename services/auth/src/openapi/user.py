from datetime import datetime
from http import HTTPStatus
from typing import ClassVar

from pydantic import BaseModel

from schemas.user import LoginHistoryResponse, UserResponse

__all__ = ["GetProfileInfo", "ResetPassword", "ResetLogin", "GetHistory"]

user_uuid = "68039548-01c4-800b-babf-fff7ac5fb54e"
new_password = "new_secure_password123"
new_login = "new_user_login"


class _UserNotFoundExample(BaseModel):
    """Пример ответа для отсутствующего пользователя"""

    example: ClassVar[dict] = {
        "summary": "User not found",
        "value": {"detail": f"User with uuid={user_uuid} not found"},
    }


class _ValidationErrorExample(BaseModel):
    """Пример ошибки валидации"""

    example: ClassVar[dict] = {
        "summary": "Validation error",
        "value": {"detail": "Некорректный пароль."},
    }


class GetProfileInfo(BaseModel):
    """Схема для получения информации о профиле"""

    summary: ClassVar[str] = "Профиль пользователя"
    description: ClassVar[str] = "Данные о пользователе"
    response_description: ClassVar[str] = "Информация о пользователе"

    responses: ClassVar[dict] = {
        HTTPStatus.OK: {
            "description": "Успешный запрос",
            "content": {
                "application/json": {
                    "example": UserResponse(
                        uuid=user_uuid,
                        email="user@example.com",
                        is_active=True,
                        created_at=datetime(2025, 4, 27, 12, 0),
                    )
                }
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "examples": {"User not found": _UserNotFoundExample.example}
                }
            },
        },
    }


class ResetPassword(BaseModel):
    """Схема для сброса пароля"""

    summary: ClassVar[str] = "Смена пароля"
    description: ClassVar[str] = "Обновление пароля пользователя"
    response_description: ClassVar[str] = "Результат операции"

    responses: ClassVar[dict] = {
        HTTPStatus.OK: {
            "description": "Пароль успешно изменен",
            "content": {
                "application/json": {
                    "example": {"message": "Password updated successfully"}
                }
            },
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "examples": {"Validation error": _ValidationErrorExample.example}
                }
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "examples": {"User not found": _UserNotFoundExample.example}
                }
            },
        },
    }


class ResetLogin(BaseModel):
    """Схема для смены логина"""

    summary: ClassVar[str] = "Смена логина"
    description: ClassVar[str] = "Обновление логина пользователя"
    response_description: ClassVar[str] = "Результат операции"

    responses: ClassVar[dict] = {
        HTTPStatus.OK: {
            "description": "Логин успешно изменен",
            "content": {
                "application/json": {
                    "example": {"message": "Login updated successfully"}
                }
            },
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "examples": {
                        "Login exists": {
                            "summary": "Login exists",
                            "value": {"detail": f"Login {new_login} already exists"},
                        }
                    }
                }
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "examples": {"User not found": _UserNotFoundExample.example}
                }
            },
        },
    }


class _HistoryResponseContent(BaseModel):
    """Пример контента истории входов"""

    example: ClassVar[list[LoginHistoryResponse]] = [
        LoginHistoryResponse(
            uuid="cab1e9c5-39ca-4ed7-86a8-fd8be1f17504",
            user_uuid=user_uuid,
            event_type="login",
            user_agent="Mozilla/5.0",
            occurred_at=datetime(2025, 4, 27, 12, 0),
        )
    ]


class GetHistory(BaseModel):
    """Схема для получения истории входов"""

    summary: ClassVar[str] = "История входов"
    description: ClassVar[str] = "История аутентификаций пользователя"
    response_description: ClassVar[str] = "Список записей истории"

    responses: ClassVar[dict] = {
        HTTPStatus.OK: {
            "description": "Успешный запрос",
            "content": {
                "application/json": {"example": _HistoryResponseContent.example}
            },
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "examples": {"User not found": _UserNotFoundExample.example}
                }
            },
        },
    }
