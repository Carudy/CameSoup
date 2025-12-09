import os

import loguru
from dotenv import load_dotenv

logger = loguru.logger

class Config:
    def __init__(self):
        self.reload()

    def reload(self):
        load_dotenv()
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.CHERRYIN_KEY = os.getenv("CHERRYIN_KEY")
        self.JUDGE_MODEL = os.getenv("JUDGE_MODEL", "agent/deepseek-v3.2(free)")
        self.ANS_MODEL = os.getenv("ANS_MODEL", "agent/deepseek-v3.2(free)")

config = Config()