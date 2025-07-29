from dataclasses import dataclass
from typing import Optional

from ..core import BaseModel


@dataclass
class UploadDigitalCodesInfoResult:
    """Результат проверки статуса загрузки цифровых кодов"""
    status: str


@dataclass
class UploadDigitalCodesInfoResponse(BaseModel):
    """Ответ на запрос статуса загрузки цифровых кодов"""
    result: UploadDigitalCodesInfoResult


@dataclass
class UploadDigitalCodesInfoRequest(BaseModel):
    """Запрос статуса загрузки цифровых кодов"""
    task_id: int 