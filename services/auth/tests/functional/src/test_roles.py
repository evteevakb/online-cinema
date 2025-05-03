"""
Test suite for the 'roles' API endpoints.
"""

from http import HTTPMethod, HTTPStatus
import uuid

import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.entity import Role, User
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
        assert set([role.name for role in user.roles]) == set(
            [Roles.PAID_USER.value, Roles.USER.value]
        )

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
        user = await create_user(
            **user, role_names=[Roles.USER.value, Roles.PAID_USER.value]
        )
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


@pytest.mark.asyncio()
class TestCreateRole:
    """Tests for /roles endpoint"""

    endpoint = "roles"
    method = HTTPMethod.POST

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        new_role = "NewRole"
        desc = "description"
        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={"name": new_role, "description": desc},
            token=su_token,
        )

        result = await db_session.execute(select(Role).where(Role.name == new_role))
        role = result.scalar_one_or_none()

        assert response.status == HTTPStatus.OK
        assert role.name == new_role
        assert role.description == desc

    async def test_duplicate_failure(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        new_role = Roles.ADMIN.value
        desc = "description"
        response = await make_request(
            method=self.method,
            endpoint=self.endpoint,
            json={"name": new_role, "description": desc},
            token=su_token,
        )

        assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio()
class TestDetailRole:
    """Tests for /roles/{name} endpoint"""

    endpoint = "roles"
    method = HTTPMethod.GET

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        name = Roles.ADMIN.value

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{name}",
            token=su_token,
        )

        assert response.status == HTTPStatus.OK
        assert response.body.get("name") == name

    async def test_non_existing(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        name = "NonExistingRole"

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{name}",
            token=su_token,
        )

        assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio()
class TestListRole:
    """Tests for /roles endpoint"""

    endpoint = "roles"
    method = HTTPMethod.GET

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}",
            token=su_token,
        )

        assert response.status == HTTPStatus.OK
        assert sorted([role.get("name") for role in response.body]) == sorted(
            all_role_names
        )


@pytest.mark.asyncio()
class TestUpdateRole:
    """Tests for /roles/{name} endpoint"""

    endpoint = "roles"
    method = HTTPMethod.PUT

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        new_name = "FREE_USER"
        new_desc = "someDesc"
        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{Roles.USER.value}",
            json={"name": new_name, "description": new_desc},
            token=su_token,
        )

        assert response.status == HTTPStatus.OK

        response = await make_request(
            method="GET",
            endpoint=f"{self.endpoint}/{new_name}",
            token=su_token,
        )

        assert response.status == HTTPStatus.OK
        assert response.body.get("name") == new_name
        assert response.body.get("description") == new_desc

    async def test_non_existing(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        new_name = "FREE_USER"
        new_desc = "someDesc"
        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{new_name}",
            json={"name": "RNDM", "description": new_desc},
            token=su_token,
        )

        assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio()
class TestDeleteRole:
    """Tests for /roles/{name} endpoint"""

    endpoint = "roles"
    method = HTTPMethod.DELETE

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{Roles.PAID_USER.value}",
            token=su_token,
        )

        assert response.status == HTTPStatus.OK
        assert response.body == {"message": f"Role {Roles.PAID_USER.value} deleted"}

        response = await make_request(
            method="GET",
            endpoint=f"{self.endpoint}/{Roles.PAID_USER.value}",
            token=su_token,
        )

        assert response.status == HTTPStatus.NOT_FOUND

    async def test_non_existing(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/NonExisting",
            token=su_token,
        )

        assert response.status == HTTPStatus.NOT_FOUND

    async def test_non_superuser_role(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        user = test_users[0]
        user_role = Roles.USER.value
        await create_roles(all_role_names)
        user = await create_user(**user, role_names=[user_role])
        user_token = create_access_token(user)

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{Roles.PAID_USER.value}",
            token=user_token,
        )

        assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio()
class TestListUserRole:
    """Tests for /roles/user/{user_uuid} endpoint"""

    endpoint = "roles/user"
    method = HTTPMethod.GET

    async def test_success(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        user_role = Roles.USER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role, user_role])

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{su_user.uuid}",
        )

        assert response.status == HTTPStatus.OK
        assert sorted(response.body) == sorted([su_role, user_role])

    async def test_non_existing(
        self,
        create_user,
        create_roles,
        db_session,
        make_request,
    ) -> None:
        test_users = get_user_sample()
        su = test_users[0]
        su_role = Roles.SUPERUSER.value
        await create_roles(all_role_names)
        su_user = await create_user(**su, role_names=[su_role])
        su_token = create_access_token(su_user)

        response = await make_request(
            method=self.method,
            endpoint=f"{self.endpoint}/{uuid.uuid4()}",
            token=su_token,
        )

        assert response.status == HTTPStatus.NOT_FOUND
