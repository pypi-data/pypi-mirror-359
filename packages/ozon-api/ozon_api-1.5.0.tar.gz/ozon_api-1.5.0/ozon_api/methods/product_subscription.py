from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_subscription import (
    ProductSubscriptionRequest,
    ProductSubscriptionResponse,
)


class OzonProductSubscriptionAPI(OzonAPIBase):
    async def product_subscription(
        self: Type["OzonProductSubscriptionAPI"], request: ProductSubscriptionRequest
    ) -> ProductSubscriptionResponse:
        """
        Метод для получения информации о подписке на товары.

        :param request: Данные для получения информации о подписке на товары
        :return: Ответ с результатом получения информации о подписке на товары
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/info/subscription",
            json=request.model_dump(),
        )
        return ProductSubscriptionResponse(**data)
