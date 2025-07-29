from .import_by_sku import ImportBySku, ImportBySku_Item
from .product_archive import (
    ProductArchiveRequest,
    ProductArchiveResponse,
    ProductUnarchiveRequest,
    ProductUnarchiveResponse,
)
from .product_attributes_update import (
    ProductAttributesUpdate,
    ProductAttributesUpdate_Item,
    ProductAttributesUpdate_Item_Attribute,
    ProductAttributesUpdate_Item_Attribute_Value,
)
from .product_barcode_add import (
    ProductBarcodeAddError,
    ProductBarcodeAddItem,
    ProductBarcodeAddRequest,
    ProductBarcodeAddResponse,
)
from .product_barcode_generate import (
    ProductBarcodeGenerateError,
    ProductBarcodeGenerateRequest,
    ProductBarcodeGenerateResponse,
)
from .product_import_info import (
    ProductImportInfo,
    ProductPicturesInfoRequest,
    ProductPicturesInfoResponse,
    ProductPicturesInfoResponseItem,
)
from .product_info_attributes import (
    ProductInfoAttributesRequest,
    ProductInfoAttributesResult,
)
from .product_info_list import (
    ProductInfoListRequest,
    ProductInfoListResponse,
)
from .product_list import (
    ProductListFilter,
    ProductListItem,
    ProductListRequest,
    ProductListResponse,
)
from .product_pictures_info import (
    ProductPicturesInfoErrorV2,
    ProductPicturesInfoItemV2,
    ProductPicturesInfoRequestV2,
    ProductPicturesInfoResponseV2,
)
from .product_rating import ProductRatingRequest, ProductRatingResponse
from .product_related_sku import (
    ProductRelatedSkuError,
    ProductRelatedSkuItem,
    ProductRelatedSkuRequest,
    ProductRelatedSkuResponse,
)
from .product_subscription import (
    ProductSubscriptionItem,
    ProductSubscriptionRequest,
    ProductSubscriptionResponse,
)
from .product_update_offer_id import (
    ProductUpdateOfferIdError,
    ProductUpdateOfferIdItem,
    ProductUpdateOfferIdRequest,
    ProductUpdateOfferIdResponse,
)
from .products_delete import (
    ProductDeleteItem,
    ProductsDeleteRequest,
    ProductsDeleteResponse,
    ProductsDeleteStatusItem,
)
from .upload_digital_codes import (
    UploadDigitalCodesInfoRequest,
    UploadDigitalCodesInfoResponse,
    UploadDigitalCodesInfoResponseResult,
    UploadDigitalCodesRequest,
    UploadDigitalCodesResponse,
    UploadDigitalCodesResponseResult,
)

from .category_attribute import CategoryAttributeItem, CategoryAttributeResponse
from .category_tree import CategoryTreeItem, CategoryTreeResponse

from .product_subscription import *
from .product_update_offer_id import *
from .products_delete_without_sku import *
from .upload_digital_codes_info import *

__all__ = [
    "ImportBySku",
    "ImportBySku_Item",
    "ProductAttributesUpdate_Item_Attribute_Value",
    "ProductAttributesUpdate_Item_Attribute",
    "ProductAttributesUpdate_Item",
    "ProductAttributesUpdate",
    "ProductImportInfo",
    "ProductPicturesInfoRequest",
    "ProductPicturesInfoResponseItem",
    "ProductPicturesInfoResponse",
    "ProductListRequest",
    "ProductListFilter",
    "ProductListResponse",
    "ProductListItem",
    "ProductRatingRequest",
    "ProductRatingResponse",
    "ProductUpdateOfferIdRequest",
    "ProductUpdateOfferIdResponse",
    "ProductUpdateOfferIdItem",
    "ProductUpdateOfferIdError",
    "ProductArchiveRequest",
    "ProductArchiveResponse",
    "ProductUnarchiveRequest",
    "ProductUnarchiveResponse",
    "ProductsDeleteRequest",
    "ProductsDeleteResponse",
    "ProductDeleteItem",
    "ProductsDeleteStatusItem",
    "UploadDigitalCodesRequest",
    "UploadDigitalCodesResponse",
    "UploadDigitalCodesResponseResult",
    "UploadDigitalCodesInfoRequest",
    "UploadDigitalCodesInfoResponse",
    "UploadDigitalCodesInfoResponseResult",
    "CategoryTreeResponse",
    "CategoryTreeItem",
    "CategoryAttributeResponse",
    "CategoryAttributeItem",
    "ProductSubscriptionRequest",
    "ProductSubscriptionItem",
    "ProductSubscriptionResponse",
    "ProductRelatedSkuRequest",
    "ProductRelatedSkuItem",
    "ProductRelatedSkuError",
    "ProductRelatedSkuResponse",
    "ProductPicturesInfoRequestV2",
    "ProductPicturesInfoItemV2",
    "ProductPicturesInfoErrorV2",
    "ProductPicturesInfoResponseV2",
    "ProductBarcodeAddRequest",
    "ProductBarcodeAddResponse",
    "ProductBarcodeAddItem",
    "ProductBarcodeAddError",
    "ProductBarcodeGenerateRequest",
    "ProductBarcodeGenerateResponse",
    "ProductBarcodeGenerateError",
    "ProductInfoAttributesRequest",
    "ProductInfoAttributesResult",
    "ProductInfoListRequest",
    "ProductInfoListResponse",
    "ProductsDeleteWithoutSkuRequest",
    "ProductsDeleteWithoutSkuResponse",
    "UploadDigitalCodesInfoRequest",
    "UploadDigitalCodesInfoResponse",
    "UploadDigitalCodesInfoResult",
]
