from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from soup.config import logger
from soup.game import SoupFlow


class SoupWebApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.soup_flow = SoupFlow()

class IgnoreHeartbeatFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        return not any(ignore in msg for ignore in [
            'post /update',
            'get /update',
        ])
    
logging.getLogger('werkzeug').addFilter(IgnoreHeartbeatFilter())

app = SoupWebApp(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,          
    x_proto=1,         
    x_host=1,          
    x_port=1,          
    x_prefix=1         
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/update", methods=["POST"])
def handle_update():
    req = request.json
    if "cmd" not in req or req["cmd"].strip().lower() != "get_info":
        return {"msg": "no cmd / wrong cmd"}
    
    # renew info
    if req['cmd'].strip().lower() == "get_info":
        res = {
            "code": 0,
            "msg": "Info renewed.",
            "ai_running": app.soup_flow.ai_running,
            "game_id": app.soup_flow.game_state["game_id"],
            "current_soup": app.soup_flow.game_state["current_soup"]['question'] if app.soup_flow.game_state["current_soup"] else None,
        }
        if req['game_id'] != app.soup_flow.game_state["game_id"]:
            res["new_chats"] = app.soup_flow.chat_history
        else:
            res["new_chats"] = app.soup_flow.chat_history[req['chat_id']:] if req['chat_id'] < len(app.soup_flow.chat_history) else []
        if res["new_chats"]:
            logger.info(f"New chats: {len(res['new_chats'])} since chat_id {req['chat_id']}")
        return res


@app.route("/cmd", methods=["POST"])
def handle_input():
    req = request.json
    if "cmd" not in req:
        return {"code": 1, "msg": "no cmd"}

    logger.info(f"Received: {req}")
    # other cmds
    if app.soup_flow.ai_running:
        return {"code": 1, "msg": "AI is processing. Please wait."}

    if req["cmd"].strip().lower() == "new_game":
        app.soup_flow.start_new_game()
        return {
            "code": 0,
            "msg": "New game started.",
            "soup_question": app.soup_flow.game_state["current_soup"]["question"],
        }

    if not app.soup_flow.game_state["running"]:
        return {"code": 0, "msg": "Game is not running."}

    if req["cmd"].strip().lower() == "end_game":
        app.soup_flow.end_game()
        return {"code": 0, "msg": "Game ended."}

    if len(req["content"]) < 5:
        return {"code": 1, "msg": "Game ended."}

    if req["cmd"].strip().startswith("ask"):
        res = app.soup_flow.handle_ask(req)
        return res

    elif req["cmd"].strip().startswith("ans"):
        res = app.soup_flow.handle_answer(req)
        return res

    else:
        return {"msg": "Unknown command."}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42345)
