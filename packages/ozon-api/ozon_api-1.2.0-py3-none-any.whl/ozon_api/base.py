import sys
from types import TracebackType
from typing import Any, Literal, Optional

from aiohttp import ClientSession
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .exceptions import (
    OzonAPIClientError,
    OzonAPIConflictError,
    OzonAPIError,
    OzonAPIForbiddenError,
    OzonAPINotFoundError,
    OzonAPIServerError,
)

logger.remove()
logger.add(sys.stderr, level="INFO")


class OzonAPIBase:
    """
    Базовый класс для работы с API Ozon.
    
    Предоставляет основные методы для взаимодействия с API Ozon, включая управление сессией,
    аутентификацию и базовые HTTP-запросы.

    Attributes:
        __client_id (str): ID клиента для доступа к API
        __api_key (str): Ключ API для аутентификации
        __api_url (str): Базовый URL API Ozon
        __description_category_id (Optional[int]): ID категории описания
        __language (Literal): Язык ответов API
        __type_id (Optional[int]): ID типа товара
        __session (Optional[ClientSession]): Сессия aiohttp для выполнения запросов
    """

    __client_id: str
    __api_key: str
    __api_url: str = "https://api-seller.ozon.ru"
    __description_category_id: Optional[int] = None
    __language: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"] = "DEFAULT"
    __type_id: Optional[int] = None
    __session: Optional[ClientSession] = None

    @property
    def api_url(self) -> str:
        """
        Получить текущий URL API.

        Returns:
            str: Базовый URL API
        """
        return self.__api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        """
        Установить URL API.

        Args:
            value (str): Новый URL API

        Raises:
            ValueError: Если URL не начинается с http:// или https://
        """
        if not value.startswith("http://") and not value.startswith("https://"):
            raise ValueError("Invalid URL: must start with 'http://' or 'https://'")
        self.__api_url = value

    @property
    def description_category_id(self) -> Optional[int]:
        """
        Получить ID категории описания.

        Returns:
            Optional[int]: ID категории описания или None
        """
        return self.__description_category_id

    @description_category_id.setter
    def description_category_id(self, value: int) -> None:
        """
        Установить ID категории описания.

        Args:
            value (int): Новый ID категории описания
        """
        self.__description_category_id = value

    @property
    def language(self) -> Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"]:
        """
        Получить текущий язык API.

        Returns:
            Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"]: Текущий язык API
        """
        return self.__language

    @language.setter
    def language(
        self,
        value: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"],
    ) -> None:
        """
        Установить язык API.

        Args:
            value (Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"]): Новый язык API
        """
        self.__language = value

    @property
    def type_id(self) -> Optional[int]:
        """
        Получить ID типа товара.

        Returns:
            Optional[int]: ID типа товара или None
        """
        return self.__type_id

    @type_id.setter
    def type_id(self, value: int) -> None:
        """
        Установить ID типа товара.

        Args:
            value (int): Новый ID типа товара
        """
        self.__type_id = value

    @property
    def client_id(self) -> str:
        """
        Получить ID клиента.

        Returns:
            str: ID клиента
        """
        return self.__client_id

    @client_id.setter
    def client_id(self, value: str) -> None:
        """
        Установить ID клиента.

        Args:
            value (str): Новый ID клиента
        """
        self.__client_id = value

    @property
    def api_key(self) -> str:
        """
        Получить ключ API.

        Returns:
            str: Ключ API
        """
        return self.__api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        """
        Установить ключ API.

        Args:
            value (str): Новый ключ API
        """
        self.__api_key = value

    def __init__(self, client_id: str, api_key: str) -> None:
        """
        Инициализация клиента API Ozon.

        Args:
            client_id (str): ID клиента для доступа к API
            api_key (str): Ключ API для аутентификации
        """
        self.client_id = client_id
        self.api_key = api_key
        logger.info("Ozon API initialized successfully.")

    async def __aenter__(self) -> "OzonAPIBase":
        """
        Асинхронный контекстный менеджер для управления сессией.
        
        Создает новую сессию с необходимыми заголовками аутентификации.

        Returns:
            OzonAPIBase: Экземпляр класса с инициализированной сессией
        """
        self.__session = ClientSession(
            headers={
                "Client-Id": self.__client_id,
                "Api-Key": self.__api_key,
            }
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Закрытие сессии при выходе из контекста.

        Args:
            exc_type: Тип исключения, если оно возникло
            exc_val: Значение исключения
            exc_tb: Traceback исключения
        """
        if self.__session and not self.__session.closed:
            await self.__session.close()
            self.__session = None

    async def _get_session(self) -> ClientSession:
        """
        Получение активной сессии для выполнения запросов.

        Если сессия не создана через контекстный менеджер, создает временную сессию.
        Рекомендуется использовать класс через контекстный менеджер для лучшей производительности.

        Returns:
            ClientSession: Активная сессия aiohttp

        Note:
            При использовании временной сессии выводится предупреждение о рекомендации
            использовать контекстный менеджер.
        """
        if self.__session and not self.__session.closed:
            return self.__session

        logger.warning(
            "Using temporary session. Consider using OzonAPI as async context manager "
            "with 'async with OzonAPI(...) as api:' for better performance."
        )
        return ClientSession(
            headers={
                "Client-Id": self.__client_id,
                "Api-Key": self.__api_key,
            }
        )

    @retry(
        retry=retry_if_exception_type((OzonAPIServerError, OzonAPIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _request(
        self,
        method: Literal["post", "get", "put", "delete"] = "post",
        api_version: str = "v1",
        endpoint: str = "",
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Выполняет HTTP-запрос к API Ozon.

        Args:
            method (Literal["post", "get", "put", "delete"]): HTTP метод запроса
            api_version (str): Версия API (по умолчанию "v1")
            endpoint (str): Конечная точка API
            json (Optional[dict[str, Any]]): Данные для отправки в формате JSON

        Returns:
            dict[str, Any]: Ответ от API в формате JSON

        Raises:
            OzonAPIClientError: При ошибках клиента (400)
            OzonAPIForbiddenError: При ошибках доступа (403)
            OzonAPINotFoundError: При отсутствии ресурса (404)
            OzonAPIConflictError: При конфликте данных (409)
            OzonAPIServerError: При ошибках сервера (500)
            OzonAPIError: При прочих ошибках

        Note:
            - Автоматически закрывает временные сессии после выполнения запроса
            - При ошибках сервера (500) или общих ошибках API выполняет 3 попытки запроса
            - Между попытками делает экспоненциальную задержку от 4 до 10 секунд
        """
        url = f"{self.__api_url}/{api_version}/{endpoint}"
        log_context = {
            "method": method,
            "endpoint": endpoint,
            "api_version": api_version,
            "url": url,
            "has_payload": json is not None
        }

        logger.debug(
            "Отправка запроса к API Ozon",
            extra=log_context
        )

        session = await self._get_session()
        should_close_session = session != self.__session

        try:
            async with getattr(session, method.lower())(url, json=json) as response:
                data = await response.json()
                
                log_context.update({
                    "status_code": response.status,
                    "response_size": len(str(data))
                })
                
                if response.status >= 400:
                    code = data.get("code", response.status)
                    message = data.get("message", "Unknown error")
                    details = data.get("details", [])
                    
                    log_context.update({
                        "error_code": code,
                        "error_message": message,
                        "error_details": details
                    })
                    
                    logger.error(
                        f"Ошибка API Ozon: {message}",
                        extra=log_context
                    )
                    
                    error_map = {
                        400: OzonAPIClientError,
                        403: OzonAPIForbiddenError,
                        404: OzonAPINotFoundError,
                        409: OzonAPIConflictError,
                        500: OzonAPIServerError,
                    }
                    exc_class = error_map.get(response.status, OzonAPIError)
                    raise exc_class(code, message, details)
                
                logger.debug(
                    "Успешный ответ от API Ozon",
                    extra=log_context
                )
                return data
                
        except Exception as e:
            log_context.update({
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            logger.error(
                f"Ошибка при выполнении запроса: {str(e)}",
                extra=log_context
            )
            raise
        finally:
            if should_close_session and not session.closed:
                await session.close()
