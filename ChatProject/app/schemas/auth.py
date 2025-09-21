from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterData(BaseModel):
    email: str
    password: str