import json
import os
import random

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()
CHERRYIN_KEY = os.getenv("CHERRYIN_KEY")

with open(os.path.join(BASE_DIR, "soups.json"), "r", encoding="utf-8") as f:
    SOUPS = json.load(f)


GAME_STATE = {
    "running": False,
    "current_soup": None,
}


def get_random_soup() -> dict:
    return random.choice(SOUPS)
