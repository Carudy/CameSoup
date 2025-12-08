from flask import Flask, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from soup.config import logger
from soup.game import SoupFlow


class SoupWebApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.soup_flow = SoupFlow()


app = SoupWebApp(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,           # Trust X-Forwarded-For
    x_proto=1,         # Trust X-Forwarded-Proto
    x_host=1,          # Trust X-Forwarded-Host
    x_port=1,          # Trust X-Forwarded-Port
    x_prefix=1         # THIS IS KEY — Trust X-Forwarded-Prefix
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cmd", methods=["POST"])
def handle_input():
    req = request.json

    logger.info(f"Received: {req}")

    if "cmd" not in req:
        return {"msg": "no cmd"}

    if req["cmd"].strip().lower() == "new_game":
        app.soup_flow.start_new_game()
        return {
            "msg": "New game started.",
            "soup_question": app.soup_flow.game_state["current_soup"]["question"],
        }

    if not app.soup_flow.game_state["running"]:
        return {"msg": "Game is not running."}

    if req["cmd"].strip().lower() == "end_game":
        app.soup_flow.end_game()
        return {"msg": "Game ended."}

    elif req["cmd"].strip().startswith("ask"):
        response = app.soup_flow.handle_ask(req["content"])
        return jsonify(response)

    elif req["cmd"].strip().startswith("ans"):
        response = app.soup_flow.handle_answer(req["content"])
        return jsonify(response)

    else:
        return {"msg": "Unknown command."}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42345, debug=True)
