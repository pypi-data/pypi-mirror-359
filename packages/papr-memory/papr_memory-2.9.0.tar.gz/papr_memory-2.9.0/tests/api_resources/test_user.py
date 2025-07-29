# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from papr_memory import Papr, AsyncPapr
from tests.utils import assert_matches_type
from papr_memory.types import (
    UserResponse,
    UserListResponse,
    UserDeleteResponse,
    UserCreateBatchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUser:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Papr) -> None:
        user = client.user.create(
            external_id="user123",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Papr) -> None:
        user = client.user.create(
            external_id="user123",
            x_api_key="X-API-Key",
            email="user@example.com",
            metadata={
                "name": "John Doe",
                "preferences": {"theme": "dark"},
            },
            type="developerUser",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Papr) -> None:
        response = client.user.with_raw_response.create(
            external_id="user123",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Papr) -> None:
        with client.user.with_streaming_response.create(
            external_id="user123",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Papr) -> None:
        user = client.user.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Papr) -> None:
        user = client.user.update(
            user_id="user_id",
            x_api_key="X-API-Key",
            email="updated.user@example.com",
            external_id="updated_user_123",
            metadata={
                "name": "Updated User",
                "preferences": {"theme": "light"},
            },
            type="developerUser",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Papr) -> None:
        response = client.user.with_raw_response.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Papr) -> None:
        with client.user.with_streaming_response.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Papr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.with_raw_response.update(
                user_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Papr) -> None:
        user = client.user.list(
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Papr) -> None:
        user = client.user.list(
            x_api_key="X-API-Key",
            email="email",
            external_id="external_id",
            page=1,
            page_size=1,
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Papr) -> None:
        response = client.user.with_raw_response.list(
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Papr) -> None:
        with client.user.with_streaming_response.list(
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Papr) -> None:
        user = client.user.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: Papr) -> None:
        user = client.user.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
            is_external=True,
        )
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Papr) -> None:
        response = client.user.with_raw_response.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Papr) -> None:
        with client.user.with_streaming_response.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserDeleteResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Papr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.with_raw_response.delete(
                user_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_batch(self, client: Papr) -> None:
        user = client.user.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserCreateBatchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_batch(self, client: Papr) -> None:
        response = client.user.with_raw_response.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserCreateBatchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_batch(self, client: Papr) -> None:
        with client.user.with_streaming_response.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserCreateBatchResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Papr) -> None:
        user = client.user.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Papr) -> None:
        response = client.user.with_raw_response.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Papr) -> None:
        with client.user.with_streaming_response.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Papr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.user.with_raw_response.get(
                user_id="",
                x_api_key="X-API-Key",
            )


class TestAsyncUser:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.create(
            external_id="user123",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.create(
            external_id="user123",
            x_api_key="X-API-Key",
            email="user@example.com",
            metadata={
                "name": "John Doe",
                "preferences": {"theme": "dark"},
            },
            type="developerUser",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.create(
            external_id="user123",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.create(
            external_id="user123",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.update(
            user_id="user_id",
            x_api_key="X-API-Key",
            email="updated.user@example.com",
            external_id="updated_user_123",
            metadata={
                "name": "Updated User",
                "preferences": {"theme": "light"},
            },
            type="developerUser",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.update(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncPapr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.with_raw_response.update(
                user_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.list(
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.list(
            x_api_key="X-API-Key",
            email="email",
            external_id="external_id",
            page=1,
            page_size=1,
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.list(
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.list(
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
            is_external=True,
        )
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserDeleteResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.delete(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserDeleteResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncPapr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.with_raw_response.delete(
                user_id="",
                x_api_key="X-API-Key",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_batch(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserCreateBatchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_batch(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserCreateBatchResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_batch(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.create_batch(
            users=[{"external_id": "user123"}],
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserCreateBatchResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncPapr) -> None:
        user = await async_client.user.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        )
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncPapr) -> None:
        response = await async_client.user.with_raw_response.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncPapr) -> None:
        async with async_client.user.with_streaming_response.get(
            user_id="user_id",
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncPapr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.user.with_raw_response.get(
                user_id="",
                x_api_key="X-API-Key",
            )
