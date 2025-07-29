# Python Ozon Seller API

[![PyPI version](https://img.shields.io/pypi/v/ozon-api)](https://pypi.org/project/ozon-api/) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Downloads](https://img.shields.io/pypi/dm/ozon-api)](https://pypi.org/project/ozon-api/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Асинхронная Python библиотека для работы с API Ozon Seller.

## Особенности

- ✨ Полностью асинхронная работа с API
- 🛡️ Строгая типизация данных с использованием Pydantic моделей
- 🚀 Простой и понятный интерфейс
- 📦 Поддержка всех основных методов API Ozon Seller

## Установка

```bash
pip install ozon-api
```

## Быстрый старт

```python
from ozon_api import OzonAPI
import asyncio

async def main():
    async with OzonAPI(client_id="your_client_id", api_key="your_api_key") as api:
        # Получение списка товаров
        products = await api.product_list(...)
        print(products)

if __name__ == "__main__":
    asyncio.run(main())
```

## Основные возможности

### Работа с товарами

- Получение списка товаров
- Импорт товаров
- Обновление товаров
- Работа с изображениями товаров
- Генерация и добавление штрихкодов
- Управление архивом товаров
- Получение рейтингов товаров

### Работа с категориями

- Получение дерева категорий
- Получение атрибутов категорий

## Документация

### Инициализация клиента

```python
from ozon_api import OzonAPI

# Рекомендуемый способ (с использованием контекстного менеджера)
async with OzonAPI(client_id="your_client_id", api_key="your_api_key") as api:
    # Ваш код здесь
    pass

# Альтернативный способ
api = OzonAPI(client_id="your_client_id", api_key="your_api_key")
```

### Настройка клиента

```python
api.api_url = "https://api-seller.ozon.ru"  # Изменение базового URL API
api.language = "RU"  # Установка языка (доступны: DEFAULT, RU, EN, TR, ZH_HANS)
```

### Обработка ошибок

Библиотека предоставляет следующие типы исключений:

- `OzonAPIError` - базовое исключение
- `OzonAPIClientError` - ошибка клиента (400)
- `OzonAPIForbiddenError` - ошибка доступа (403)
- `OzonAPINotFoundError` - ресурс не найден (404)
- `OzonAPIConflictError` - конфликт (409)
- `OzonAPIServerError` - ошибка сервера (500)

```python
try:
    await api.product_list(...)
except OzonAPIClientError as e:
    print(f"Ошибка клиента: {e.message}")
except OzonAPIError as e:
    print(f"Общая ошибка: {e.message}")
```

## Примеры использования

### Получение списка товаров

```python
from ozon_api.models.product_list import ProductListRequest

request = ProductListRequest(
    page=1,
    page_size=100
)
response = await api.product_list(request)
```

### Импорт товаров

```python
from ozon_api.models.product_import import ProductImportRequest

request = ProductImportRequest(
    items=[...]  # Список товаров для импорта
)
response = await api.product_import(request)
```

### Работа с изображениями

```python
from ozon_api.models.product_pictures import ProductPicturesRequest

request = ProductPicturesRequest(
    product_id="...",
    images=[...]
)
response = await api.product_pictures(request)
```

## Внеси вклад в проект

Мы рады любым улучшениям и pull request'ам! Вот как вы можете помочь:

### Процесс внесения изменений

1. Форкните репозиторий
2. Создайте ветку для вашей фичи:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Внесите изменения и добавьте тесты
4. Убедитесь, что код соответствует стандартам:
   ```bash
   ruff check --fix
   isort .
   black .
   ```
5. Закоммитьте изменения:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
6. Отправьте изменения в ваш форк:
   ```bash
   git push origin feature/amazing-feature
   ```
7. Создайте Pull Request

### Правила контрибуции

- Используйте [Conventional Commits](https://www.conventionalcommits.org/) для сообщений коммитов
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости
- Следуйте существующему стилю кода
- Один PR - одно изменение

### Сообщение о багах

Если вы нашли баг, пожалуйста, создайте issue с подробным описанием:

- Версия библиотеки
- Версия Python
- Ожидаемое поведение
- Текущее поведение
- Шаги для воспроизведения

## Лицензия

MIT

## Автор

Создано с ❤️ [Mephistofx](https://github.com/mephistofox)

Telegram: [@mephistofx](https://t.me/mephistofx)  
Email: dev@fxcode.ru

## Поддержка

Если у вас возникли вопросы или проблемы, пожалуйста, создайте issue в репозитории проекта.

## Версионирование

Проект использует семантическое версионирование (SemVer):
- MAJOR версия: несовместимые изменения API
- MINOR версия: новая функциональность с обратной совместимостью
- PATCH версия: исправления ошибок с обратной совместимостью
