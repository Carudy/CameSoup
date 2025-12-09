from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from soup.agents.dep import SoupState
from soup.config import CHERRYIN_KEY

ANSWER_JUDGE_SYSTEM_PROMPT = """
你现在是「海龟汤」游戏的【答案裁判】（Answer Judge）。
你的唯一职责是：判断玩家提交的完整答案是否已经**大体正确**（即已触及汤底的核心真相），当表述不够完美或细节有小出入，但核心逻辑正确且关键要素都说中就判为「正确」。

严格遵守以下规则：
1. 只有当玩家的答案与汤底的**核心真相完全一致或高度等价**时，才回答「正确」。
2. 如果玩家只是接近、缺少关键点、理解方向错误、多余假设干扰真相，一律判为「错误」。
3. 绝对不要因为「很接近」就心软，必须严格！
4. 你看不到玩家的提问历史，只根据本次提交的答案 + 汤底进行独立判断。
""".strip()


class AnswerJudgeOutput(BaseModel):
    """答案裁判的结构化输出"""
    result: Literal["正确", "错误"] = Field(
        description="玩家本次提交的答案是否大体正确"
    )
    reasoning: str = Field(
        description="简要的判断依据"
    )


model = OpenAIChatModel(
    # "agent/deepseek-v3.2-exp(free)",
    "agent/deepseek-v3.1-terminus(free)",
    # "agent/glm-4.6(free)",
    provider=OpenAIProvider(
        api_key=CHERRYIN_KEY, base_url="https://open.cherryin.ai/v1/"
    ),
)

answer_agent = Agent[
    SoupState,
    AnswerJudgeOutput
](
    model=model,
    system_prompt=ANSWER_JUDGE_SYSTEM_PROMPT,
    output_type=AnswerJudgeOutput,
    retries=3,           
)

@answer_agent.instructions
def build_answer_judge_instructions(ctx: SoupState) -> str:
    """
    动态注入当前海龟汤的汤面和汤底（仅裁判可见）
    """
    soup = ctx.deps.current_soup
    if not soup:
        raise ValueError("当前没有加载海龟汤题目（current_soup 为空）")

    question = soup.get("question", "").strip()
    answer = soup.get("answer", "").strip()

    if not question or not answer:
        raise ValueError("current_soup 缺少 question 或 answer 字段")

    return f"""
【当前海龟汤题目 - 仅你可见】

汤面（玩家看到的故事）：
{question}

汤底（标准正确答案）：
{answer}

请严格根据上面的汤底，判断玩家本次提交的答案是否已抓住核心真相。
""".strip()