from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from validators import UserRequest, UserResponse

from db import get_db
from tables import User



app = FastAPI() 
@app.get("/health-check")
def health_check():
    return {"status": "ok",
            "service": "FastAPI",
            "message": "Service is running smoothly"
            }


@app.get("/users/{user_id}" ,response_model=UserResponse)
def get_user_details(user_id: int, db: Session = Depends(get_db)):
    with db.begin() :
        user = db.get(User , user_id)
        if user is None:
            return {"error": "User not found"}
        return user
        
        
    
@app.post("/users", response_model=UserResponse)
def create_user(user : UserRequest, db : Session = Depends(get_db)):
    with db.begin() :
        
        new_user = User( name=user.name, email=user.email)
        db.add(new_user)
        db.flush()  # Flush to get the new user's ID
        db.refresh(new_user)
        return new_user

    
    
    
    
@app.put("/users/{user_id}" ,response_model=UserResponse)
def update_user(user_id : int ,updated_user : UserRequest, db : Session = Depends(get_db)):
    with db.begin() :
        old_user = db.get(User , user_id)
        if old_user is None:
            return {"error": "User not found"}
        old_user.name = updated_user.name
        old_user.email = updated_user.email
        
        return old_user

    
    
    
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    with db.begin() :
        user = db.get(User , user_id)
        if user is None:
            return {"error": "User not found"}
        db.delete(user)
        
        return {"message": "User deleted successfully"}