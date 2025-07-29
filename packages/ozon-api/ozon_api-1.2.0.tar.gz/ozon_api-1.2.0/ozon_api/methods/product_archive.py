from typing import Type

from ozon_api.base import OzonAPIBase
from ozon_api.models.product_archive import (
    ProductArchiveRequest,
    ProductArchiveResponse,
    ProductUnarchiveRequest,
    ProductUnarchiveResponse,
)


class OzonProductArchiveAPI(OzonAPIBase):
    """
    Класс для работы с архивированием и разархивированием товаров через Ozon API.

    Предоставляет методы для архивирования и восстановления товаров с помощью соответствующих эндпоинтов Ozon API.
    """

    async def product_archive(
        self: Type["OzonProductArchiveAPI"], request: ProductArchiveRequest
    ) -> ProductArchiveResponse:
        """
        Архивирует товары на платформе Ozon.

        Отправляет POST-запрос к эндпоинту 'product/archive' для архивирования указанных товаров.

        :param request: Объект запроса с параметрами для архивирования товаров.
        :type request: ProductArchiveRequest
        :return: Ответ API с результатом архивирования товаров.
        :rtype: ProductArchiveResponse
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/archive",
            json=request.model_dump(),
        )
        return ProductArchiveResponse(**data)

    async def product_unarchive(
        self: Type["OzonProductArchiveAPI"], request: ProductUnarchiveRequest
    ) -> ProductUnarchiveResponse:
        """
        Разархивирует товары на платформе Ozon.

        Отправляет POST-запрос к эндпоинту 'product/unarchive' для восстановления ранее архивированных товаров.

        :param request: Объект запроса с параметрами для разархивирования товаров.
        :type request: ProductUnarchiveRequest
        :return: Ответ API с результатом разархивирования товаров.
        :rtype: ProductUnarchiveResponse
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/unarchive",
            json=request.model_dump(),
        )
        return ProductUnarchiveResponse(**data)
