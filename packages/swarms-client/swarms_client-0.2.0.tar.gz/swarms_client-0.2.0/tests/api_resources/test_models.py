# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from swarms_client import SwarmsClient, AsyncSwarmsClient
from swarms_client.types import ModelListAvailableResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize(
        "client", [False, True], indirect=True, ids=["loose", "strict"]
    )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_available(self, client: SwarmsClient) -> None:
        model = client.models.list_available()
        assert_matches_type(ModelListAvailableResponse, model, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_available(self, client: SwarmsClient) -> None:
        response = client.models.with_raw_response.list_available()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelListAvailableResponse, model, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_available(self, client: SwarmsClient) -> None:
        with client.models.with_streaming_response.list_available() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelListAvailableResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client",
        [False, True, {"http_client": "aiohttp"}],
        indirect=True,
        ids=["loose", "strict", "aiohttp"],
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_available(self, async_client: AsyncSwarmsClient) -> None:
        model = await async_client.models.list_available()
        assert_matches_type(ModelListAvailableResponse, model, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_available(
        self, async_client: AsyncSwarmsClient
    ) -> None:
        response = await async_client.models.with_raw_response.list_available()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelListAvailableResponse, model, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_available(
        self, async_client: AsyncSwarmsClient
    ) -> None:
        async with async_client.models.with_streaming_response.list_available() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelListAvailableResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True
