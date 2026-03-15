from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json
import uuid

app = FastAPI()

r = redis.Redis(host="redis", port=6379, decode_responses=True)

class Task(BaseModel):
    url: str
    action: str
    selector: str | None = None
    value: str | None = None


@app.get("/")
def health():
    return {"status": "online"}


@app.post("/task")
def add_task(task: Task):

    task_id = str(uuid.uuid4())

    payload = {
        "id": task_id,
        "url": task.url,
        "action": task.action,
        "selector": task.selector,
        "value": task.value
    }

    r.lpush("task_queue", json.dumps(payload))

    return {"task_id": task_id}
