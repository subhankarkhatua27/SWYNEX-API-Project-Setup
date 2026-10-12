from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session

from db import get_db
from tables import User

app = FastAPI() 
@app.get("/health-check")
def health_check():
    return {"status": "ok",
            "service": "FastAPI",
            "message": "Service is running smoothly"
            }


@app.get("/users")
def get_user_details(db : Session = Depends(get_db)):
    pass
    
    



@app.post("/users/{user_id}")
def create_user(db : Session = Depends(get_db)):
    pass
    
    
    
    
@app.put("/users/{user_id}")
def update_user(db : Session = Depends(get_db)):
    pass
    
    
    
    
    
@app.delete("/users/{user_id}")
def delete_user(db : Session = Depends(get_db)):
    pass