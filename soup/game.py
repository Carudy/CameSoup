import json
import os
import random

from rich.console import Console
from rich.text import Text

from soup.agents import answer_agent, judge_agent
from soup.agents.dep import SoupState
from soup.config import BASE_DIR, logger
from soup.comm.msg import GameMsg

class SoupFlow:
    def __init__(self):
        self.judge_agent = judge_agent
        self.answer_agent = answer_agent
        self.ai_running = False
        self.chat_history = []
        self.chat_len = 0

        self.game_state = {
            "game_id": 0,
            "running": False,
            "current_soup": None,
        }

        with open(os.path.join(BASE_DIR, "soups.json"), "r", encoding="utf-8") as f:
            self.soups = json.load(f)
        self.console = Console()

    def get_random_soup(self):
        return random.choice(self.soups)
    
    def insert_chat(self, sayer, content):
        self.chat_history.append({'sayer': sayer, 'content': content})
        self.chat_len += 1

    def start_new_game(self):
        self.end_game()
        self.game_state["game_id"] += 1
        self.game_state["running"] = True
        self.game_state["current_soup"] = self.get_random_soup()
        msg = f"新游戏开始了: {self.game_state['current_soup']['question']}"
        self.insert_chat('主持人', msg)
        logger.info(msg)

    def end_game(self):
        self.game_state["running"] = False
        self.game_state["current_soup"] = None
        self.chat_history = []
        self.chat_len = 0
        logger.info("Game ended.")

    def handle_ask(self, user_input):
        input_txt = ''
        speaker = None
        if isinstance(user_input, dict):
            input_txt = user_input.get('content', '')
            speaker = user_input.get('speaker', None)
        else:
            input_txt = user_input

        ret = GameMsg()
        self.ai_running = True

        if not self.game_state["running"]:
            ret["msg"] = "Game is not running."
            self.ai_running = False
            return ret
        self.insert_chat(speaker if speaker else 'someone', input_txt)

        judge_res = self.judge_agent.run_sync(
            input_txt, deps=SoupState(**self.game_state)
        )
        msg = f"判断：{judge_res.output.result}"
        ret["msg"] = msg
        ret['speaker'] = '主持人'
        self.insert_chat('主持人', msg)

        msg += f"\n依据：{judge_res.output.reasoning}"
        self.console.print(Text(msg, style="bold blue"))
        self.ai_running = False 
        return ret
    
    def handle_answer(self, user_input):
        input_txt = ''
        speaker = None
        if isinstance(user_input, dict):
            input_txt = user_input.get('content', '')
            speaker = user_input.get('speaker', None)
        else:
            input_txt = user_input

        res = GameMsg()
        self.ai_running = True

        if not self.game_state["running"]:
            res["msg"] = "Game is not running."
            self.ai_running = False
            return res

        self.insert_chat(speaker if speaker else 'someone', input_txt)

        answer_res = self.answer_agent.run_sync(
            input_txt, deps=SoupState(**self.game_state)
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
        self.insert_chat('host', res["msg"])
        self.ai_running = False
        return res

    # for CLI
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
