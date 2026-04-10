from rest_framework.response import Response

def success_response(data=None, message="success", code=0, status=200):
    return Response({
        "code": code,
        "message": message,
        "data": data if data is not None else {}
    }, status=status)

def error_response(message="error", code=500, data=None, status=400):
    return Response({
        "code": code,
        "message": message,
        "data": data if data is not None else {}
    }, status=status)
