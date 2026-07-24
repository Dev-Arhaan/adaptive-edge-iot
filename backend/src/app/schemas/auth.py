from pydantic import BaseModel


class LoginRequest(BaseModel):
    passphrase: str


class LoginResponse(BaseModel):
    token: str