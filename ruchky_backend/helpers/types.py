from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber


class PhoneNumber(PydanticPhoneNumber):
    default_region_code = "IN"
    phone_format = "E164"
