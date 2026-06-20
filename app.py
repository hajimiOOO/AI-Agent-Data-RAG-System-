import json
import os
import shutil

import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent.planner import plan_task
from agent.executor import execute_task
from agent.critic import check_result
from agent.reporter import generate_report, save_html_report
from rag.vector_store import load_document, split_text, build_vector_db


# =========================
# 1. 初始化环境
# =========================

load_dotenv(override=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    st.error("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件是否配置正确。")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


# =========================
# 2. Streamlit 页面配置
# =========================

st.set_page_config(
    page_title="AI Multi-Agent System",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 AI Multi-Agent System")
st.write("基于 DeepSeek 的多智能体数据分析与知识库问答系统。")


# =========================
# 3. Session State 初始化
# =========================

if "rag_collection" not in st.session_state:
    st.session_state.rag_collection = None

if "rag_chunks" not in st.session_state:
    st.session_state.rag_chunks = []

if "csv_file_path" not in st.session_state:
    st.session_state.csv_file_path = None


# =========================
# 4. 侧边栏：上传 CSV 和知识库
# =========================

st.sidebar.header("📁 数据准备")

csv_file = st.sidebar.file_uploader(
    "上传 CSV 文件",
    type=["csv"],
)

if csv_file is not None:
    os.makedirs("uploads", exist_ok=True)
    csv_path = os.path.join("uploads", csv_file.name)

    with open(csv_path, "wb") as f:
        f.write(csv_file.getbuffer())

    st.session_state.csv_file_path = csv_path
    st.sidebar.success(f"CSV 已上传：{csv_file.name}")


doc_file = st.sidebar.file_uploader(
    "上传知识库文档 txt / md",
    type=["txt", "md"],
)

if doc_file is not None:
    os.makedirs("knowledge_uploads", exist_ok=True)
    doc_path = os.path.join("knowledge_uploads", doc_file.name)

    with open(doc_path, "wb") as f:
        f.write(doc_file.getbuffer())

    st.sidebar.success(f"文档已上传：{doc_file.name}")

    if st.sidebar.button("构建 RAG 知识库"):
        with st.spinner("正在构建向量数据库..."):
            text = load_document(doc_path)
            chunks = split_text(text)

            if os.path.exists("rag_chroma_db"):
                shutil.rmtree("rag_chroma_db")

            collection = build_vector_db(chunks)

            st.session_state.rag_collection = collection
            st.session_state.rag_chunks = chunks

        st.sidebar.success(f"知识库构建完成，共 {len(chunks)} 个 chunk。")


# =========================
# 5. 用户输入任务
# =========================

st.subheader("💬 输入任务")

user_input = st.text_area(
    "请输入你的任务，例如：分析这个 CSV / 这个项目用了什么技术栈？",
    height=120,
)


# =========================
# 6. 执行 Agent
# =========================

if st.button("🚀 执行 Agent"):

    if not user_input.strip():
        st.warning("请先输入任务。")
        st.stop()

    # 1. Planner Agent
    with st.spinner("Planner Agent 正在规划任务..."):
        plan = plan_task(client, user_input)

    st.subheader("🧠 Planner Agent 任务规划")
    st.json(plan)

    # 2. Executor Agent
    with st.spinner("Executor Agent 正在执行任务..."):
        execution = execute_task(
            client=client,
            plan=plan,
            user_input=user_input,
            csv_file_path=st.session_state.csv_file_path,
            rag_collection=st.session_state.rag_collection,
        )

    st.subheader("⚙️ Executor Agent 执行结果")

    task_type = execution.get("type")
    raw = execution.get("raw")
    result = execution.get("result")

    if task_type == "csv":
        try:
            result_dict = json.loads(result)
            st.json(result_dict)
        except Exception:
            st.write(result)

    elif task_type == "rag":
        st.write(result)

        if raw and raw.get("retrieved_chunks"):
            st.subheader("🔍 RAG 检索片段")
            for i, chunk in enumerate(raw["retrieved_chunks"], start=1):
                with st.expander(f"资料片段 {i}"):
                    st.write(chunk)

    else:
        st.write(result)

    # 3. Critic Agent
    with st.spinner("Critic Agent 正在评审结果..."):
        review = check_result(client, str(result))

    st.subheader("🔍 Critic Agent 评审")
    st.write(review)

    # 4. Reporter Agent
    with st.spinner("Reporter Agent 正在生成最终报告..."):
        final_report = generate_report(
            client=client,
            task_type=task_type,
            execution_result=str(result),
        )

    st.subheader("📝 Reporter Agent 最终报告")
    st.write(final_report)

    # 5. 展示图表
    chart_files = []

    if task_type == "csv":
        try:
            result_dict = json.loads(result)
            chart_files = result_dict.get("生成的图表", [])
        except Exception:
            chart_files = []

        if chart_files:
            st.subheader("📈 自动生成图表")
            for chart_file in chart_files:
                if os.path.exists(chart_file):
                    st.image(
                        chart_file,
                        caption=chart_file,
                        use_container_width=True,
                    )

    # 6. 生成 HTML 报告
    report_file = save_html_report(final_report, chart_files)

    if os.path.exists(report_file):
        with open(report_file, "rb") as f:
            st.download_button(
                label="📥 下载 HTML 报告",
                data=f,
                file_name="agent_report.html",
                mime="text/html",
            )