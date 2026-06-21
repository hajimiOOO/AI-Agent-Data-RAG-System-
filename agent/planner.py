import json

from openai import OpenAI


def plan_task(client: OpenAI, user_input: str) -> dict:
    """
    Planner Agent：判断用户任务类型。
    返回 JSON：
    {
        "type": "csv" | "rag" | "mysql" | "chat",
        "reason": "判断原因"
    }
    """

    text = user_input.lower()

    mysql_keywords = [
        "mysql",
        "sql",
        "数据库",
        "数据表",
        "表",
        "查询",
        "订单",
        "用户",
        "商品",
        "销售额",
        "金额",
        "支付",
        "总金额",
        "总销售额",
        "分组",
        "统计",
        "test 数据库",
    ]

    csv_keywords = [
        "csv",
        "表格文件",
        "上传的数据",
        "文件分析",
    ]

    rag_keywords = [
        "知识库",
        "文档",
        "项目说明",
        "项目用了什么",
        "技术栈",
        "介绍这个项目",
    ]

    # 规则兜底：优先保证 MySQL 工具能被触发
    if any(keyword in text for keyword in mysql_keywords):
        return {
            "type": "mysql",
            "reason": "用户问题包含数据库、SQL、查询或统计相关关键词，判断为 MySQL 查询任务。",
        }

    if any(keyword in text for keyword in csv_keywords):
        return {
            "type": "csv",
            "reason": "用户问题包含 CSV 或文件分析相关关键词，判断为 CSV 数据分析任务。",
        }

    if any(keyword in text for keyword in rag_keywords):
        return {
            "type": "rag",
            "reason": "用户问题包含知识库或项目文档相关关键词，判断为 RAG 知识库问答任务。",
        }

    prompt = f"""
你是一个任务规划 Agent。

你需要根据用户输入判断任务类型：

1. csv：用户想分析 CSV、表格文件、上传的数据文件。
2. rag：用户想基于知识库、文档、项目说明进行问答。
3. mysql：用户想查询 MySQL 数据库、订单表、用户表、商品表、支付状态、销售额、数据库数据等。
4. chat：普通对话或无法归类的问题。

注意：
- 如果用户提到 SQL、数据库、查询表、订单、用户、销售额、统计数据库数据，一律返回 mysql。
- 不要返回 sql，只能返回 mysql。

请严格返回 JSON，不要输出多余解释。

格式：
{{
  "type": "csv | rag | mysql | chat",
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
                "content": "你是一个严谨的任务规划器，只能输出 JSON。type 只能是 csv、rag、mysql、chat。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        plan = json.loads(content)

        # 防止模型返回 sql，强制转成 mysql
        if plan.get("type") == "sql":
            plan["type"] = "mysql"
            plan["reason"] = "模型返回 sql，系统自动转换为 mysql 查询任务。"

        return plan

    except Exception:
        return {
            "type": "chat",
            "reason": "模型输出不是合法 JSON，回退到普通对话。",
        }