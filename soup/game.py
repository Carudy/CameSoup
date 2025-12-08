import json
import os
import random

from rich.console import Console
from rich.text import Text

from soup.agents import answer_agent, judge_agent
from soup.agents.dep import SoupState
from soup.config import BASE_DIR, logger


class SoupFlow:
    def __init__(self):
        self.judge_agent = judge_agent
        self.answer_agent = answer_agent
        self.ai_running = False

        self.game_state = {
            "running": False,
            "current_soup": None,
        }

        with open(os.path.join(BASE_DIR, "soups.json"), "r", encoding="utf-8") as f:
            self.soups = json.load(f)

        self.console = Console()

    def get_random_soup(self):
        return random.choice(self.soups)

    def start_new_game(self):
        self.game_state["running"] = True
        self.game_state["current_soup"] = self.get_random_soup()
        logger.info(f"New game started with soup: {self.game_state['current_soup']}")

    def end_game(self):
        self.game_state["running"] = False
        self.game_state["current_soup"] = None
        logger.info("Game ended.")

    def handle_ask(self, user_input):
        res = {
            "msg": "",
        }
        self.ai_running = True

        if not self.game_state["running"]:
            res["msg"] = "Game is not running."
            return res

        judge_res = self.judge_agent.run_sync(
            user_input, deps=SoupState(**self.game_state)
        )
        msg = f"判断：{judge_res.output.result}"
        res["msg"] = msg
        msg += f"\n依据：{judge_res.output.reasoning}"
        self.console.print(Text(msg, style="bold blue"))
        self.ai_running = False 
        return res

    def handle_answer(self, user_input):
        res = {
            "msg": "",
        }

        self.ai_running = True

        if not self.game_state["running"]:
            res["msg"] = "Game is not running."
            return res

        answer_res = self.answer_agent.run_sync(
            user_input, deps=SoupState(**self.game_state)
        )
        if answer_res.output.result == "正确":
            res["msg"] = (
                f"恭喜你，猜对了！汤底是：{self.game_state['current_soup']['answer']}"
            )
            self.console.print(Text(res["msg"], style="bold blue"))
            self.end_game()
        else:
            res["msg"] = "很遗憾，回答错误。"
            self.console.print(
                Text(
                    res["msg"] + f"\n依据：{answer_res.output.reasoning}",
                    style="bold blue",
                )
            )
        self.ai_running = False
        return res

    def run(self, user_input):
        if "start" == user_input.strip().lower():
            self.start_new_game()
            self.console.print(
                Text(
                    f"汤面：{self.game_state['current_soup']['question']}",
                    style="bold green",
                )
            )

        else:
            if user_input.strip().lower() == "quit":
                self.end_game()
                self.console.print(Text("游戏结束。", style="bold red"))
            elif not self.game_state["running"]:
                self.console.print(
                    Text("游戏未开始。请输入 'start' 开始新游戏。", style="bold red")
                )

            if user_input.strip().startswith("ask"):
                self.handle_ask(user_input)

            elif user_input.strip().startswith("ans"):
                self.handle_answer(user_input)

            else:
                self.console.print(Text("无法识别的输入。", style="bold red"))
