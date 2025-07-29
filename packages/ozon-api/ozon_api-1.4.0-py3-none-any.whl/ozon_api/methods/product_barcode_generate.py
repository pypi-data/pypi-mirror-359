from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_barcode_generate import (
    ProductBarcodeGenerateRequest,
    ProductBarcodeGenerateResponse,
)


class OzonProductBarcodeGenerateAPI(OzonAPIBase):
    async def product_barcode_generate(
        self: Type["OzonProductBarcodeGenerateAPI"],
        request: ProductBarcodeGenerateRequest,
    ) -> ProductBarcodeGenerateResponse:
        """
        Если у товара нет штрихкода, вы можете создать его с помощью этого метода. Если штрихкод уже есть, но он не указан в системе Ozon, вы можете привязать его через метод `/v1/barcode/add`.
        • За один запрос вы можете создать штрихкоды не больше чем для `100` товаров.
        • С одного аккаунта продавца можно использовать метод не больше `20` раз в минуту.

        :param request: Данные для создания штрих-кодов
        :return: Ответ с результатом создания штрих-кодов
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="barcode/generate",
            json=request.model_dump(),
        )
        return ProductBarcodeGenerateResponse(**data)
