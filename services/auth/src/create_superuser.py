import asyncio
from fastapi import Depends, HTTPException, status, Query, Header
from sqlalchemy import select
import typer

from models.entity import User, Role

from db.postgre import get_session

app = typer.Typer()


async def create_superuser(email: str, password: str, session_gen=get_session()):
    session = await anext(session_gen)
    try:
        result = await session.execute(select(User).where(User.email == email))
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

        user = User(email=email, password=password)
        user.is_active = True
        user.roles = [user_role]

        session.add(user)
        await session.commit()
        await session.refresh(user)
    finally:
        await session.close()


@app.command()
def create(email: str, password: str):
    asyncio.run(create_superuser(email, password))


if __name__ == "__main__":
    app()
