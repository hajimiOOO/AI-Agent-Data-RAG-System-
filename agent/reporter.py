import os


def save_html_report(report_content: str, chart_files: list[str] | None = None) -> str:
    """
    将最终分析内容和图表保存为 HTML 报告。
    """
    os.makedirs("output", exist_ok=True)

    if chart_files is None:
        chart_files = []

    report_file = "output/report.html"

    formatted_content = report_content.replace("\n", "<br>")

    chart_html = ""

    if chart_files:
        chart_html += "<h2>图表展示</h2>"

        for chart_file in chart_files:
            chart_html += f"""
            <div class="chart-card">
                <h3>{chart_file}</h3>
                <img src="../{chart_file}" alt="{chart_file}">
            </div>
            """

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AI Agent 分析报告</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.8;
            padding: 40px;
        }}

        .container {{
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }}

        h1 {{
            text-align: center;
            color: #2c3e50;
        }}

        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}

        .report-content {{
            font-size: 16px;
        }}

        .chart-card {{
            margin-top: 30px;
            padding: 20px;
            background: #fafafa;
            border-radius: 12px;
            border: 1px solid #eee;
        }}

        .chart-card img {{
            width: 100%;
            max-width: 850px;
            display: block;
            margin: 0 auto;
            border-radius: 8px;
        }}

        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #888;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Agent 分析报告</h1>

        <div class="report-content">
            {formatted_content}
        </div>

        {chart_html}

        <div class="footer">
            本报告由 DeepSeek + Python Multi-Agent System 自动生成
        </div>
    </div>
</body>
</html>
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)

    return report_file


def generate_report(client, task_type: str, execution_result: str) -> str:
    """
    Reporter Agent：根据 Executor Agent 的执行结果生成最终报告。

    支持任务类型：
    - csv：CSV 数据分析
    - rag：知识库问答
    - mysql：MySQL 查询
    - chat：普通对话
    """
    prompt = f"""
请根据下面的执行结果，生成一份清晰、专业、适合展示的中文报告。

任务类型：
{task_type}

执行结果：
{execution_result}

请根据不同任务类型生成对应内容：

1. 如果任务类型是 csv：
请输出：
- 数据概览
- 核心指标
- 分组统计发现
- 图表含义说明
- 业务建议

2. 如果任务类型是 rag：
请输出：
- 用户问题的直接回答
- 回答依据
- 如果资料不足，请明确说明资料中没有提到，不能编造

3. 如果任务类型是 mysql：
请输出：
- 用户查询意图
- 生成 SQL 的作用说明
- 查询结果解读
- 数据分析结论
- 业务含义或建议

4. 如果任务类型是 chat：
请自然、清晰地回答用户问题。

要求：
- 使用中文
- 结构清晰
- 不要编造执行结果里没有的信息
- 不要输出 Markdown 表格，尽量用分点说明
- 语气专业但容易理解
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的数据分析与报告生成 Agent，擅长把工具执行结果整理成清晰报告。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content