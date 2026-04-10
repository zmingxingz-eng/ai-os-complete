class BusinessException(Exception):
    def __init__(self, message="业务异常", code=400):
        self.message = message
        self.code = code
        super().__init__(message)
