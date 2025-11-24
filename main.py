from rich.console import Console
from rich.text import Text

from soup.answer_agent import answer_agent
from soup.config import GAME_STATE, get_random_soup
from soup.host_agent import host_agent
from soup.judge_agent import judge_agent

console = Console()


if __name__ == "__main__":
    while True:
        user_input = input("input: ")
        host_res = host_agent.run_sync(user_input)
        console.print("Host: ", host_res.output)

        if not GAME_STATE["running"]:
            if host_res.output.ask_new_game:
                GAME_STATE["running"] = True
                GAME_STATE["current_soup"] = get_random_soup()
                console.print(
                    Text(
                        f"汤面：{GAME_STATE['current_soup']['question']}",
                        style="bold green",
                    )
                )
            else:
                console.print(Text("Game not running.", style="bold red"))
        else:
            if host_res.output.asking_question:
                judge_res = judge_agent.run_sync(
                    user_input,
                )
                console.print(Text(judge_res.output.result, style="bold blue"))
                console.print(Text(judge_res.output.reasoning, style="bold green"))
            elif host_res.output.answering:
                answer_res = answer_agent.run_sync(
                    user_input,
                )
                console.print(Text(answer_res.output.result, style="bold blue"))
                console.print(Text(answer_res.output.reasoning, style="bold green"))
                if answer_res.output.result == "正确":
                    console.print(
                        Text(
                            f"恭喜你，猜对了！汤底是：{GAME_STATE['current_soup']['answer']}",
                            style="bold red",
                        )
                    )
                    GAME_STATE["running"] = False
                    break
            else:
                console.print(Text("Unrecognized input.", style="bold red"))
