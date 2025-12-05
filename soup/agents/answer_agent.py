from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from soup.agents.dep import SoupState
from soup.config import CHERRYIN_KEY

JUDGE_PROMPT = """
你是海龟汤游戏的判断者，根据用户的回答，判断其是否大体正确。
"""


class JudgeRes(BaseModel):
    """对用户的回应。"""

    result: Literal["正确", "错误"] = Field(description="根据汤面汤底对用户回答的判断")
    reasoning: str = Field(description="简要说明判断依据")


model = OpenAIChatModel(
    "agent/deepseek-v3.2-exp(free)",
    # "agent/glm-4.6(free)",
    provider=OpenAIProvider(
        api_key=CHERRYIN_KEY, base_url="https://open.cherryin.ai/v1/"
    ),
)

answer_agent = Agent(
    model=model,
    deps_type=SoupState,
    system_prompt=JUDGE_PROMPT,
    output_type=JudgeRes,
)


@answer_agent.instructions
def answer_instructions(ctx) -> str:
    """为answer_agent生成指令。"""
    current_soup = ctx.deps.current_soup
    soup_question = current_soup["question"]
    soup_answer = current_soup["answer"]

    return f"""
当前的
汤面：{soup_question}
汤底：{soup_answer} 
"""
