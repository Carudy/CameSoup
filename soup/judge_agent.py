from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from soup.config import CHERRYIN_KEY, GAME_STATE

JUDGE_PROMPT = """
你是海龟汤游戏的判断者，根据用户输入分类回答：
- 一般疑问句（能用是/否回答）：根据汤面汤底回答"是"或"否"或"不相关"
    - 若用户的问题与汤底信息高度相关且答案为肯定，则回答"是" 
    - 若用户的问题与汤底信息高度相关且答案为否定，则回答"否"
    - 若感觉无法用是否回答，则回答"不相关"
注意不主动透露答案信息
"""


class JudgeRes(BaseModel):
    """对用户的回应。"""

    result: Literal["是", "否", "不相关"] = Field(
        description="根据汤面汤底对用户问题的判断"
    )
    reasoning: str = Field(description="简要说明判断依据")


model = OpenAIChatModel(
    "agent/deepseek-v3.2-exp(free)",
    # "agent/glm-4.6(free)",
    provider=OpenAIProvider(
        api_key=CHERRYIN_KEY, base_url="https://open.cherryin.ai/v1/"
    ),
)

judge_agent = Agent(
    model=model,
    system_prompt=JUDGE_PROMPT,
    output_type=JudgeRes,
)


@judge_agent.instructions
def judge_instructions() -> str:
    """为judge_agent生成指令。"""
    current_soup = GAME_STATE["current_soup"]
    soup_question = current_soup["question"]
    soup_answer = current_soup["answer"]

    return f"""
当前的
汤面：{soup_question}
汤底：{soup_answer} 
"""
