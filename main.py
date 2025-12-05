from soup.game import SoupFlow

if __name__ == "__main__":
    flow = SoupFlow()
    while True:
        command = input(
            "输入 'start' 开始新游戏，'quit' 退出游戏，'ask: <问题>' 提问，'ans: <答案>' 回答：\n"
        )
        flow.run(command)
