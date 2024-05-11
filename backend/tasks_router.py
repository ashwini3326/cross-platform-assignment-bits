from fastapi import APIRouter, Body , HTTPException
from backend.models import Task
from backend.db import database_creds
import json 
import requests
from typing import Annotated
from backend.utils import not_none_task_data
from fastapi.security import OAuth2PasswordBearer


tasks = {}
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/create_task")
async def create_task(
    title:Annotated[ str|None, Body()] =None,
    description:Annotated[ str|None, Body()] = None,
    due_date :Annotated[ str|None, Body()]=None,
    completed: Annotated[ int, Body()] =0
):
    task_data = {
        "title":title,"description":description, "due_date":due_date,"completed":completed
    }
    back4app_class = "Task"
    url = "https://parseapi.back4app.com/classes/" + back4app_class
    resp = requests.post(url, data=task_data, headers=database_creds)
    if resp.status_code == 201:
        return {"task_creation_status": "created",
                "status_code": resp.status_code,
                "response_data": resp.content,
                "resp":resp.url
                }
    else:
        return {
            "Task_creation Failed": "failed",
            "status_code": resp.status_code,
            "response_data": resp.content,
        }

@router.get("/get_task/{_id}")
async def get_task(
    _id: str
):
    back4app_class = "Task"
    headers = database_creds
    params = {"where": '{"objectId":"%s"}'%(_id)}
    print("params : ", params)
    url = "https://parseapi.back4app.com/classes/" + back4app_class
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()["results"][0]
    else:
        raise HTTPException(status_code= resp.status_code, detail="Unable to fetch task.")

@router.get("/get_tasks")
async def get_tasks():
    back4app_class = "Task"
    headers = database_creds
    url = "https://parseapi.back4app.com/classes/" + back4app_class
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()["results"]
    else:
        return {
            "Failed to fetch task": resp.status_code,

        }

@router.put("/update_task/{task_id}")
async def update_task(
    task_id : str,
    title : Annotated[ str|None, Body()] =None,
    description: Annotated[ str|None, Body()]=None,
    due_date: Annotated[ str|None, Body()]=None,
    completed: Annotated[ int, Body()]=0,
):
    new_task_data = {"title":title,
                     "description":description,
                     "due_date":due_date,
                     "completed":completed}
    print(new_task_data)
    new_task_data = not_none_task_data(new_task_data)
    print(new_task_data)
    back4app_class = "Task"
    headers = database_creds
    url = "https://parseapi.back4app.com/classes/" + back4app_class + f"/{task_id}"
    resp = requests.put(url, data=new_task_data, headers=headers)
    if resp.status_code == 200:
        return {"update_status": "updated" }
    else:
        raise HTTPException(status_code=resp.status_code , detail=resp.content)


@router.delete("/delete_task/{task_id}", status_code=204)
async def delete_task(
        task_id : str,
):
    back4app_class = "Task"
    headers = database_creds
    url = "https://parseapi.back4app.com/classes/" + back4app_class + "/" + task_id
    resp = requests.delete(url, headers=headers)
    print(resp.status_code)
    if resp.status_code == 200:
        return {"deletion_status": "deleted"}
    else:
        raise HTTPException(status_code=resp.status_code, detail="Task Not Found")