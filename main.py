from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATA_FILE = "battle_log.json"

# 初期ロード（ファイルがあれば読み込む）
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        battle_log = json.load(f)
else:
    battle_log = []

@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "log": battle_log})

@app.post("/submit")
def submit_battle(
    name: str = Form(...),
    date: str = Form(...),
    count: int = Form(...),
    stage: int = Form(...),
    damage: int = Form(...)
):
    new_entry = {
        "name": name,
        "date": date,
        "count": count,
        "stage": stage,
        "damage": damage
    }
    battle_log.append(new_entry)

    # 保存
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=303)

# Render用にはこの起動は不要（Render側が起動する）
