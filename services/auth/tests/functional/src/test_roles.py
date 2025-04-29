"""
Test suite for the 'roles' API endpoints.
"""

from http import HTTPMethod, HTTPStatus
import uuid

import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.entity import User
from testdata.samples.roles import all_role_names, Roles
from testdata.samples.users import user as get_user_sample
from utils.auth import create_access_token


@pytest.mark.asyncio()
class TestAssignRole:
    """Tests for /roles/assign endpoint"""
    endpoint = "roles/assign"
    method = HTTPMethod.PATCH

    async def test_success(
            self,
            create_user,
            create_roles,
            db_session,
            make_request,
            ) -> None:
        """Test successful role assignment."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.OK

        await db_session.refresh(user)
        result = await db_session.execute(
            select(User)
            .where(User.uuid == str(user.uuid))
            .options(selectinload(User.roles))
            )
        user = result.scalar_one_or_none()
        assert set([role.name for role in user.roles]) == set([Roles.PAID_USER.value, Roles.USER.value])

    async def test_user_not_found(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role assignment for a non-existent user."""
        test_users = get_user_sample()
        admin = test_users[0]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(uuid.uuid4()),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_not_found(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role assignment for a non-existent role."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role = Roles.ADMIN.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": "non_existent_role"},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.NOT_FOUND        

    async def test_role_already_assigned(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role assignment when the role is already assigned."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value, Roles.PAID_USER.value])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio()
class TestRevokeRole:
    """Tests for /roles/revoke endpoint"""
    endpoint = "roles/revoke"
    method = HTTPMethod.PATCH
    
    async def test_success(
            self,
            create_user,
            create_roles,
            db_session,
            make_request,
            ) -> None:
        """Test successful role revocation."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value, user_role])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.OK

        await db_session.refresh(user)
        result = await db_session.execute(
            select(User)
            .where(User.uuid == str(user.uuid))
            .options(selectinload(User.roles))
            )
        user = result.scalar_one_or_none()
        assert set([role.name for role in user.roles]) == set([Roles.USER.value])

    async def test_user_not_found(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role revocation for a non-existent user."""
        test_users = get_user_sample()
        admin = test_users[0]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(uuid.uuid4()),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_not_found(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role revocation for a non-existent role."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role = Roles.ADMIN.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": "non_existent_role"},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_not_assigned(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test role revocation when the role is not assigned."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role, user_role = Roles.ADMIN.value, Roles.PAID_USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[Roles.USER.value])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.BAD_REQUEST

    async def test_last_role(
            self,
            create_user,
            create_roles,
            make_request,
            ) -> None:
        """Test revocation of the last role."""
        test_users = get_user_sample()
        admin, user = test_users[0], test_users[1]
        admin_role, user_role = Roles.ADMIN.value, Roles.USER.value
        await create_roles(all_role_names)
        admin = await create_user(**admin, role_names=[admin_role])
        user = await create_user(**user, role_names=[user_role])
        admin_token = create_access_token(admin)

        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={
                "user_uuid": str(user.uuid),
                "role": {"name": user_role},
            },
            token=admin_token,
            )
        assert response.status == HTTPStatus.BAD_REQUEST
