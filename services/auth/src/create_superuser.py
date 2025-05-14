import asyncio
from typing import AsyncGenerator

from sqlalchemy import select
import typer

from db.postgre import get_session
from models.entity import Role, User

app = typer.Typer()


async def create_superuser(
    username: str, password: str, session_gen: AsyncGenerator = get_session()
) -> None:
    session = await anext(session_gen)
    try:
        result = await session.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise Exception("User already exists")

        role_result = await session.execute(
            select(Role).where(Role.name == "superuser")
        )
        user_role = role_result.scalar_one_or_none()

        if not user_role:
            user_role = Role(name="superuser")
            session.add(user_role)
            await session.commit()
            await session.refresh(user_role)

        user = User(username=username, password=password)
        user.is_active = True
        user.roles = [user_role]

        session.add(user)
        await session.commit()
        await session.refresh(user)
    finally:
        await session.close()


@app.command()
def create(username: str, password: str) -> None:
    asyncio.run(create_superuser(username, password))


if __name__ == "__main__":
    app()
