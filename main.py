import argparse
import threading
from soup.game import SoupFlow
from soup.web.app import app, Config
from soup.config import logger, config

def run_cli():
    flow = SoupFlow()
    while True:
        command = input(
            "输入 'start' 开始新游戏，'quit' 退出游戏，'ask: <问题>' 提问，'ans: <答案>' 回答：\n"
        )
        flow.run(command)


def run_web():
    host = Config.HOST
    port = Config.PORT
    logger.info(f"Starting Kame Soup server on {host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", dest="cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_web()
