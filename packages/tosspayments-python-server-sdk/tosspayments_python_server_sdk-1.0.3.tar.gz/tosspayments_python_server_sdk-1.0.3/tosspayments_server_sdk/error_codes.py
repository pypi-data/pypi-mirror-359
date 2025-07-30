class ErrorCodes:
    """TossPayments error code constants"""

    # API KEY ERRORS
    # https://docs.tosspayments.com/reference/using-api/api-keys#api-키-에러
    INVALID_CLIENT_KEY = "INVALID_CLIENT_KEY"
    INVALID_API_KEY = "INVALID_API_KEY"
    UNAUTHORIZED_KEY = "UNAUTHORIZED_KEY"
    INCORRECT_BASIC_AUTH_FORMAT = "INCORRECT_BASIC_AUTH_FORMAT"

    class Groups:
        """Error code groups"""

        AUTH = {
            "INVALID_CLIENT_KEY",  # 400
            "INVALID_API_KEY",  # 400
            "UNAUTHORIZED_KEY",  # 401
            "INCORRECT_BASIC_AUTH_FORMAT",  # 401
        }

    @classmethod
    def is_auth_error(cls, error_code: str) -> bool:
        return error_code in cls.Groups.AUTH
