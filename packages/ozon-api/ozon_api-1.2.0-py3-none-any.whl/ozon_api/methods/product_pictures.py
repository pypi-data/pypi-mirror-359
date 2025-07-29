from typing import Any, Type

from ozon_api.base import OzonAPIBase


class OzonProductPicturesAPI(OzonAPIBase):
    async def product_pictures_import(
        self: Type["OzonProductPicturesAPI"], items: dict
    ) -> dict[str, Any]:
        """
        Метод для загрузки или обновления изображений товара.
        • При каждом вызове метода передавайте все изображения, которые должны быть на карточке товара. Например, если вы вызвали метод и загрузили 10 изображений, а затем вызвали метод второй раз и загрузили ещё одно, то все 10 предыдущих сотрутся.
        • Для загрузки передайте адрес ссылки на изображение в общедоступном облачном хранилище. Формат изображения по ссылке — JPG или PNG.
        • Изображения в массиве images располагайте в соответствии с желаемым порядком на сайте. Главным будет первое изображение в массиве.
        • Для каждого товара вы можете загрузить до 15 изображений.
        • Для загрузки изображений 360 используйте поле images360, для загрузки маркетингового цвета — color_image.
        • Если вы хотите изменить состав или порядок изображений, получите информацию с помощью метода `/v3/product/info/list` — в нём отображается текущий порядок и состав изображений. Скопируйте данные полей images, images360, color_image, измените и дополните состав или порядок в соответствии с необходимостью.


        :param items: Данные для импорта изображений товаров
        :return: Ответ с результатом импорта изображений товаров
        """
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/pictures/import",
            json=items,
        )
        return data

    async def product_pictures_info(
        self: Type["OzonProductPicturesAPI"], product_id: list[str]
    ) -> dict[str, Any]:
        """
        Метод для получения информации о изображениях товара.

        :param product_id: Список идентификаторов товаров в системе продавца — product_id (max 1000)
        :return: Ответ с информацией о изображениях товара
        """
        data = await self._request(
            method="post",
            api_version="v2",
            endpoint="product/pictures/info",
            json={"product_id": product_id},
        )
        return data
