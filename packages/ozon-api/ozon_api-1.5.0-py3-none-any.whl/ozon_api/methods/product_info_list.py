from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_info_list import (
    ProductInfoListRequest,
    ProductInfoListResponse,
)


class OzonProductInfoListAPI(OzonAPIBase):
    async def product_info_list(
        self: Type["OzonProductInfoListAPI"], request: ProductInfoListRequest
    ) -> ProductInfoListResponse:
        """
        Метод для получения информации о товарах по их идентификаторам.

        :param request: Данные для получения информации о товарах
        :return: Ответ с информацией о товарах
        """
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="product/info/list",
            json=request.model_dump(),
        )
        return ProductInfoListResponse(**data)
