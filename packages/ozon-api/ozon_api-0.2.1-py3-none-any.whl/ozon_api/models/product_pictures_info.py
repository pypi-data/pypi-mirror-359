from typing import List

from pydantic import BaseModel, Field


class ProductPicturesInfoRequestV2(BaseModel):
    """
    Модель запроса для получения информации об изображениях товаров.

    :param product_id: Список идентификаторов товаров
    """

    product_id: List[int] = Field(
        ...,
        description="Список идентификаторов товаров в системе продавца — product_id.",
    )


class ProductPicturesInfoItemV2(BaseModel):
    """
    Модель информации об изображениях одного товара.

    :param product_id: Идентификатор товара
    :param primary_photo: Ссылки на главное изображение
    :param photo: Ссылки на фотографии товара
    :param color_photo: Ссылки на образцы цвета
    :param photo_360: Ссылки на 360° изображения
    """

    product_id: int = Field(
        ..., description="Идентификатор товара в системе продавца — product_id."
    )
    primary_photo: List[str] = Field(
        default_factory=list, description="Ссылка на главное изображение."
    )
    photo: List[str] = Field(
        default_factory=list, description="Ссылки на фотографии товара."
    )
    color_photo: List[str] = Field(
        default_factory=list, description="Ссылки на загруженные образцы цвета."
    )
    photo_360: List[str] = Field(
        default_factory=list, description="Ссылки на изображения 360."
    )


class ProductPicturesInfoErrorV2(BaseModel):
    """
    Модель ошибки при получении информации об изображениях товара.

    :param product_id: Идентификатор товара
    :param error: Описание ошибки
    """

    product_id: int = Field(
        ..., description="Идентификатор товара, по которому возникла ошибка."
    )
    error: str = Field(..., description="Описание ошибки.")


class ProductPicturesInfoResponseV2(BaseModel):
    """
    Модель ответа с информацией об изображениях товаров и ошибках.

    :param items: Список изображений товаров
    :param errors: Список ошибок
    """

    items: List[ProductPicturesInfoItemV2] = Field(
        default_factory=list, description="Изображения товаров."
    )
    errors: List[ProductPicturesInfoErrorV2] | None = Field(
        default_factory=list, description="Список ошибок по изображениям товара."
    )
