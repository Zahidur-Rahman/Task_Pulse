from pydantic import EmailStr, Field, BaseModel

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class ShowUser(BaseModel):
    id: int
    email: EmailStr
    # is_active: bool

    class Config:
        
        orm_mode = True
        
class UserResponse(ShowUser):
    pass
    class Config:
        orm_mode = True       

