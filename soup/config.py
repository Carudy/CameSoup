import os

import loguru
from dotenv import load_dotenv

logger = loguru.logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()
CHERRYIN_KEY = os.getenv("CHERRYIN_KEY")
