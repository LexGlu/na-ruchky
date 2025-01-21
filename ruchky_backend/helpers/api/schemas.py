from ninja import Schema


class BaseResponse(Schema):
    message: str
