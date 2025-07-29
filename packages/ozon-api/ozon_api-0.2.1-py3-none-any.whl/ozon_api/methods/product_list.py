from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_list import ProductListRequest, ProductListResult


class OzonProductListAPI(OzonAPIBase):
    async def product_list(
        self: Type["OzonProductListAPI"], request: ProductListRequest
    ) -> ProductListResult:
        """
        Метод для получения списка всех товаров.
        • Если вы используете фильтр по идентификатору `offer_id` или `product_id`, остальные параметры заполнять не обязательно.
        • За один раз вы можете использовать только одну группу идентификаторов, не больше `1000` товаров.
        • Если вы не используете для отображения идентификаторы, укажите `limit` и `last_id` в следующих запросах.

        :param request: Данные для получения списка товаров
        :return: Ответ с результатом получения списка товаров
        """
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="product/list",
            json=request.model_dump(),
        )
        return ProductListResult(**data)

    async def product_info_limit(self: Type["OzonProductListAPI"]) -> dict[str, any]:
        """
        Метод для получения информации о лимитах:

        • На ассортимент — сколько всего товаров можно создать в вашем личном кабинете.
        • На создание товаров — сколько товаров можно создать в сутки.
        • На обновление товаров — сколько товаров можно отредактировать в сутки.

        Если у вас есть лимит на ассортимент и вы израсходуете его, вы не сможете создавать новые товары.

        :return: Ответ с результатом получения информации о товаре
        """
        data = await self._request(
            method="post",
            api_version="v4",
            endpoint="product/info/limit",
        )
        return data
