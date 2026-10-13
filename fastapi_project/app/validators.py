from pydantic import BaseModel, EmailStr



class UserRequest(BaseModel):
    
    name: str
    email: EmailStr
    
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}
    # class Config:
    #     orm_mode = True