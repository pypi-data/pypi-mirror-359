from ..core import BaseMethod
from ..models.upload_digital_codes_info import (
    UploadDigitalCodesInfoRequest,
    UploadDigitalCodesInfoResponse,
)


class UploadDigitalCodesInfo(BaseMethod):
    """Метод для получения статуса загрузки кодов активации"""

    def __init__(self):
        super().__init__()
        self.url = "/v1/product/upload_digital_codes/info"
        self.method = "POST"
        self.request_type = UploadDigitalCodesInfoRequest
        self.response_type = UploadDigitalCodesInfoResponse

    def run(self, task_id: int) -> UploadDigitalCodesInfoResponse:
        """
        Запрос статуса загрузки кодов активации

        :param task_id: Идентификатор задачи на загрузку кодов активации
        :return: Ответ с информацией о статусе загрузки
        """
        return self._run(UploadDigitalCodesInfoRequest(task_id=task_id)) 