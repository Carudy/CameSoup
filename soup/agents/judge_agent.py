from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from soup.agents.dep import SoupState
from soup.config import CHERRYIN_KEY

JUDGE_SYSTEM_PROMPT = """
你现在是「海龟汤」游戏的严格判断者。
你的任务是根据汤面（用户看到的故事）和汤底（隐藏的真相），对玩家的提问进行精准分类回答。

规则如下：
1. 如果问题是典型的「是否」疑问句（可以用 是 / 否 明确回答），请严格按照汤底的事实回答：
   - 完全正确且与汤底高度相关的肯定回答 → 回答「是」
   - 完全错误或与汤底矛盾的否定回答 → 回答「否」
   - 与汤底无关或无法用「是/否」明确判断 → 回答「不相关」
2. 绝不能主动泄露任何汤底信息，只能回答「是」「否」「不相关」三者之一。
3. 回答必须极其简洁，不能添加任何额外解释、暗示或情感词。
""".strip()


class JudgeOutput(BaseModel):
    """Judge 代理的结构化输出"""
    result: Literal["是", "否", "不相关"] = Field(
        description="对玩家提问的最终判定结果"
    )
    reasoning: str = Field(
        description="【内部记录】判断此结果的简要逻辑依据，仅用于调试和日志，不会在回复中显示"
    )

model = OpenAIChatModel(
    "agent/deepseek-v3.1-terminus(free)", 
    provider=OpenAIProvider(
        api_key=CHERRYIN_KEY,
        base_url="https://open.cherryin.ai/v1/",
    )
)

judge_agent = Agent[
    SoupState,           
    JudgeOutput          
](
    model=model,
    system_prompt=JUDGE_SYSTEM_PROMPT,
    output_type=JudgeOutput,
    retries=2,           
)

# ==================== Dynamic Instructions ====================

@judge_agent.instructions
def build_judge_instructions(ctx: SoupState) -> str:
    """
    动态注入当前海龟汤的汤面和汤底（仅 Judge 能看到）。
    """
    soup = ctx.deps.current_soup
    if not soup:
        raise ValueError("当前没有加载海龟汤题目（current_soup 为空）")

    question = soup.get("question", "").strip()
    answer = soup.get("answer", "").strip()

    if not question or not answer:
        raise ValueError("current_soup 缺少 question 或 answer 字段")

    return f"""
当前海龟汤题目（仅你可见）：

汤面（玩家看到的故事）：
{question}

汤底（隐藏的真相）：
{answer}
    """.strip()