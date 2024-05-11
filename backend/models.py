import uuid
from pydantic import BaseModel

class Task(BaseModel):
    title: str | None
    description: str | None
    due_date: str | None
    completed: bool 
    _id: str = str(uuid.uuid4())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id: str = str(uuid.uuid4())
    
    @property
    def get_id(self):
        return self._id
    
    def update_task(self, **kwargs):
        print(kwargs)
        for key in kwargs.keys():
            if kwargs.get(key):
                setattr(self, key, kwargs[key])
            if key == "completed":
                setattr(self,key, kwargs[key])
        print("task_status : ", self.completed)

class User(BaseModel):
    name: str
    email: str
    password: str