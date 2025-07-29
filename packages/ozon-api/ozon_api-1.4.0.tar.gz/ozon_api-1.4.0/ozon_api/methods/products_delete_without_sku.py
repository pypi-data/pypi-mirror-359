from typing import List

from ..core import BaseMethod
from ..models.products_delete_without_sku import (
    ProductDeleteWithoutSkuRequest,
    ProductDeleteWithoutSkuResponse
)


class ProductsDeleteWithoutSku(BaseMethod):
    """Метод для удаления товаров без SKU из архива."""

    def __init__(self):
        """Инициализация метода."""
        super().__init__()
        self.url = '/v2/products/delete'
        self.method = 'POST'
        self.response_type = ProductDeleteWithoutSkuResponse

    def build_request_params(
            self,
            products: List[ProductDeleteWithoutSkuRequest]
    ) -> dict:
        """
        Построение параметров запроса.

        Args:
            products: Список товаров для удаления

        Returns:
            dict: Параметры запроса
        """
        return {
            'products': [
                {'offer_id': product.offer_id}
                for product in products
            ]
        } 