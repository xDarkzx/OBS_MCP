from enum import IntEnum


class ErrorCode(IntEnum):
    # Connection errors (1000s)
    CONNECTION_FAILED = 1000
    CONNECTION_REFUSED = 1001
    AUTH_FAILED = 1002

    # Request errors (2000s)
    REQUEST_FAILED = 2000
    RESOURCE_NOT_FOUND = 2001

    # Validation errors (3000s)
    VALIDATION_FAILED = 3000
    INVALID_PARAMETER = 3001
    MISSING_PARAMETER = 3002
    VALUE_OUT_OF_RANGE = 3003


class OBSMCPError(Exception):
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code.name} ({code.value})] {message}")
