from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ProductInfoAttributesFilter(BaseModel):
    offer_id: Optional[List[str]] = Field(
        None, description="Артикулы товаров (offer_id)"
    )
    product_id: Optional[List[int]] = Field(None, description="ID товаров (product_id)")
    sku: Optional[List[int]] = Field(None, description="SKU товаров (sku)")
    visibility: Optional[str] = Field(
        None, description="Видимость товара (ALL, VISIBLE, INVISIBLE)"
    )


class ProductInfoAttributesRequest(BaseModel):
    filter: ProductInfoAttributesFilter = Field(..., description="Фильтр товаров")
    last_id: Optional[str] = Field(
        None, description="Идентификатор последнего значения на странице"
    )
    limit: Optional[int] = Field(
        1000, description="Количество значений на странице (1-1000)"
    )
    sort_by: Optional[Literal["sku", "offer_id", "id", "title"]] = Field(
        None, description="Параметр сортировки"
    )
    sort_dir: Optional[Literal["asc", "desc"]] = Field(
        None, description="Направление сортировки"
    )


class ProductInfoAttributesValue(BaseModel):
    dictionary_value_id: Optional[int] = Field(
        None, description="Идентификатор характеристики в словаре"
    )
    value: Optional[str] = Field(None, description="Значение характеристики товара")


class ProductInfoAttributesComplexAttribute(BaseModel):
    id: Optional[int] = Field(None, description="Идентификатор характеристики")
    complex_id: Optional[int] = Field(
        None,
        description="Идентификатор характеристики, поддерживающей вложенные свойства",
    )
    values: Optional[List[ProductInfoAttributesValue]] = Field(
        default_factory=list, description="Массив значений характеристики"
    )
    depth: Optional[int] = Field(None, description="Глубина")


class ProductInfoAttributesAttribute(BaseModel):
    id: Optional[int] = Field(None, description="Идентификатор характеристики")
    complex_id: Optional[int] = Field(
        None,
        description="Идентификатор характеристики, поддерживающей вложенные свойства",
    )
    values: Optional[List[ProductInfoAttributesValue]] = Field(
        default_factory=list, description="Массив значений характеристики"
    )


class ProductInfoAttributesPdfFile(BaseModel):
    file_name: Optional[str] = Field(None, description="Путь к PDF-файлу")
    name: Optional[str] = Field(None, description="Название файла")


class ProductInfoAttributesModelInfo(BaseModel):
    model_id: Optional[int] = Field(None, description="Идентификатор модели")
    count: Optional[int] = Field(
        None, description="Количество объединённых товаров модели"
    )


class ProductInfoAttributesResultItem(BaseModel):
    attributes: Optional[List[ProductInfoAttributesAttribute]] = Field(
        default_factory=list, description="Список характеристик товара"
    )
    attributes_with_defaults: Optional[List[int]] = Field(
        default_factory=list,
        description="Список ID характеристик со значением по умолчанию",
    )
    barcode: Optional[str] = Field(None, description="Штрихкод")
    barcodes: Optional[List[str]] = Field(
        default_factory=list, description="Все штрихкоды товара"
    )
    description_category_id: Optional[int] = Field(
        None, description="ID категории описания"
    )
    color_image: Optional[str] = Field(None, description="Маркетинговый цвет")
    complex_attributes: Optional[List[ProductInfoAttributesComplexAttribute]] = Field(
        default_factory=list, description="Массив вложенных характеристик"
    )
    dimension_unit: Optional[str] = Field(
        None, description="Единица измерения габаритов"
    )
    height: Optional[int] = Field(None, description="Высота упаковки")
    id: Optional[int] = Field(None, description="ID товара (product_id)")
    images: Optional[List[str]] = Field(
        default_factory=list, description="Ссылки на изображения товара"
    )
    model_info: Optional[ProductInfoAttributesModelInfo] = Field(
        None, description="Информация о модели"
    )
    name: Optional[str] = Field(None, description="Название товара")
    offer_id: Optional[str] = Field(None, description="Артикул товара")
    pdf_list: Optional[List[ProductInfoAttributesPdfFile]] = Field(
        default_factory=list, description="Массив PDF-файлов"
    )
    primary_image: Optional[str] = Field(
        None, description="Ссылка на главное изображение товара"
    )
    sku: Optional[str] = Field(None, description="SKU товара")
    type_id: Optional[int] = Field(None, description="ID типа товара")
    weight: Optional[int] = Field(None, description="Вес товара в упаковке")
    weight_unit: Optional[str] = Field(None, description="Единица измерения веса")
    width: Optional[int] = Field(None, description="Ширина упаковки")
    last_id: Optional[str] = Field(
        None, description="Идентификатор последнего значения на странице"
    )
    total: Optional[int] = Field(None, description="Количество товаров в списке")


class ProductInfoAttributesResult(BaseModel):
    result: List[ProductInfoAttributesResultItem] = Field(
        default_factory=list, description="Результаты запроса"
    )
