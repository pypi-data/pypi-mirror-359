# Changelog

## [0.2.1]
### Added
- Реализованы методы для работы с категориями описаний:
  - get_description_category_tree
  - get_description_category_attribute
  - get_description_category_attribute_values
  - get_description_category_attribute_values_search
  - get_full_category_info
- Реализованы методы для импорта и управления товарами:
  - product_import
  - product_import_info
  - product_import_by_sku
  - product_attributes_update
  - products_delete
  - upload_digital_codes
  - upload_digital_codes_info
- Реализованы методы для работы с изображениями товаров:
  - product_pictures_import
  - product_pictures_info
  - product_pictures_info_v2
- Реализованы методы для работы со штрихкодами:
  - product_barcode_add
  - product_barcode_generate
- Реализованы методы для подписки и получения информации о товарах:
  - product_subscription
  - product_list
  - product_info_limit
  - product_info_attributes
  - product_info_list
- Реализованы методы для обновления и архивации товаров:
  - product_update_offer_id
  - product_archive
  - product_unarchive
- Реализованы методы для получения связанных SKU и рейтинга товаров:
  - product_related_sku
  - product_rating_by_sku
