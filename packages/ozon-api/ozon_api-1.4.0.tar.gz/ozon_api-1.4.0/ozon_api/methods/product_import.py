from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.import_by_sku import ImportBySku
from ozon_api.models.product_attributes_update import ProductAttributesUpdate
from ozon_api.models.product_import import ProductImport
from ozon_api.models.product_import_info import ProductImportInfo
from ozon_api.models.products_delete import (
    ProductsDeleteRequest,
    ProductsDeleteResponse,
)
from ozon_api.models.upload_digital_codes import (
    UploadDigitalCodesInfoRequest,
    UploadDigitalCodesInfoResponse,
    UploadDigitalCodesRequest,
    UploadDigitalCodesResponse,
)


class OzonProductImportAPI(OzonAPIBase):
    """
    Класс для работы с импортом товаров и связанных операций через API Ozon.

    Позволяет импортировать товары, получать информацию об импорте, обновлять характеристики, удалять товары и загружать цифровые коды.
    """

    async def product_import(
        self: Type["OzonProductImportAPI"], request: ProductImport
    ) -> dict:
        """
        Импортировать товары в Ozon.

        :param request: Данные для импорта товаров
        :return: Результат выполнения операции
        """
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="product/import",
            json=request.model_dump(),
        )
        return data

    async def product_import_info(
        self: Type["OzonProductImportAPI"], request: ProductImportInfo
    ) -> dict:
        """
        Получить информацию о задаче импорта товаров.

        :param request: Данные для запроса информации об импорте
        :return: Информация о задаче импорта
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/import/info",
            json=request.model_dump(),
        )
        return data

    async def product_import_by_sku(
        self: Type["OzonProductImportAPI"], request: ImportBySku
    ) -> dict:
        """
        Импортировать товары по SKU.

        :param request: Данные для импорта по SKU
        :return: Результат выполнения операции
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/import-by-sku",
            json=request.model_dump(),
        )
        return data

    async def product_attributes_update(
        self: Type["OzonProductImportAPI"], request: ProductAttributesUpdate
    ) -> dict:
        """
        Обновить характеристики товаров.

        :param request: Данные для обновления характеристик
        :return: Результат выполнения операции
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/attributes/update",
            json=request.model_dump(),
        )
        return data

    async def products_delete(
        self: Type["OzonProductImportAPI"], request: ProductsDeleteRequest
    ) -> ProductsDeleteResponse:
        """
        Удалить товары из системы Ozon.

        :param request: Данные для удаления товаров
        :return: Ответ с результатом удаления
        """
        data = await self._request(
            method="post",
            api_version="v2",
            endpoint="products/delete",
            json=request.model_dump(),
        )
        return ProductsDeleteResponse(**data)

    async def upload_digital_codes(
        self: Type["OzonProductImportAPI"], request: UploadDigitalCodesRequest
    ) -> UploadDigitalCodesResponse:
        """
        Загрузить цифровые коды для товаров.

        :param request: Данные для загрузки цифровых кодов
        :return: Ответ с результатом загрузки
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/upload_digital_codes",
            json=request.model_dump(),
        )
        return UploadDigitalCodesResponse(**data)

    async def upload_digital_codes_info(
        self: Type["OzonProductImportAPI"], request: UploadDigitalCodesInfoRequest
    ) -> UploadDigitalCodesInfoResponse:
        """
        Получить информацию о задаче загрузки цифровых кодов.

        :param request: Данные для запроса информации о загрузке
        :return: Ответ с информацией о задаче
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/upload_digital_codes/info",
            json=request.model_dump(),
        )
        return UploadDigitalCodesInfoResponse(**data)
