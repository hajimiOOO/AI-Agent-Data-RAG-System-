import json

from openai import OpenAI


def plan_task(client: OpenAI, user_input: str) -> dict:
    """
    Planner Agent：判断用户任务类型。
    返回 JSON：
    {
        "type": "csv" | "rag" | "chat",
        "reason": "判断原因"
    }
    """
    prompt = f"""
你是一个任务规划 Agent。

你需要根据用户输入判断任务类型：

1. csv：用户想分析 CSV、表格、销售数据、成绩数据等。
2. rag：用户想基于知识库、文档、项目说明进行问答。
3. chat：普通对话或无法归类的问题。

请严格返回 JSON，不要输出多余解释。

格式：
{{
  "type": "csv | rag | chat",
  "reason": "你的判断原因"
}}

用户输入：
{user_input}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个严谨的任务规划器，只能输出 JSON。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        return {
            "type": "chat",
            "reason": "模型输出不是合法 JSON，回退到普通对话。",
        }