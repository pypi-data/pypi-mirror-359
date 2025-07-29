import sys
from types import TracebackType
from typing import Any, Literal, Optional

from aiohttp import ClientSession
from loguru import logger

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
    __client_id: str
    __api_key: str
    __api_url: str = "https://api-seller.ozon.ru"
    __description_category_id: Optional[int] = None
    __language: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"] = "DEFAULT"
    __type_id: Optional[int] = None
    __session: Optional[ClientSession] = None

    @property
    def api_url(self) -> str:
        return self.__api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        if not value.startswith("http://") and not value.startswith("https://"):
            raise ValueError("Invalid URL: must start with 'http://' or 'https://'")
        self.__api_url = value

    @property
    def description_category_id(self) -> Optional[int]:
        return self.__description_category_id

    @description_category_id.setter
    def description_category_id(self, value: int) -> None:
        self.__description_category_id = value

    @property
    def language(self) -> Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"]:
        return self.__language

    @language.setter
    def language(
        self,
        value: Literal["DEFAULT", "RU", "EN", "TR", "ZH_HANS"],
    ) -> None:
        self.__language = value

    @property
    def type_id(self) -> Optional[int]:
        return self.__type_id

    @type_id.setter
    def type_id(self, value: int) -> None:
        self.__type_id = value

    @property
    def client_id(self) -> str:
        return self.__client_id

    @client_id.setter
    def client_id(self, value: str) -> None:
        self.__client_id = value

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        self.__api_key = value

    def __init__(self, client_id: str, api_key: str) -> None:
        self.client_id = client_id
        self.api_key = api_key
        logger.info("Ozon API initialized successfully.")

    async def __aenter__(self) -> "OzonAPIBase":
        """Асинхронный контекстный менеджер для управления сессией"""
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
        """Закрытие сессии при выходе из контекста"""
        if self.__session and not self.__session.closed:
            await self.__session.close()
            self.__session = None

    async def _get_session(self) -> ClientSession:
        """Получение сессии. Если сессия не создана, создает временную"""
        if self.__session and not self.__session.closed:
            return self.__session

        # Если сессия не создана (не используется контекстный менеджер),
        # создаем временную сессию для обратной совместимости
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

    async def _request(
        self,
        method: Literal["post", "get", "put", "delete"] = "post",
        api_version: str = "v1",
        endpoint: str = "",
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = f"{self.__api_url}/{api_version}/{endpoint}"

        session = await self._get_session()
        should_close_session = (
            session != self.__session
        )  # Закрываем только временные сессии

        try:
            async with getattr(session, method.lower())(url, json=json) as response:
                data = await response.json()
                if response.status >= 400:
                    code = data.get("code", response.status)
                    message = data.get("message", "Unknown error")
                    details = data.get("details", [])
                    error_map = {
                        400: OzonAPIClientError,
                        403: OzonAPIForbiddenError,
                        404: OzonAPINotFoundError,
                        409: OzonAPIConflictError,
                        500: OzonAPIServerError,
                    }
                    exc_class = error_map.get(response.status, OzonAPIError)
                    raise exc_class(code, message, details)
                return data
        finally:
            if should_close_session and not session.closed:
                await session.close()
