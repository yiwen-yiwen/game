from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import random

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

SAVE_FILE = 'game_save.json'

DEFAULT_STATE = {
    "day": 1,
    "phase": "warmup",
    "time_slot": "morning",
    "review": 50,
    "mental": 80,
    "energy": 100,
    "score": 60,
    "stats_unlocked": False,
    "history": [],
    "game_over": False,
    "ending": None,
    "current_event": None
}

PHASE_DAYS = {
    "warmup": 5,
    "sprint": 2,
    "exam": 1
}

TIME_SLOTS = ["morning", "noon", "afternoon", "evening"]

EVENTS = {
    "warmup": {
        "morning": {
            "title": "早晨的抉择",
            "story": "闹钟响了第三遍，你躺在床上，感觉灵魂还在梦里游荡。今天第一节是专业课，老师点名很严...",
            "choices": [
                {"text": "爬起来去上课", "effects": {"score": 10, "energy": -10}, "desc": "平时分+10，精力-10"},
                {"text": "翻个身继续睡", "effects": {"score": -15, "energy": 20}, "desc": "平时分-15，精力+20"},
                {"text": "让室友帮忙答到", "effects": {"score": 5, "energy": 5, "mental": -5}, "desc": "平时分+5，精力+5，精神-5"}
            ]
        },
        "noon": {
            "title": "午后的作业危机",
            "story": "吃完午饭回到宿舍，发现群里老师催交上周布置的作业，截止时间就在今天下午...",
            "choices": [
                {"text": "认真写", "effects": {"review": 5, "energy": -15}, "desc": "复习+5，精力-15"},
                {"text": "找学霸抄", "effects": {"score": 5, "energy": -5}, "desc": "平时分+5，精力-5"},
                {"text": "假装没看见", "effects": {"score": -20, "mental": 10}, "desc": "平时分-20，精神+10"}
            ]
        },
        "afternoon": {
            "title": "下午的自由时光",
            "story": "下午没课，宿舍里室友在打游戏，楼下有人在打篮球，图书馆的座位还空着...",
            "choices": [
                {"text": "去图书馆复习", "effects": {"review": 15, "energy": -20}, "desc": "复习+15，精力-20"},
                {"text": "在宿舍打游戏", "effects": {"mental": 15, "review": -5}, "desc": "精神+15，复习-5"},
                {"text": "去社团活动", "effects": {"mental": 15, "review": -5}, "desc": "精神+15，复习-5"}
            ]
        },
        "evening": {
            "title": "深夜的挣扎",
            "story": "夜深了，宿舍熄灯了，室友有的已经睡了，有的还在刷手机。明天还有课，但你感觉复习进度落后了...",
            "choices": [
                {"text": "熬夜刷题", "effects": {"review": 20, "energy": -25, "mental": -10}, "desc": "复习+20，精力-25，精神-10"},
                {"text": "早睡养精神", "effects": {"energy": 25, "mental": 10}, "desc": "精力+25，精神+10"},
                {"text": "刷手机到半夜", "effects": {"mental": 5, "energy": -10, "review": -5}, "desc": "精神+5，精力-10，复习-5"}
            ]
        }
    },
    "sprint": {
        "morning": {
            "title": "冲刺阶段的早晨",
            "story": "距离考试只剩几天了，你感觉心跳加速。今天的课老师说要划重点，绝对不能错过...",
            "choices": [
                {"text": "认真听划重点", "effects": {"review": 25, "energy": -15}, "desc": "复习+25，精力-15"},
                {"text": "在课上偷偷复习", "effects": {"review": 15, "energy": -10}, "desc": "复习+15，精力-10"},
                {"text": "课上补觉", "effects": {"energy": 20, "review": -10}, "desc": "精力+20，复习-10"}
            ]
        },
        "noon": {
            "title": "争分夺秒的午后",
            "story": "午饭时间，食堂里人山人海。你端着饭找到一个角落坐下，发现旁边坐的是学霸...",
            "choices": [
                {"text": "向学霸请教", "effects": {"review": 20, "mental": 10, "energy": -10}, "desc": "复习+20，精神+10，精力-10"},
                {"text": "自己 panic 复习", "effects": {"review": 15, "mental": -15, "energy": -20}, "desc": "复习+15，精神-15，精力-20"},
                {"text": "慢慢吃饭休息", "effects": {"energy": 15, "mental": 10}, "desc": "精力+15，精神+10"}
            ]
        },
        "afternoon": {
            "title": "下午的极限挑战",
            "story": "下午的阳光照进图书馆，你看着厚厚的教材，感觉头都大了。旁边的人都在埋头苦读...",
            "choices": [
                {"text": "硬撑着学", "effects": {"review": 10, "mental": -20}, "desc": "复习+10，精神-20"},
                {"text": "回宿舍休息", "effects": {"energy": 20, "mental": 10, "review": -5}, "desc": "精力+20，精神+10，复习-5"},
                {"text": "去咖啡厅换环境", "effects": {"review": 15, "energy": -10, "mental": 5}, "desc": "复习+15，精力-10，精神+5"}
            ]
        },
        "evening": {
            "title": "考前的最后夜晚",
            "story": "这是考前的最后一个晚上了，宿舍里弥漫着紧张的气氛。有人在走廊里背书，有人已经躺下了...",
            "choices": [
                {"text": "通宵复习", "effects": {"review": 30, "energy": -40, "mental": -20}, "desc": "复习+30，精力-40，精神-20"},
                {"text": "正常睡觉", "effects": {"energy": 20, "mental": 15}, "desc": "精力+20，精神+15"},
                {"text": "和室友互相提问", "effects": {"review": 15, "mental": 10, "energy": -10}, "desc": "复习+15，精神+10，精力-10"}
            ]
        }
    },
    "exam": {
        "morning": {
            "title": "期末考试日",
            "story": "今天就是期末考试的日子。你走进考场，手心冒汗，心脏狂跳。试卷发下来了...",
            "choices": [
                {"text": "冷静答题", "effects": {"review": 0, "mental": -10, "energy": -20}, "desc": "精神-10，精力-20"},
                {"text": "先写会的", "effects": {"review": 0, "mental": -5, "energy": -15}, "desc": "精神-5，精力-15"},
                {"text": "临场发挥", "effects": {"review": 0, "mental": -20, "energy": -10}, "desc": "精神-20，精力-10"}
            ]
        },
        "noon": {
            "title": "中场休息",
            "story": "上午的考试结束了，你走出考场，感觉整个人都被掏空了。下午的考试还在等着你...",
            "choices": [
                {"text": "抓紧复习下午科目", "effects": {"review": 10, "energy": -15}, "desc": "复习+10，精力-15"},
                {"text": "吃饭休息", "effects": {"energy": 20, "mental": 10}, "desc": "精力+20，精神+10"},
                {"text": "和同学对答案", "effects": {"mental": -15, "energy": -5}, "desc": "精神-15，精力-5"}
            ]
        },
        "afternoon": {
            "title": "最后一场考试",
            "story": "这是最后一场考试了。你看着试卷，感觉脑子里一片空白，又好像什么都有...",
            "choices": [
                {"text": "全力以赴", "effects": {"review": 0, "mental": -20, "energy": -30}, "desc": "精神-20，精力-30"},
                {"text": "尽力而为", "effects": {"review": 0, "mental": -10, "energy": -20}, "desc": "精神-10，精力-20"},
                {"text": "随缘作答", "effects": {"review": 0, "mental": 5, "energy": -10}, "desc": "精神+5，精力-10"}
            ]
        },
        "evening": {
            "title": "考试结束",
            "story": "铃声响起，你放下笔，长舒一口气。期末考试终于结束了，你走出教学楼，夕阳正好...",
            "choices": [
                {"text": "查看结局", "effects": {}, "desc": "进入结局结算"}
            ]
        }
    }
}

