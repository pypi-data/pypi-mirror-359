from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ProductDeleteWithoutSkuRequest:
    """Запрос на удаление товара без SKU."""
    offer_id: str

@dataclass
class ProductDeleteWithoutSkuStatus:
    """Статус удаления товара."""
    error: Optional[str]
    is_deleted: bool
    offer_id: str

@dataclass
class ProductDeleteWithoutSkuResponse:
    """Ответ на запрос удаления товара без SKU."""
    status: List[ProductDeleteWithoutSkuStatus] 