from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_info_attributes import (
    ProductInfoAttributesRequest,
    ProductInfoAttributesResult,
)


class OzonProductInfoAttributesAPI(OzonAPIBase):
    async def product_info_attributes(
        self: Type["OzonProductInfoAttributesAPI"],
        request: ProductInfoAttributesRequest,
    ) -> ProductInfoAttributesResult:
        """
        Получить описание характеристик товара по идентификатору и видимости.

        Пример использования:
        ```python
        from ozon_api.models.product_info_attributes import ProductInfoAttributesRequest, ProductInfoAttributesFilter
        request = ProductInfoAttributesRequest(
            filter=ProductInfoAttributesFilter(offer_id=["123"], visibility="VISIBLE"),
            limit=10,
            sort_by="sku",
            sort_dir="asc"
        )
        result = await api.product_info_attributes(request)
        ```
        :param request: Данные для получения описания характеристик товара
        :return: Описание характеристик товара
        """
        data = await self._request(
            method="post",
            api_version="v4",
            endpoint="product/info/attributes",
            json=request.model_dump(),
        )
        return ProductInfoAttributesResult(**data)
