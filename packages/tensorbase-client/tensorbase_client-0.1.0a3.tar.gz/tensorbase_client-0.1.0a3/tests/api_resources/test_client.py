# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from tensorbase_client import Tensorbase, AsyncTensorbase
from tensorbase_client.types import HealthCheckResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_health_check(self, client: Tensorbase) -> None:
        client_ = client.health_check()
        assert_matches_type(HealthCheckResponse, client_, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_health_check(self, client: Tensorbase) -> None:
        response = client.with_raw_response.health_check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(HealthCheckResponse, client_, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_health_check(self, client: Tensorbase) -> None:
        with client.with_streaming_response.health_check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(HealthCheckResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_health_check(self, async_client: AsyncTensorbase) -> None:
        client = await async_client.health_check()
        assert_matches_type(HealthCheckResponse, client, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_health_check(self, async_client: AsyncTensorbase) -> None:
        response = await async_client.with_raw_response.health_check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(HealthCheckResponse, client, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_health_check(self, async_client: AsyncTensorbase) -> None:
        async with async_client.with_streaming_response.health_check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(HealthCheckResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True
