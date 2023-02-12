class VkApiError(Exception):
    """
    Исключение, вызывается если VK API вернул ошибку в ответе
    """

    def __init__(self, error):
        self.error = error
        self.error_code = error.get("error_code")
        self.error_msg = error.get("error_msg")
        self.request_params = error.get("request_params")
        self.captcha_sid = error.get("captcha_sid")
        self.captcha_img = error.get("captcha_img")

    def __str__(self):
        return f"[{self.error_code}] {self.error_msg}"

    def __repr__(self):
        return f"[{self.error_code}] {self.error_msg}"


# class Captcha(VkApiError):
#     def __init__(self, ):


class VkaError(Exception): ...