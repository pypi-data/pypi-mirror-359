from typing import Any, Dict, List, Type

from ozon_api.base import OzonAPIBase
from ozon_api.models import CategoryAttributeResponse, CategoryTreeResponse


class OzonCategoryAPI(OzonAPIBase):
    """
    Класс для работы с категориями Ozon через API.

    Позволяет получать дерево категорий, атрибуты категорий, значения атрибутов и полную информацию о категории.
    """

    async def get_description_category_tree(
        self: Type["OzonCategoryAPI"],
    ) -> CategoryTreeResponse:
        """
        Получить дерево категорий Ozon.

        :return: Ответ с деревом категорий (CategoryTreeResponse)
        """
        response = await self._request(
            method="post",
            api_version="v1",
            endpoint="description-category/tree",
        )
        return CategoryTreeResponse(**response)

    async def get_description_category_attribute(
        self: Type["OzonCategoryAPI"], category_id: int = 0
    ) -> dict:
        """
        Получить атрибуты для заданной категории.

        :param category_id: Идентификатор категории (по умолчанию 0)
        :return: Словарь с атрибутами категории
        """
        response = await self._request(
            method="post",
            api_version="v1",
            endpoint="description-category/attribute",
            json={
                "description_category_id": self._OzonAPIBase__description_category_id,
                "type_id": self._OzonAPIBase__type_id,
                "language": self._OzonAPIBase__language,
            },
        )
        return CategoryAttributeResponse(**response).model_dump()

    async def get_description_category_attribute_values(
        self: Type["OzonCategoryAPI"],
        name: str = "",
        attribute_id: int = 0,
        last_value_id: int = 0,
        limit: int = 5000,
    ) -> List[Dict[str, Any]]:
        """
        Получить значения для атрибута категории.

        :param name: Название атрибута (опционально)
        :param attribute_id: Идентификатор атрибута
        :param last_value_id: Последний полученный id значения (для пагинации)
        :param limit: Максимальное количество значений за запрос
        :return: Список значений атрибута
        """
        result: List[Dict[str, Any]] = []
        while True:
            data = await self._request(
                method="post",
                api_version="v1",
                endpoint="description-category/attribute/values",
                json={
                    "attribute_id": attribute_id,
                    "description_category_id": self._OzonAPIBase__description_category_id,
                    "language": self._OzonAPIBase__language,
                    "last_value_id": last_value_id,
                    "limit": limit,
                    "type_id": self._OzonAPIBase__type_id,
                },
            )
            try:
                result.extend(data.get("result", []))
                last_value_id = data["result"][-1]["id"]
            except Exception:
                break
            if not data.get("has_next"):
                break
        return {"result": result}

    async def get_description_category_attribute_values_search(
        self: Type["OzonCategoryAPI"],
        attribute_id: int,
        value: str,
        limit: int = 100,
    ):
        """
        Поиск значений атрибута по строке.

        :param attribute_id: Идентификатор атрибута
        :param value: Строка для поиска значения
        :param limit: Максимальное количество результатов
        :return: Результат поиска значений
        """
        return await self._request(
            method="post",
            api_version="v1",
            endpoint="description-category/attribute/values/search",
            json={
                "attribute_id": attribute_id,
                "description_category_id": self._OzonAPIBase__description_category_id,
                "language": self._OzonAPIBase__language,
                "limit": limit,
                "type_id": self.type_id,
                "value": value,
            },
        )

    async def get_full_category_info(self: Type["OzonCategoryAPI"]) -> list[dict]:
        """
        Получить полную информацию о категории, включая все поля и их значения.

        :return: Список словарей с информацией по каждому полю категории
        """
        fields_response = await self.get_description_category_attribute()
        fields = fields_response.get("result", [])
        category_info = []
        for field in fields:
            try:
                field_values = await self.get_description_category_attribute_values(
                    attribute_id=field["id"], name=field["name"]
                )
                category_field = {
                    "id": field["id"],
                    "name": field["name"],
                    "description": field["description"],
                    "values": field_values,
                    "is_required": field["is_required"],
                }
                category_info.append(category_field)
            except Exception as e:
                print(f"Error processing field {field['name']}: {e}")
                continue
        return category_info
