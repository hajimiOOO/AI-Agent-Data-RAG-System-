import json

from openai import OpenAI

from tools.csv_analyzer import analyze_csv_with_chart
from tools.rag_tool import answer_with_rag
from rag.vector_store import retrieve_chunks


def execute_task(
    client: OpenAI,
    plan: dict,
    user_input: str,
    csv_file_path: str | None = None,
    rag_collection=None,
) -> dict:
    """
    Executor Agent：根据 Planner 的任务类型执行对应工具。
    """
    task_type = plan.get("type", "chat")

    if task_type == "csv":
        if not csv_file_path:
            return {
                "type": "csv",
                "result": "请先上传 CSV 文件。",
                "raw": None,
            }

        tool_result = analyze_csv_with_chart(csv_file_path)

        try:
            raw_result = json.loads(tool_result)
        except Exception:
            raw_result = {"error": tool_result}

        return {
            "type": "csv",
            "result": tool_result,
            "raw": raw_result,
        }

    if task_type == "rag":
        if rag_collection is None:
            return {
                "type": "rag",
                "result": "请先上传知识库文档并构建向量数据库。",
                "raw": None,
            }

        chunks = retrieve_chunks(rag_collection, user_input)
        answer = answer_with_rag(client, user_input, chunks)

        return {
            "type": "rag",
            "result": answer,
            "raw": {
                "retrieved_chunks": chunks,
            },
        }

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个友好的 AI 助手。",
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        stream=False,
    )

    return {
        "type": "chat",
        "result": response.choices[0].message.content,
        "raw": None,
    }