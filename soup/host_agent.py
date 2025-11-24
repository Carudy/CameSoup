from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from soup.config import CHERRYIN_KEY, GAME_STATE, SOUPS

HOST_PROMPT = """
根据用户的输入，判断他们是想开始新游戏，在提出问题，还是类似于在解答问题。
- 如果用户输入包含“回答”、“我知道了”等关键词，则判断为“回答问题”。
"""


class HostOutput(BaseModel):
    ask_new_game: bool = Field(description="Whether user is asking for a new game.")
    asking_question: bool = Field(description="Whether user is asking a question.")
    answering: bool = Field(description="Whether user is trying to narrative a story.")


model = OpenAIChatModel(
    "agent/deepseek-v3.1-terminus(free)",
    # "agent/glm-4.6(free)",
    provider=OpenAIProvider(
        api_key=CHERRYIN_KEY, base_url="https://open.cherryin.ai/v1/"
    ),
)

host_agent = Agent(
    model=model,
    system_prompt=HOST_PROMPT,
    output_type=HostOutput,
)
