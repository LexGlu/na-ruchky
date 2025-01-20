from ninja import Schema


class BaseResponse(Schema):
    message: str


class CSRFTokenResponse(Schema):
    csrf_token: str
