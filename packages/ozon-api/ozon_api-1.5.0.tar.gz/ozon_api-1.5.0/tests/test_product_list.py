import os

import pytest
from dotenv import load_dotenv

from ozon_api import OzonAPI
from ozon_api.models.product_list import (
    ProductListFilter,
    ProductListRequest,
    ProductListResult,
)

load_dotenv()
client_id = os.getenv("OZON_CLIENT_ID")
api_key = os.getenv("OZON_CLIENT_SECRET")
ozon = OzonAPI(client_id, api_key)


@pytest.mark.asyncio
async def test_product_list():
    async with ozon as api:
        filter = ProductListFilter()  # Заполните фильтр при необходимости
        request = ProductListRequest(filter=filter)
        response = await api.product_list(request)
        assert isinstance(response, ProductListResult)
        assert hasattr(response, "result")
        assert hasattr(response.result, "items")
        assert hasattr(response.result, "total")


@pytest.mark.asyncio
async def test_product_info_limit():
    async with ozon as api:
        response = await api.product_info_limit()
        assert isinstance(response, dict)
