from typing import List, Literal

from pydantic import BaseModel, Field


class ProductListFilter(BaseModel):
    """
    Модель фильтра для получения списка товаров.

    Позволяет фильтровать товары по артикулу, идентификатору и видимости.
    """

    offer_id: List[str] | None = Field(None, description="Артикулы товаров (offer_id)")
    product_id: List[int] | None = Field(None, description="ID товаров (product_id)")
    visibility: str | None = Field(
        None, description="Видимость товара (ALL, VISIBLE, INVISIBLE)"
    )
    # Можно добавить другие поля фильтра по необходимости


class ProductListRequest(BaseModel):
    """
    Модель запроса для получения списка товаров.

    :param filter: Фильтр товаров
    :param last_id: Идентификатор последнего товара для пагинации
    :param limit: Максимальное количество товаров в ответе (1-1000)
    :param sort_by: Поле для сортировки
    :param sort_dir: Направление сортировки (ASC или DESC)
    """

    filter: ProductListFilter = Field(..., description="Фильтр товаров")
    last_id: str | None = Field(
        None, description="Идентификатор последнего товара для пагинации"
    )
    limit: int = Field(
        1000, description="Максимальное количество товаров в ответе (1-1000)"
    )
    sort_by: str | None = Field(None, description="Сортировка (например, 'product_id')")
    sort_dir: Literal["ASC", "DESC"] | None = Field(
        None, description="Направление сортировки"
    )


class ProductListItem(BaseModel):
    """
    Модель одного товара в списке товаров.

    :param product_id: ID товара в системе Ozon
    :param offer_id: Артикул товара
    :param visibility: Видимость товара
    """

    product_id: int = Field(..., description="ID товара в системе Ozon")
    offer_id: str = Field(..., description="Артикул товара (offer_id)")
    visibility: str = Field(..., description="Видимость товара")
    # Можно добавить другие поля из ответа по необходимости


class ProductListResponse(BaseModel):
    """
    Модель ответа на запрос списка товаров.

    :param items: Список товаров
    :param total: Общее количество товаров
    :param last_id: Идентификатор последнего товара для пагинации
    """

    items: List[dict] = Field(..., description="Список товаров")
    total: int = Field(..., description="Общее количество товаров")
    last_id: str | None = Field(
        None, description="Идентификатор последнего товара для пагинации"
    )


class ProductListResult(BaseModel):
    """
    Модель результата запроса списка товаров.

    :param result: Ответ с данными о товарах
    """

    result: ProductListResponse
