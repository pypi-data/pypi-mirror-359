import os

import pytest
from dotenv import load_dotenv

from ozon_api import OzonAPI
from ozon_api.models.product_archive import (
    ProductArchiveRequest,
    ProductArchiveResponse,
    ProductUnarchiveRequest,
    ProductUnarchiveResponse,
)

load_dotenv()
client_id = os.getenv("OZON_CLIENT_ID")
api_key = os.getenv("OZON_CLIENT_SECRET")
ozon = OzonAPI(client_id, api_key)


@pytest.mark.asyncio
async def test_product_archive():
    async with ozon as api:
        request = ProductArchiveRequest(
            product_id=[716653639, 716653622]
        )  # Замените на валидные product_id
        response = await api.product_archive(request)
        assert isinstance(response, ProductArchiveResponse)
        assert hasattr(response, "result")


@pytest.mark.asyncio
async def test_product_unarchive():
    async with ozon as api:
        request = ProductUnarchiveRequest(
            product_id=[716653639, 716653622]
        )  # Замените на валидные product_id
        response = await api.product_unarchive(request)
        assert isinstance(response, ProductUnarchiveResponse)
        assert hasattr(response, "result")
