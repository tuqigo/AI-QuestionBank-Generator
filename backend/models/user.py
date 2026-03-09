from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: str
    password: str
    code: str  # 注册验证码


class UserLogin(BaseModel):
    email: str
    password: str


class UserInDB(BaseModel):
    id: int
    email: str
    hashed_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmailOtpRequest(BaseModel):
    email: str
    purpose: str = "register"  # register 或 reset_password


class EmailLoginRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str
