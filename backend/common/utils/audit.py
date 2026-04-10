from functools import wraps
from apps.system.audit_log.services import AuditLogService

def audit_action(action: str, target: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = args[1] if len(args) > 1 else None
            response = func(*args, **kwargs)
            operator = getattr(request, "user", None) if request is not None else None
            if operator is not None and getattr(operator, "is_authenticated", False):
                AuditLogService.write_log(
                    action=action,
                    target=target,
                    content=f"{action}:{target}",
                    operator=operator,
                )
            return response
        return wrapper
    return decorator
