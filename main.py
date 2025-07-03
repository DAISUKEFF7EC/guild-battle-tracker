from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import os
import json
from collections import defaultdict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BATTLE_FILE = "battle_log.json"
DECLARE_FILE = "declare_log.json"
AVAIL_FILE = "available_log.json"

# ファイル読み込み
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

battle_log = load_data(BATTLE_FILE)
declare_log = load_data(DECLARE_FILE)
available_log = load_data(AVAIL_FILE)

# 戦闘記録をプレイヤー×日付でまとめる
def summarize_battle_log():
    summary = defaultdict(lambda: defaultdict(list))  # {name: {day: [1回目, 2回目, ...]}}
    for entry in battle_log:
        summary[entry["name"]][entry["day"]].append(entry["count"])
    return {name: {day: sorted(set(counts)) for day, counts in days.items()} for name, days in summary.items()}

# プレイヤー一覧
def get_all_names():
    names = {entry["name"] for entry in battle_log + declare_log + available_log}
    return sorted(names)

# -------------------------------
# トップ（テンプレートに集計反映）
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("main.html", {
        "request": request,
        "log": battle_log,
        "declarations": declare_log,
        "availabilities": available_log,
        "battle_summary": summarize_battle_log(),
        "player_names": get_all_names()
    })

# -------------------------------
# 戦闘記録 登録・削除
# -------------------------------
@app.post("/submit")
def submit_battle(
    request: Request,
    name: str = Form(...),
    day: str = Form(...),
    count: str = Form(...),
    stage: int = Form(...),
    damage: int = Form(...)
):
    new_entry = {
        "name": name,
        "day": day,
        "count": count,
        "stage": stage,
        "damage": damage
    }
    battle_log.append(new_entry)
    with open(BATTLE_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)
    return show_form(request)

@app.post("/delete_battle")
def delete_battle(request: Request, name: str = Form(...), day: str = Form(...), count: str = Form(...)):
    global battle_log
    battle_log = [
        entry for entry in battle_log
        if not (entry["name"] == name and entry["day"] == day and entry["count"] == count)
    ]
    with open(BATTLE_FILE, "w", encoding="utf-8") as f:
        json.dump(battle_log, f, indent=2, ensure_ascii=False)
    return show_form(request)

# -------------------------------
# 削れる％申告（上書き＋削除）
# -------------------------------
@app.post("/declare")
def submit_declare(
    request: Request,
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
            entry.update({
                "stage1": stage1, "stage2": stage2, "stage3": stage3,
                "stage4": stage4, "stage5": stage5, "stage6": stage6
            })
            found = True
            break
    if not found:
        declare_log.append({
            "name": name,
            "stage1": stage1, "stage2": stage2, "stage3": stage3,
            "stage4": stage4, "stage5": stage5, "stage6": stage6
        })
    with open(DECLARE_FILE, "w", encoding="utf-8") as f:
        json.dump(declare_log, f, indent=2, ensure_ascii=False)
    return show_form(request)

@app.post("/delete_declare")
def delete_declare(request: Request, name: str = Form(...)):
    global declare_log
    declare_log = [entry for entry in declare_log if entry["name"] != name]
    with open(DECLARE_FILE, "w", encoding="utf-8") as f:
        json.dump(declare_log, f, indent=2, ensure_ascii=False)
    return show_form(request)

# -------------------------------
# 参加可能時間（上書き＋削除）
# -------------------------------
@app.post("/available")
def submit_available(
    request: Request,
    name: str = Form(...),
    day1: List[str] = Form(...),
    day2: List[str] = Form(...),
    day3: List[str] = Form(...)
):
    found = False
    for entry in available_log:
        if entry["name"] == name:
            entry.update({
                "day1": day1,
                "day2": day2,
                "day3": day3
            })
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
    return show_form(request)

@app.post("/delete_available")
def delete_available(request: Request, name: str = Form(...)):
    global available_log
    available_log = [entry for entry in available_log if entry["name"] != name]
    with open(AVAIL_FILE, "w", encoding="utf-8") as f:
        json.dump(available_log, f, indent=2, ensure_ascii=False)
    return show_form(request)
