class VkApiError(Exception):
    """
    Исключение, вызывается если VK API вернул ошибку в ответе
    """

    def __init__(self, error):
        self.error_code = error.get("error_code")
        self.error_msg = error.get("error_msg")
        self.request_params = error.get("request_params")

    def __str__(self):
        return f"[{self.error_code}] {self.error_msg}"
