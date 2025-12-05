import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()
CHERRYIN_KEY = os.getenv("CHERRYIN_KEY")
