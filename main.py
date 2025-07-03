from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BATTLE_FILE = "battle_log.json"
DECLARE_FILE = "declare_log.json"
AVAIL_FILE = "available_log.json"

# 各ファイルの読み込み（存在しない場合は空配列）
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

battle_log = load_data(BATTLE_FILE)
declare_log = load_data(DECLARE_FILE)
available_log = load_data(AVAIL_FILE)

# ------------------------
# トップ（1画面で全タブ表示）
# ------------------------
@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("main.html", {
        "request": request,
        "log": battle_log,
        "declarations": declare_log,
        "availabilities": available_log
    })

# ------------------------
# 戦闘記録の登録
# ------------------------
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
    with open(BATTLE_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_battle")
def delete_battle(name: str = Form(...), date: str = Form(...), count: int = Form(...)):
    global battle_log
    battle_log = [
        entry for entry in battle_log
        if not (entry["name"] == name and entry["date"] == date and entry["count"] == count)
    ]
    with open(BATTLE_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)
    return RedirectResponse(url="/", status_code=303)

# ------------------------
# 削れる％申告（同名上書き + 削除）
# ------------------------
@app.get("/declare", response_class=HTMLResponse)
def show_declare_form(request: Request):
    return templates.TemplateResponse("declare.html", {"request": request, "declarations": declare_log})

@app.post("/declare")
def submit_declare(
    name: str = Form(...),
    stage1: int = Form(...),
    stage2: int = Form(...),
    stage3: int = Form(...),
    stage4: int = Form(...),
    stage5: int = Form(...),
    stage6: int = Form(...)
):
    found = False
    for entry in declare_log:
        if entry["name"] == name:
            entry["stage1"] = stage1
            entry["stage2"] = stage2
            entry["stage3"] = stage3
            entry["stage4"] = stage4
            entry["stage5"] = stage5
            entry["stage6"] = stage6
            found = True
            break

    if not found:
        declare_log.append({
            "name": name,
            "stage1": stage1,
            "stage2": stage2,
            "stage3": stage3,
            "stage4": stage4,
            "stage5": stage5,
            "stage6": stage6
        })

    with open(DECLARE_FILE, "w", encoding="utf-8") as f:
        json.dump(declare_log, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_declare")
def delete_declare(name: str = Form(...)):
    global declare_log
    declare_log = [entry for entry in declare_log if entry["name"] != name]
    with open(DECLARE_FILE, "w", encoding="utf-8") as f:
        json.dump(declare_log, f, indent=2, ensure_ascii=False)
    return RedirectResponse(url="/", status_code=303)

# ------------------------
# 参加可能時間申告（同名上書き + 削除）
# ------------------------
@app.get("/available", response_class=HTMLResponse)
def show_available_form(request: Request):
    return templates.TemplateResponse("available.html", {"request": request, "availabilities": available_log})

@app.post("/available")
def submit_available(
    name: str = Form(...),
    day1: str = Form(...),
    day2: str = Form(...),
    day3: str = Form(...)
):
    found = False
    for entry in available_log:
        if entry["name"] == name:
            entry["day1"] = day1
            entry["day2"] = day2
            entry["day3"] = day3
            found = True
            break

    if not found:
        available_log.append({
            "name": name,
            "day1": day1,
            "day2": day2,
            "day3": day3
        })

    with open(AVAIL_FILE, "w", encoding="utf-8") as f:
        json.dump(available_log, f, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_available")
def delete_available(name: str = Form(...)):
    global available_log
    available_log = [entry for entry in available_log if entry["name"] != name]
    with open(AVAIL_FILE, "w", encoding="utf-8") as f:
        json.dump(available_log, f, indent=2, ensure_ascii=False)
    return RedirectResponse(url="/", status_code=303)
