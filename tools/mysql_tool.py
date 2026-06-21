import os
import re

import pymysql
from dotenv import load_dotenv


# 读取项目根目录下的 .env 文件
# override=True 表示优先使用 .env 里的配置，避免读到旧的系统环境变量
load_dotenv(override=True)


def get_mysql_connection():
    """
    创建 MySQL 数据库连接。
    配置信息从 .env 中读取。
    """
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")

    if not user or not password or not database:
        raise ValueError(
            "MySQL 配置不完整，请检查 .env 中是否配置了 "
            "MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE。"
        )

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    return conn


def get_mysql_schema():
    """
    获取当前 MySQL 数据库中的所有表结构。
    例如：
    表名：user
    字段：id int, name varchar(50), age int
    """
    conn = get_mysql_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            schema_parts = []

            for table_item in tables:
                table_name = list(table_item.values())[0]

                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                columns = cursor.fetchall()

                column_info = []

                for col in columns:
                    column_info.append(
                        f"{col['Field']} {col['Type']}"
                    )

                schema_parts.append(
                    f"表名：{table_name}\n字段：{', '.join(column_info)}"
                )

        return "\n\n".join(schema_parts)

    finally:
        conn.close()


def clean_sql(sql):
    """
    清理大模型返回的 SQL。
    防止模型返回 ```sql ... ``` 这种 Markdown 代码块。
    """
    sql = sql.strip()
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


def is_safe_select_sql(sql):
    """
    SQL 安全检查：
    只允许 SELECT 查询。
    禁止 INSERT、UPDATE、DELETE、DROP 等危险操作。
    """
    sql_lower = sql.lower().strip()

    if not sql_lower.startswith("select"):
        return False

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "replace",
        "grant",
        "revoke",
        "commit",
        "rollback",
        "use",
    ]

    for keyword in forbidden_keywords:
        pattern = r"\b" + keyword + r"\b"
        if re.search(pattern, sql_lower):
            return False

    return True


def generate_mysql_sql(client, question, schema):
    """
    根据用户自然语言问题和 MySQL 表结构生成 SELECT SQL。
    """
    prompt = f"""
你是一个专业 MySQL 查询生成助手。

请根据数据库表结构和用户问题，生成一条可以在 MySQL 中执行的 SELECT 查询语句。

要求：
1. 只能生成 SELECT 查询。
2. 不能生成 INSERT、UPDATE、DELETE、DROP、ALTER、CREATE 等危险操作。
3. 只返回 SQL 语句，不要解释。
4. SQL 必须基于下面的真实表结构，不能编造表名或字段名。
5. 如果用户问统计类问题，可以使用 COUNT、SUM、AVG、MAX、MIN、GROUP BY、ORDER BY。
6. 如果查询结果可能很多，请加 LIMIT 20。
7. 如果表名是 user，请使用反引号写成 `user`，避免和 MySQL 关键字冲突。
8. 表名和字段名如有需要，请使用 MySQL 反引号包裹。

数据库表结构：
{schema}

用户问题：
{question}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个严谨的 MySQL SQL 生成助手，只能输出 SELECT SQL。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    sql = response.choices[0].message.content
    sql = clean_sql(sql)

    return sql


def execute_mysql_sql(sql):
    """
    执行 MySQL SELECT 查询，并返回结果。
    这里直接使用 PyMySQL 查询，不使用 pandas，避免结果转换异常。
    """
    print("正在使用新版 tools/mysql_tool.py 执行 MySQL 查询")

    if not is_safe_select_sql(sql):
        return {
            "error": "SQL 安全检查未通过，只允许执行 SELECT 查询。",
            "sql": sql,
        }

    conn = get_mysql_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        if rows:
            columns = list(rows[0].keys())
        else:
            columns = []

        return {
            "sql": sql,
            "row_count": len(rows),
            "columns": columns,
            "data": rows,
        }

    except Exception as e:
        return {
            "error": f"MySQL 查询执行失败：{e}",
            "sql": sql,
        }

    finally:
        conn.close()


def run_mysql_agent(client, question):
    """
    MySQL Agent 主函数：
    1. 获取数据库表结构
    2. 根据用户问题生成 SQL
    3. 做 SQL 安全检查
    4. 执行 SQL
    5. 返回查询结果
    """
    try:
        schema = get_mysql_schema()

        if not schema:
            return {
                "question": question,
                "schema": "",
                "generated_sql": "",
                "query_result": {
                    "error": "当前 MySQL 数据库中没有读取到表结构。",
                },
            }

        table_question_keywords = [
            "有哪些表",
            "有什么表",
            "所有表",
            "表名",
            "数据库结构",
            "表结构",
        ]

        if any(keyword in question for keyword in table_question_keywords):
            return {
                "question": question,
                "schema": schema,
                "generated_sql": "无需生成 SQL，直接返回数据库表结构。",
                "query_result": {
                    "sql": None,
                    "row_count": None,
                    "columns": ["schema"],
                    "data": [
                        {
                            "schema": schema,
                        }
                    ],
                },
            }

        sql = generate_mysql_sql(
            client=client,
            question=question,
            schema=schema,
        )

        query_result = execute_mysql_sql(sql)

        return {
            "question": question,
            "schema": schema,
            "generated_sql": sql,
            "query_result": query_result,
        }

    except Exception as e:
        return {
            "question": question,
            "schema": "",
            "generated_sql": "",
            "query_result": {
                "error": f"MySQL Agent 执行失败：{e}",
            },
        }