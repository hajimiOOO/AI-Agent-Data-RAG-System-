from openai import OpenAI


def check_result(client: OpenAI, result: str) -> str:
    """
    Critic Agent：检查执行结果是否合理、清晰。
    """
    prompt = f"""
请检查下面的结果是否清晰、合理，是否存在明显问题。

内容：
{result}

请用中文回答：
1. 是否合理
2. 存在的问题
3. 可改进建议
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个严谨的结果评审 Agent。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content