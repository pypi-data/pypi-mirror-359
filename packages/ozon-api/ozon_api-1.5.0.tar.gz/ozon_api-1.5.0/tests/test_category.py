import os

import pytest
from dotenv import load_dotenv

from ozon_api import OzonAPI

load_dotenv()
client_id = os.getenv("OZON_CLIENT_ID")
api_key = os.getenv("OZON_CLIENT_SECRET")
ozon = OzonAPI(client_id, api_key)

ozon.description_category_id = 17027949
ozon.type_id = 94765


@pytest.mark.asyncio
async def test_get_description_category_tree():
    async with ozon as api:
        response = await api.get_description_category_tree()
        assert hasattr(response, "model_dump")
        data = response.model_dump()
        assert isinstance(data, dict)
        assert "result" in data or data != {}


@pytest.mark.asyncio
async def test_get_description_category_attribute():
    async with ozon as api:
        response = await api.get_description_category_attribute()
        assert isinstance(response, dict)
        assert "result" in response or response != {}


@pytest.mark.asyncio
async def test_get_description_category_attribute_values():
    async with ozon as api:
        result = await api.get_description_category_attribute_values(
            attribute_id=85, name="Бренд"
        )
        assert isinstance(result, dict)
        assert "result" in result


@pytest.mark.asyncio
async def test_get_description_category_attribute_values_search():
    async with ozon as api:
        response = await api.get_description_category_attribute_values_search(
            attribute_id=85, value="Cordiant"
        )
        assert isinstance(response, dict)


@pytest.mark.asyncio
async def test_get_full_category_info():
    async with ozon as api:
        result = await api.get_full_category_info()
        assert isinstance(result, list)
