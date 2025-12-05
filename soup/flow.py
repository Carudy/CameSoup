import json
import os
import random

from pydantic import BaseModel
from rich.console import Console
from rich.text import Text

from soup.agents import answer_agent, judge_agent
from soup.agents.dep import SoupState
from soup.config import BASE_DIR


class SoupFlow:
    def __init__(self):
        self.judge_agent = judge_agent
        self.answer_agent = answer_agent

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

    def end_game(self):
        self.game_state["running"] = False
        self.game_state["current_soup"] = None

    def handle_guess(self, user_input):
        if not self.game_state["running"]:
            return "Game is not running."

        judge_res = self.judge_agent.run_sync(
            user_input, deps=SoupState(**self.game_state)
        )
        msg = f"判断：{judge_res.output.result}"
        msg += f"\n依据：{judge_res.output.reasoning}"
        return msg

    def handle_answer(self, user_input):
        if not self.game_state["running"]:
            return "Game is not running."

        answer_res = self.answer_agent.run_sync(
            user_input, deps=SoupState(**self.game_state)
        )
        if answer_res.output.result == "正确":
            result = (
                f"恭喜你，猜对了！汤底是：{self.game_state['current_soup']['answer']}"
            )
            self.end_game()
            return result
        else:
            msg = "很遗憾，回答错误。"
            msg += f"\n依据：{answer_res.output.reasoning}"
            return msg

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
                msg = self.handle_guess(user_input)
                self.console.print(Text(msg, style="bold blue"))

            elif user_input.strip().startswith("ans"):
                msg = self.handle_answer(user_input)
                self.console.print(Text(msg, style="bold blue"))

            else:
                self.console.print(Text("无法识别的输入。", style="bold red"))
