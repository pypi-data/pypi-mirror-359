import os

import pytest
from dotenv import load_dotenv

from ozon_api import OzonAPI

load_dotenv()
client_id = os.getenv("OZON_CLIENT_ID")
api_key = os.getenv("OZON_CLIENT_SECRET")
ozon = OzonAPI(client_id, api_key)

# @pytest.mark.asyncio
# async def test_product_pictures_import():
#     async with ozon as api:
#         items = {}  # Заполните валидными данными
#         response = await api.product_pictures_import(items)
#         assert isinstance(response, dict)


@pytest.mark.asyncio
async def test_product_pictures_info():
    async with ozon as api:
        product_id = ["2275511907"]  # Замените на валидные product_id
        response = await api.product_pictures_info(product_id)
        assert isinstance(response, dict)
