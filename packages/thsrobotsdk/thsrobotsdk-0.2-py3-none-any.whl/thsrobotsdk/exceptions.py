class ThsrobotSDKError(Exception):
    """THSRobotSDK 的基础异常类。"""
    pass

class RequestError(ThsrobotSDKError):
    """HTTP 请求出错时抛出的异常。"""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Request failed with status {status_code}: {message}")
