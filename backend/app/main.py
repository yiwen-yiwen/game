from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import random
import os

app = FastAPI(title="大学生期末求生模拟器")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储游戏状态
games: Dict[str, Any] = {}

class GameState(BaseModel):
    energy: int = 100
    study_progress: int = 0
    day: int = 1
    hour: int = 8
    coins: int = 0
    game_over: bool = False
    ending: Optional[str] = None
    is_midnight_rest: bool = False

class EventChoice(BaseModel):
    choice: str

class RandomEventResult(BaseModel):
    message: str
    study_change: int = 0
    coins_change: int = 0

@app.post("/api/game/new")
def new_game():
    game_id = str(uuid.uuid4())
    state = {
        "energy": 100,
        "study_progress": 0,
        "day": 1,
        "hour": 8,
        "coins": 0,
        "game_over": False,
        "ending": None,
        "is_midnight_rest": False,
    }
    games[game_id] = state
    return {"game_id": game_id, "state": state}

@app.get("/api/game/{game_id}")
def get_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return games[game_id]

@app.post("/api/game/{game_id}/event")
def handle_event(game_id: str, event: EventChoice):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    state = games[game_id]
    
    if state["game_over"]:
        raise HTTPException(status_code=400, detail="游戏已结束")
    
    if state["is_midnight_rest"]:
        state["is_midnight_rest"] = False
    
    choice = event.choice
    hour = state["hour"]
    result = {
        "message": "",
        "study_change": 0,
        "energy_change": 0,
        "coins_change": 0,
        "time_passed": 4,
        "random_event": None,
    }
    
    is_day = 8 <= hour < 20
    
    if choice == "review":
        if not is_day:
            raise HTTPException(status_code=400, detail="夜晚不能复习")
        result["study_change"] = 5
        result["energy_change"] = -30
        result["message"] = "你认真复习了4小时，感觉收获满满！"
    
    elif choice == "sleep":
        if is_day:
            raise HTTPException(status_code=400, detail="白天不能睡觉")
        result["energy_change"] = 20
        result["message"] = "你美美地睡了4小时，精力充沛！"
    
    elif choice == "go_out":
        result["energy_change"] = -30
        rand = random.random()
        if rand < 0.5:
            result["study_change"] = 10
            result["random_event"] = {
                "message": "外出偶遇学霸，请教后复习进度大幅提升！",
                "type": "study"
            }
        else:
            result["coins_change"] = 500
            result["random_event"] = {
                "message": "外出捡到红包，获得500金币！",
                "type": "coins"
            }
        result["message"] = "你外出探索了一番..."
    
    else:
        raise HTTPException(status_code=400, detail="无效的选择")
    
    state["study_progress"] = min(100, max(0, state["study_progress"] + result["study_change"]))
    state["energy"] = min(100, max(0, state["energy"] + result["energy_change"]))
    state["coins"] += result["coins_change"]
    
    state["hour"] += result["time_passed"]
    
    if state["hour"] >= 24:
        state["hour"] = 0
        state["is_midnight_rest"] = True
        state["energy"] = min(100, state["energy"] + 80)
        state["day"] += 1
        result["midnight_rest"] = True
        result["message"] += " \n时间到了午夜，你自动进入休息，精力恢复80点。"
        
        if state["day"] > 7:
            state["game_over"] = True
            if state["study_progress"] >= 100:
                state["ending"] = "pass"
                result["ending"] = "pass"
                result["message"] += " \n期末考试结束！你通过了考试！"
            else:
                state["ending"] = "fail"
                result["ending"] = "fail"
                result["message"] += " \n期末考试结束！你挂科了..."
    
    return {"state": state, "result": result}

@app.post("/api/game/{game_id}/midnight")
def handle_midnight(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    state = games[game_id]
    
    if state["game_over"]:
        raise HTTPException(status_code=400, detail="游戏已结束")
    
    if not state["is_midnight_rest"]:
        raise HTTPException(status_code=400, detail="不是休息时间")
    
    state["is_midnight_rest"] = False
    state["hour"] = 8
    
    return state

@app.delete("/api/game/{game_id}")
def delete_game(game_id: str):
    if game_id in games:
        del games[game_id]
    return {"message": "游戏已删除"}

# 静态文件服务 - 用于部署前端
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
