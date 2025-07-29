from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_related_sku import (
    ProductRelatedSkuRequest,
    ProductRelatedSkuResponse,
)


class OzonProductRelatedSkuAPI(OzonAPIBase):
    async def product_related_sku(
        self: Type["OzonProductRelatedSkuAPI"], request: ProductRelatedSkuRequest
    ) -> ProductRelatedSkuResponse:
        """
        Метод для получения списка товаров, связанных с указанным товаром.

        :param request: Данные для получения списка связанных товаров
        :return: Ответ с результатом получения списка связанных товаров
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/related-sku/get",
            json=request.model_dump(),
        )
        return ProductRelatedSkuResponse(**data)