RANDOM_EVENTS = [
    {
        "title": "意外之喜",
        "story": "你在图书馆座位下发现了一本上届学霸留下的复习笔记！",
        "choices": [
            {"text": "认真研读", "effects": {"review": 15, "energy": -5}, "desc": "复习+15，精力-5"},
            {"text": "拍照收藏", "effects": {"review": 10, "mental": 5}, "desc": "复习+10，精神+5"}
        ]
    },
    {
        "title": "室友的求助",
        "story": "室友慌慌张张地问你借复习资料，说ta什么都没准备...",
        "choices": [
            {"text": "慷慨分享", "effects": {"mental": 15, "review": -5}, "desc": "精神+15，复习-5"},
            {"text": "婉拒", "effects": {"mental": -10}, "desc": "精神-10"},
            {"text": "交换资料", "effects": {"review": 10, "energy": -5}, "desc": "复习+10，精力-5"}
        ]
    },
    {
        "title": "老师的通知",
        "story": "群里突然通知，考试范围缩小了！重点只有前三章！",
        "choices": [
            {"text": "针对性复习", "effects": {"review": 20, "mental": 15}, "desc": "复习+20，精神+15"},
            {"text": "放松一会", "effects": {"mental": 20, "energy": 10}, "desc": "精神+20，精力+10"}
        ]
    },
    {
        "title": "身体报警",
        "story": "你突然感觉头晕目眩，可能是最近熬夜太多了...",
        "choices": [
            {"text": "立刻休息", "effects": {"energy": 20, "review": -10}, "desc": "精力+20，复习-10"},
            {"text": "硬撑过去", "effects": {"energy": -15, "mental": -15, "review": 5}, "desc": "精力-15，精神-15，复习+5"}
        ]
    },
    {
        "title": "外卖风波",
        "story": "你点的外卖被送错了，现在手里是一份陌生人的麻辣香锅...",
        "choices": [
            {"text": "吃掉它", "effects": {"energy": 15, "mental": 10}, "desc": "精力+15，精神+10"},
            {"text": "联系骑手换回来", "effects": {"energy": -5, "mental": -5}, "desc": "精力-5，精神-5"}
        ]
    }
]

