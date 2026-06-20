# 基于 DeepSeek 的智能 CSV 数据分析 Agent

## 一、项目简介

本项目是一个基于 DeepSeek API、Python、Pandas、Matplotlib 和 Streamlit 实现的智能 CSV 数据分析 Agent。

用户可以在网页端上传 CSV 文件，系统会自动识别数据字段类型，完成基础统计分析、分类维度分析、图表生成，并调用大语言模型自动生成中文数据分析报告，最终支持 HTML 报告下载。

本项目主要面向数据分析、业务分析和 AI 应用开发场景，适合用于销售数据、成绩数据、订单数据、用户数据等表格型数据的快速分析。

---

## 二、技术栈

* Python
* DeepSeek API
* OpenAI SDK
* Streamlit
* Pandas
* Matplotlib
* python-dotenv
* HTML / CSS

---

## 三、核心功能

### 1. CSV 文件上传

用户可以通过 Streamlit 网页界面上传 CSV 文件。

### 2. 自动识别字段类型

系统会自动识别：

* 数值列
* 分类列
* 字段名称
* 数据行数
* 数据列数
* 前 5 行样例数据

### 3. 自动统计分析

对数值列自动计算：

* 数量
* 总和
* 平均值
* 最大值
* 最小值

### 4. 分类维度分析

对分类字段和数值字段进行分组统计，例如：

* 按产品统计销售额
* 按地区统计销售额
* 按班级统计成绩
* 按性别统计成绩

### 5. 自动生成图表

系统会根据分类列和数值列自动生成柱状图，并保存到 `charts/` 文件夹。

### 6. LLM 自动生成分析报告

系统会将 Python 工具计算出的结构化结果传递给 DeepSeek，由大模型生成中文数据分析报告。

报告包括：

* 数据概览
* 核心指标分析
* 分类维度分析
* 关键发现
* 业务建议 / 学习建议 / 运营建议

### 7. HTML 报告导出

系统会将分析文字和图表整合成 HTML 报告，用户可以在网页端下载。

---

## 四、项目结构

```text
python-project/
│
├── app.py                  # Streamlit 网页入口
├── main.py                 # 命令行版本入口
├── .env                    # API Key 配置文件
├── requirements.txt        # 项目依赖
├── README.md               # 项目说明文档
├── sales.csv               # 示例销售数据
├── students.csv            # 示例成绩数据
│
├── tools/
│   ├── __init__.py
│   └── csv_analyzer.py     # CSV 分析与图表生成工具
│
├── reports/
│   ├── __init__.py
│   └── html_report.py      # HTML 报告生成模块
│
├── charts/                 # 自动生成的图表
│
├── output/                 # 自动生成的 HTML 报告
│
└── practice/               # 学习过程中的练习代码
```

---

## 五、运行方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录新建 `.env` 文件，并写入：

```env
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

### 3. 启动网页应用

```bash
streamlit run app.py
```

启动后，在浏览器中打开：

```text
http://localhost:8501
```

### 4. 使用方式

1. 上传 CSV 文件
2. 点击“开始分析”
3. 查看自动生成的数据分析报告
4. 查看图表
5. 下载 HTML 报告

---

## 六、Agent 工作流程

本项目的 Agent 工作流程如下：

```text
用户上传 CSV 文件
        ↓
Python 读取 CSV 数据
        ↓
Pandas 自动识别字段类型
        ↓
Python 工具完成统计分析
        ↓
Matplotlib 自动生成图表
        ↓
将结构化分析结果传给 DeepSeek
        ↓
DeepSeek 生成中文数据分析报告
        ↓
系统生成 HTML 报告
        ↓
用户下载报告
```

---

## 七、项目亮点

### 1. 结合大语言模型与传统数据分析工具

本项目不是直接让大模型“凭空分析”，而是先使用 Python 和 Pandas 完成真实的数据计算，再将结构化结果交给 DeepSeek 生成分析报告。

这种方式可以减少大模型在数值计算上的幻觉，提高分析结果的可靠性。

### 2. 具备 Agent 工具调用思想

项目中将 CSV 分析、图表生成、HTML 报告生成封装为独立工具模块，形成了“大模型负责理解与表达，Python 工具负责真实执行”的 Agent 应用结构。

### 3. 支持网页端交互

通过 Streamlit 实现了 CSV 上传、报告展示、图表展示和 HTML 报告下载，提升了项目的可展示性和易用性。

### 4. 适合数据分析场景

项目可以用于销售数据、成绩数据、订单数据、用户数据等表格型数据分析，具有较强的业务扩展空间。

---

## 八、后续优化方向

* 支持 Excel 文件上传
* 支持更多图表类型，例如折线图、饼图、散点图
* 支持用户自定义分析目标
* 支持多轮追问分析结果
* 接入数据库，实现 SQL 数据分析
* 增加 RAG 知识库能力
* 使用 LangGraph 实现更完整的 Agent 工作流
* 支持报告导出为 PDF
* 部署到云端，形成在线数据分析工具

---

## 九、项目总结

本项目实现了一个从 CSV 数据读取、自动统计分析、图表生成，到大模型生成分析报告和 HTML 报告下载的完整流程。

通过本项目，我掌握了 DeepSeek API 调用、Prompt 设计、Agent 工具调用思想、Pandas 数据分析、Matplotlib 可视化和 Streamlit 网页开发等能力，并初步具备了开发 LLM 数据分析应用的实践经验。
