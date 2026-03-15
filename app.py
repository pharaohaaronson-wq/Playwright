from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
import asyncio
from playwright.async_api import async_playwright

app = FastAPI(title="Playwright Task Server")

TASK_RESULTS = {}

class TaskRequest(BaseModel):
    task_name: str
    action: str
    url: Optional[str] = None
    selector: Optional[str] = None
    data: Optional[dict] = None
    timeout: int = 30


@app.get("/")
async def health():
    return {
        "status": "online",
        "engine": "playwright",
        "tasks": len(TASK_RESULTS),
        "time": datetime.now().isoformat()
    }


@app.post("/execute_task")
async def execute_task(task: TaskRequest, background_tasks: BackgroundTasks):

    task_id = str(uuid.uuid4())

    TASK_RESULTS[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "created": datetime.now().isoformat()
    }

    background_tasks.add_task(run_task, task_id, task)

    return {
        "task_id": task_id,
        "status": "queued"
    }


@app.get("/task/{task_id}")
async def task_status(task_id: str):

    if task_id not in TASK_RESULTS:
        raise HTTPException(404, "Task not found")

    return TASK_RESULTS[task_id]


async def run_task(task_id, task):

    try:

        TASK_RESULTS[task_id]["status"] = "running"

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = await browser.new_page()

            if task.url:
                await page.goto(task.url)

            result = {}

            if task.action == "click":

                await page.click(task.selector)
                result["message"] = "clicked"

            elif task.action == "fill":

                for selector, value in task.data.items():
                    await page.fill(selector, value)

                result["message"] = "filled fields"

            elif task.action == "screenshot":

                path = f"/tmp/{task_id}.png"
                await page.screenshot(path=path)

                result["screenshot"] = path

            elif task.action == "text":

                text = await page.inner_text(task.selector)
                result["text"] = text

            elif task.action == "title":

                result["title"] = await page.title()

            await browser.close()

        TASK_RESULTS[task_id]["status"] = "completed"
        TASK_RESULTS[task_id]["result"] = result

    except Exception as e:

        TASK_RESULTS[task_id]["status"] = "failed"
        TASK_RESULTS[task_id]["error"] = str(e)


if __name__ == "__main__":

    import os
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
