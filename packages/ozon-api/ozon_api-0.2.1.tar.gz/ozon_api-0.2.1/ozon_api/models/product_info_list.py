from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorLevel(str, Enum):
    UNSPECIFIED = "ERROR_LEVEL_UNSPECIFIED"
    ERROR = "ERROR_LEVEL_ERROR"
    WARNING = "ERROR_LEVEL_WARNING"
    INTERNAL = "ERROR_LEVEL_INTERNAL"


class ColorIndex(str, Enum):
    UNSPECIFIED = "COLOR_INDEX_UNSPECIFIED"
    WITHOUT_INDEX = "COLOR_INDEX_WITHOUT_INDEX"
    GREEN = "COLOR_INDEX_GREEN"
    YELLOW = "COLOR_INDEX_YELLOW"
    RED = "COLOR_INDEX_RED"


class ShipmentType(str, Enum):
    UNSPECIFIED = "SHIPMENT_TYPE_UNSPECIFIED"
    GENERAL = "SHIPMENT_TYPE_GENERAL"
    BOX = "SHIPMENT_TYPE_BOX"
    PALLET = "SHIPMENT_TYPE_PALLET"


class ProductInfoListRequest(BaseModel):
    offer_id: Optional[List[str]] = Field(
        None, description="Идентификаторы товаров в системе продавца — артикулы."
    )
    product_id: Optional[List[int]] = Field(
        None, description="Идентификаторы товаров в системе продавца — product_id."
    )
    sku: Optional[List[int]] = Field(
        None, description="Идентификаторы товаров в системе Ozon — SKU."
    )


class ProductInfoListError(BaseModel):
    attribute_id: Optional[int]
    code: Optional[str]
    field: Optional[str]
    level: Optional[ErrorLevel]
    state: Optional[str]
    texts: Optional[Dict[str, Any]]


class ProductInfoListCommission(BaseModel):
    delivery_amount: Optional[float]
    percent: Optional[float]
    return_amount: Optional[float]
    sale_schema: Optional[str]
    value: Optional[float]
    currency_code: Optional[str]


class ProductInfoListStockStatus(BaseModel):
    present: Optional[int]
    reserved: Optional[int]
    sku: Optional[int]
    source: Optional[str]


class ProductInfoListStocks(BaseModel):
    has_stock: Optional[bool]
    stocks: Optional[List[ProductInfoListStockStatus]]


class ProductInfoListVisibilityDetails(BaseModel):
    has_price: Optional[bool]
    has_stock: Optional[bool]


class ProductInfoListItem(BaseModel):
    barcodes: Optional[List[str]]
    color_image: Optional[List[str]]
    commissions: Optional[List[ProductInfoListCommission]]
    created_at: Optional[str]
    currency_code: Optional[str]
    description_category_id: Optional[int]
    discounted_fbo_stocks: Optional[int]
    errors: Optional[List[ProductInfoListError]]
    has_discounted_fbo_item: Optional[bool]
    id: Optional[int]
    images: Optional[List[str]]
    images360: Optional[List[str]]
    is_archived: Optional[bool]
    is_autoarchived: Optional[bool]
    is_discounted: Optional[bool]
    is_kgt: Optional[bool]
    is_prepayment_allowed: Optional[bool]
    is_super: Optional[bool]
    marketing_price: Optional[str]
    min_price: Optional[str]
    model_info: Optional[Dict[str, Any]]
    name: Optional[str]
    offer_id: Optional[str]
    old_price: Optional[str]
    price: Optional[str]
    price_indexes: Optional[Dict[str, Any]]
    color_index: Optional[ColorIndex]
    external_index_data: Optional[Dict[str, Any]]
    ozon_index_data: Optional[Dict[str, Any]]
    self_marketplaces_index_data: Optional[Dict[str, Any]]
    primary_image: Optional[List[str]]
    sources: Optional[List[Dict[str, Any]]]
    quant_code: Optional[str]
    shipment_type: Optional[ShipmentType]
    sku: Optional[int]
    source: Optional[str]
    statuses: Optional[Dict[str, Any]]
    is_created: Optional[bool]
    moderate_status: Optional[str]
    status: Optional[str]
    status_description: Optional[str]
    status_failed: Optional[str]
    status_name: Optional[str]
    status_tooltip: Optional[str]
    status_updated_at: Optional[str]
    validation_status: Optional[str]
    stocks: Optional[ProductInfoListStocks]
    type_id: Optional[int]
    updated_at: Optional[str]
    vat: Optional[str]
    visibility_details: Optional[ProductInfoListVisibilityDetails]
    volume_weight: Optional[float]


class ProductInfoListResponse(BaseModel):
    items: List[ProductInfoListItem] = Field(
        default_factory=list, description="Массив данных о товарах."
    )
