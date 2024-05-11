from fastapi import FastAPI , Body
from pydantic import BaseModel
import requests
from typing import Annotated 

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.db import fake_users_db

from fastapi.middleware.cors import CORSMiddleware
origins = [ "*"]

from backend import  tasks_router

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
app.include_router(tasks_router.router)
app.add_middleware(CORSMiddleware,     
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get("/secure_endpoint")
def secure_endpoint(
    token: Annotated[str, Depends(oauth_scheme)]
):
    return token

class User(BaseModel):
    email: str 
    username: str = lambda : email
    name: str 
    password: str 
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    for identity in db:
        if db[identity]["username"] == username:
            return UserInDB(**db[identity])

def fake_decode_token(token):
    print("token is : ", token)
    user = get_user(fake_users_db, token)

    return user 

def password_hash(password: str):
    return "fakehashed-" + password

async def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Authentication Credentials",
            headers = {"www-Authenticate": "Bearer"}
        )
    return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):  
    
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user



@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)

    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    user = UserInDB(**user_dict)
    hashed_password = password_hash(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or passwrod ")
    return {"access_token": user.username, "token_type": "bearer"}
    


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

### Register User
database_creds = {
"X-Parse-Application-Id" : "X-Parse-Application-Id",
"X-Parse-REST-API-Key" : "X-Parse-REST-API-Key"
}

@app.post("/register_user", status_code=201)
async def register_user(user_info : User):
    back4app_class = "User"
    headers = database_creds
    post_data = {
        "name": user_info.name,
        "email": user_info.email,
        "password": password_hash(user_info.password)
    }
    url = "https://parseapi.back4app.com/classes/" + back4app_class
    resp = requests.post(url, data=post_data, headers=headers)
    
    if resp.status_code == 201:
        return {"user_registration_status": "created",
                "status_code": resp.status_code,
                "response_data": resp.content
                }
    else:
        return {
            "registration_status": "failed",
            "status_code": resp.status_code,
            "response_data": resp.content,
        }
    
@app.post("/login")
async def user_login(email: Annotated[str, Body()], password: Annotated[str, Body()]):
    back4app_class = "User"
    headers = database_creds

    params = {"where": '{"email":"%s", "password":"%s"}' %(email, password_hash(password))}
    url = "https://parseapi.back4app.com/classes/" + back4app_class
    print(params)
    resp = requests.get(url, headers=headers, params=params)
    print("response is : ", resp)
    if resp.status_code == 200 and len(resp.json()["results"])>0:
        print(resp.content)
        return {"logged": True,
                "status_code": resp.status_code,
                "response_data": resp.content
                }
    else:
        raise HTTPException(status_code=400, detail="Incorrect UserName or Password ")
