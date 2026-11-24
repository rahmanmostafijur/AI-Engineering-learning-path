from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    email: str


class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    role: str
    content: str