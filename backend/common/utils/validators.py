def validate_code(value: str):
    if not value:
        raise ValueError("编码不能为空")
