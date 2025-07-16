from fastapi import HTTPException, status


class InvalidCredentials(HTTPException):
    def __init__(self, detail: str = "Invalid Credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InsufficientPermission(HTTPException):
    def __init__(self, detail: str = "Insufficient permission"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
