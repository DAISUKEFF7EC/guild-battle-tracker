from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATA_FILE = "battle_log.json"
DECL_FILE = "declarations.json"

# バトルログ初期ロード
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        battle_log = json.load(f)
else:
    battle_log = []

# ステージ削り申告データ初期ロード
if os.path.exists(DECL_FILE):
    with open(DECL_FILE, "r", encoding="utf-8") as f:
        declarations = json.load(f)
else:
    declarations = []

# メインフォーム表示
@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "log": battle_log})

# バトル記録登録
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

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=303)

# 削りパーセント申告フォーム表示
@app.get("/declare", response_class=HTMLResponse)
def show_declaration_form(request: Request):
    return templates.TemplateResponse("declaration.html", {"request": request, "declarations": declarations})

# 削りパーセント申告登録
@app.post("/declare")
def submit_declaration(
    name: str = Form(...),
    stage1: int = Form(...),
    stage2: int = Form(...),
    stage3: int = Form(...),
    stage4: int = Form(...),
    stage5: int = Form(...),
    stage6: int = Form(...)
):
    entry = {
        "name": name,
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
        "stage4": stage4,
        "stage5": stage5,
        "stage6": stage6,
    }
    declarations.append(entry)

    with open(DECL_FILE, "w", encoding="utf-8") as f:
        json.dump(declarations, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/declare", status_code=303)
