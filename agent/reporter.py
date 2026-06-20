import os


def save_html_report(report_content: str, chart_files: list[str]) -> str:
    """
    将最终分析内容和图表保存为 HTML 报告。
    """
    os.makedirs("output", exist_ok=True)

    report_file = "output/report.html"

    formatted_content = report_content.replace("\n", "<br>")

    chart_html = ""

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

        <h2>图表展示</h2>
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
    Reporter Agent：根据执行结果生成最终报告。
    """
    prompt = f"""
请根据下面的执行结果，生成一份清晰、专业的中文报告。

任务类型：
{task_type}

执行结果：
{execution_result}

要求：
- 如果是数据分析任务，请输出数据概览、核心指标、关键发现和建议。
- 如果是知识库问答任务，请清晰回答问题，并说明依据。
- 如果是普通对话，请自然回答。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业报告生成 Agent。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content