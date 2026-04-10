from rest_framework.views import exception_handler
from common.exceptions.base import BusinessException
from common.responses.response import error_response

def custom_exception_handler(exc, context):
    if isinstance(exc, BusinessException):
        return error_response(message=exc.message, code=exc.code, status=400)
    response = exception_handler(exc, context)
    if response is not None:
        return error_response(message="request failed", code=response.status_code, data=response.data, status=response.status_code)
    return error_response(message="internal server error", code=500, status=500)
