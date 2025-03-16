import asyncio
from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict
import os

ROOT_PATH = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))
app = FastAPI()

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    content: str
    is_user: bool

async def run_graphrag(query: str, method: str) -> str:
    cmd = [
        "graphrag",
        "query",
        "--root", "..",
        "--method", method,
        "--query", query
    ]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        return f"Error: {stderr.decode()}"
    content = stdout.decode().strip()
    return content

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat_api(
    message: str = Form(...),
    method: str = Form(...),
    history: str = Form("[]")  # 接收JSON字符串格式的历史记录
):
    try:
        from json import loads
        history_data = loads(history)
        full_query = "\n".join([msg["content"] for msg in history_data] + [message])
    except:
        full_query = message
    
    response = await run_graphrag(full_query, method)
    
    return {
        "response": response,
        "full_query": full_query
    }