ENDINGS = {
    "god": {
        "name": "学霸封神",
        "desc": "你以满级状态走出考场，同学们纷纷拜你为考神。下学期，你的笔记被复印了10086份。",
        "condition": lambda s: s["review"] >= 90 and s["mental"] >= 70 and s["score"] >= 80
    },
    "lucky": {
        "name": "运气之王",
        "desc": "你复习的内容恰好都考了，不会的都没考。你怀疑自己是天选之子。",
        "condition": lambda s: s["review"] >= 70 and s["mental"] >= 60
    },
    "normal": {
        "name": "平稳落地",
        "desc": "你勉强通过了所有考试，虽然分数不高，但至少不用补考了。假期可以安心躺平了。",
        "condition": lambda s: s["review"] >= 50 and s["score"] >= 40
    },
    "makeup": {
        "name": "补考见",
        "desc": "你挂科了。辅导员亲切地拍了拍你的肩膀：'下学期补考见。'你的假期注定与复习为伴。",
        "condition": lambda s: s["review"] < 50 and s["score"] < 60
    },
    "dropout": {
        "name": "退学警告",
        "desc": "你的平时分太低了，老师甚至不记得有你这个学生。教务处给你发了退学警告信。",
        "condition": lambda s: s["score"] < 30
    },
    "hospital": {
        "name": "医院 VIP",
        "desc": "你因为过度劳累被送进了医院。护士给你扎针的时候说：'年轻人，身体最重要啊。'",
        "condition": lambda s: s["energy"] < 10 or s["mental"] < 10
    }
}


def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_STATE.copy()


def save_state(state):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(max_val, value))


