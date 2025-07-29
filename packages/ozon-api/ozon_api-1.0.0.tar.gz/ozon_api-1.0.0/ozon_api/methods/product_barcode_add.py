from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_barcode_add import (
    ProductBarcodeAddRequest,
    ProductBarcodeAddResponse,
)


class OzonProductBarcodeAddAPI(OzonAPIBase):
    async def product_barcode_add(
        self: Type["OzonProductBarcodeAddAPI"], request: ProductBarcodeAddRequest
    ) -> ProductBarcodeAddResponse:
        """
        Если у товара есть штрихкод, который не указан в системе Ozon, привяжите его с помощью этого метода. Если штрихкода нет, вы можете создать его через метод `/v1/barcode/generate`.
        • За один запрос вы можете назначить штрихкод не больше чем на `100` товаров.
        • На одном товаре может быть до `100` штрихкодов.
        • С одного аккаунта продавца можно использовать метод не больше `20` раз в минуту.

        :param request: Данные для добавления штрих-кодов
        :return: Ответ с результатом добавления штрих-кодов
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="barcode/add",
            json=request.model_dump(),
        )
        return ProductBarcodeAddResponse(**data)
