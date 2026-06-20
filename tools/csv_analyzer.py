import json
import os
import pandas as pd
import matplotlib.pyplot as plt


def analyze_csv_with_chart(file_path):
    """
    读取 CSV 文件，自动分析数据，并生成图表。
    """
    try:
        df = pd.read_csv(file_path)

        os.makedirs("charts", exist_ok=True)

        result = {
            "基础信息": {
                "文件名": file_path,
                "行数": len(df),
                "列数": len(df.columns),
                "字段名": list(df.columns),
                "前5行数据": df.head().to_dict(orient="records")
            },
            "数值列统计": {},
            "分类列统计": {},
            "生成的图表": []
        }

        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        category_columns = df.select_dtypes(include=["object"]).columns.tolist()

        result["基础信息"]["数值列"] = numeric_columns
        result["基础信息"]["分类列"] = category_columns

        for col in numeric_columns:
            result["数值列统计"][col] = {
                "数量": int(df[col].count()),
                "总和": float(df[col].sum()),
                "平均值": float(df[col].mean()),
                "最大值": float(df[col].max()),
                "最小值": float(df[col].min())
            }

        for category_col in category_columns[:2]:
            result["分类列统计"][category_col] = {}

            for numeric_col in numeric_columns[:2]:
                group_result = (
                    df.groupby(category_col)[numeric_col]
                    .sum()
                    .sort_values(ascending=False)
                )

                result["分类列统计"][category_col][numeric_col + "_分组求和"] = group_result.to_dict()

                chart_file = f"charts/{category_col}_{numeric_col}_bar.png"

                plt.figure(figsize=(8, 5))
                group_result.plot(kind="bar")
                plt.title(f"{category_col} 按 {numeric_col} 分组求和")
                plt.xlabel(category_col)
                plt.ylabel(numeric_col)
                plt.tight_layout()
                plt.savefig(chart_file)
                plt.close()

                result["生成的图表"].append(chart_file)

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"CSV 分析或画图出错：{e}"