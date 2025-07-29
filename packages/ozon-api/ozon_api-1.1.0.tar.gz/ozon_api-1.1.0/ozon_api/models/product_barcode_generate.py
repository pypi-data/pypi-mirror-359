from typing import List

from pydantic import BaseModel, Field


class ProductBarcodeGenerateRequest(BaseModel):
    product_ids: List[str] = Field(
        ..., description="Идентификаторы товаров, для которых нужно создать штрихкод"
    )


class ProductBarcodeGenerateError(BaseModel):
    code: str = Field(..., description="Код ошибки")
    error: str = Field(..., description="Описание ошибки")
    barcode: str = Field(
        ..., description="Штрихкод, при создании которого произошла ошибка"
    )
    product_id: int = Field(
        ...,
        description="Идентификатор товара, для которого не удалось создать штрихкод",
    )


class ProductBarcodeGenerateResponse(BaseModel):
    errors: List[ProductBarcodeGenerateError] | None = Field(
        default_factory=list, description="Ошибки при создании штрихкода"
    )
