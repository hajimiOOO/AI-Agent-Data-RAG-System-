from openai import OpenAI


def answer_with_rag(
    client: OpenAI,
    question: str,
    context_chunks: list[str],
) -> str:
    """
    基于检索到的资料片段调用 DeepSeek 生成回答。
    """
    context = "\n\n".join(context_chunks)

    prompt = f"""
请你严格根据下面的资料回答用户问题。
如果资料中没有相关信息，请回答：资料中没有提到，无法确定。

资料：
{context}

用户问题：
{question}
"""

    messages = [
        {
            "role": "system",
            "content": "你是一个严谨的知识库问答助手，只能根据提供的资料回答问题。",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False,
    )

    return response.choices[0].message.content