def get_current_event(state):
    phase = state["phase"]
    time_slot = state["time_slot"]
    
    if phase == "exam" and time_slot == "evening":
        return EVENTS[phase][time_slot]
    
    if random.random() < 0.15:
        event = random.choice(RANDOM_EVENTS).copy()
        event["is_random"] = True
        return event
    
    return EVENTS[phase][time_slot]


def apply_choice(state, choice):
    effects = choice.get("effects", {})
    for key, value in effects.items():
        if key in state:
            state[key] = clamp(state[key] + value)
    
    state["history"].append({
        "day": state["day"],
        "time": state["time_slot"],
        "choice": choice["text"] + "（" + choice.get("desc", "") + "）",
        "effect": effects
    })
    
    if state["energy"] <= 0:
        state["energy"] = 30
        state["mental"] = clamp(state["mental"] - 5)
        state["history"].append({
            "day": state["day"],
            "time": "强制休息",
            "choice": "精力耗尽，强制休息",
            "effect": {"energy": 30, "mental": -5}
        })
    
    return state


def advance_time(state):
    current_idx = TIME_SLOTS.index(state["time_slot"])
    if current_idx < len(TIME_SLOTS) - 1:
        state["time_slot"] = TIME_SLOTS[current_idx + 1]
    else:
        state["time_slot"] = "morning"
        state["day"] += 1
        
        if state["day"] > PHASE_DAYS["warmup"] and state["phase"] == "warmup":
            state["phase"] = "sprint"
            state["day"] = 1
        elif state["day"] > PHASE_DAYS["sprint"] and state["phase"] == "sprint":
            state["phase"] = "exam"
            state["day"] = 1
        elif state["day"] > PHASE_DAYS["exam"] and state["phase"] == "exam":
            state["game_over"] = True
            state["ending"] = calculate_ending(state)
    
    return state


def calculate_ending(state):
    for key, ending in ENDINGS.items():
        if ending["condition"](state):
            return {"key": key, "name": ending["name"], "desc": ending["desc"]}
    
    return {"key": "normal", "name": "平稳落地", "desc": "你勉强通过了所有考试，虽然分数不高，但至少不用补考了。假期可以安心躺平了。"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/event')
def event_page():
    return render_template('event.html')


@app.route('/ending')
def ending_page():
    return render_template('ending.html')


@app.route('/api/state', methods=['GET'])
def get_state():
    state = load_state()
    return jsonify(state)


@app.route('/api/start', methods=['POST'])
def start_game():
    state = DEFAULT_STATE.copy()
    state["history"] = []
    state["current_event"] = get_current_event(state)
    save_state(state)
    return jsonify(state)


@app.route('/api/choice', methods=['POST'])
def make_choice():
    data = request.get_json()
    choice_idx = data.get('choice_idx', 0)
    
    state = load_state()
    
    if state["game_over"]:
        return jsonify({"error": "游戏已结束"}), 400
    
    event = state.get("current_event") or get_current_event(state)
    
    if choice_idx < 0 or choice_idx >= len(event["choices"]):
        return jsonify({"error": "无效的选择"}), 400
    
    choice = event["choices"][choice_idx]
    state = apply_choice(state, choice)
    
    if not state["stats_unlocked"]:
        state["stats_unlocked"] = True
    
    state = advance_time(state)
    
    if not state["game_over"]:
        state["current_event"] = get_current_event(state)
    else:
        state["current_event"] = None
    
    save_state(state)
    return jsonify(state)


@app.route('/api/event', methods=['GET'])
def get_event():
    state = load_state()
    if state["game_over"]:
        return jsonify({"error": "游戏已结束"}), 400
    
    event = state.get("current_event") or get_current_event(state)
    state["current_event"] = event
    save_state(state)
    return jsonify(event)


@app.route('/api/ending', methods=['GET'])
def get_ending():
    state = load_state()
    if not state["game_over"]:
        return jsonify({"error": "游戏尚未结束"}), 400
    
    return jsonify(state["ending"])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
