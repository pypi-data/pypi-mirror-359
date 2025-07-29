# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quarkupy, AsyncQuarkupy
from tests.utils import assert_matches_type
from quarkupy.types.registry.quark.files import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLancedbIngest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quarkupy) -> None:
        lancedb_ingest = client.registry.quark.vector.lancedb_ingest.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        )
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quarkupy) -> None:
        lancedb_ingest = client.registry.quark.vector.lancedb_ingest.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
            opt_operation="opt_operation",
            opt_uri="opt_uri",
        )
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quarkupy) -> None:
        response = client.registry.quark.vector.lancedb_ingest.with_raw_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lancedb_ingest = response.parse()
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quarkupy) -> None:
        with client.registry.quark.vector.lancedb_ingest.with_streaming_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lancedb_ingest = response.parse()
            assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLancedbIngest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuarkupy) -> None:
        lancedb_ingest = await async_client.registry.quark.vector.lancedb_ingest.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        )
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuarkupy) -> None:
        lancedb_ingest = await async_client.registry.quark.vector.lancedb_ingest.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
            opt_operation="opt_operation",
            opt_uri="opt_uri",
        )
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuarkupy) -> None:
        response = await async_client.registry.quark.vector.lancedb_ingest.with_raw_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lancedb_ingest = await response.parse()
        assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuarkupy) -> None:
        async with async_client.registry.quark.vector.lancedb_ingest.with_streaming_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lancedb_ingest = await response.parse()
            assert_matches_type(QuarkHistoryItem, lancedb_ingest, path=["response"])

        assert cast(Any, response.is_closed) is True
