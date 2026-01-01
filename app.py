import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. 页面基础设置 (整容第一步) ---
st.set_page_config(page_title="Action Log", page_icon="⚡", layout="centered")

# --- 2. 注入 CSS (整容核心) ---
# 这段代码会覆盖 Streamlit 的默认丑样式
st.markdown("""
<style>
    /* 全局背景变白，字体优化 */
    .stApp {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 隐藏 Streamlit 顶部的红线和菜单，假装自己是原生 App */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 任务卡片样式 */
    .task-card {
        background-color: white;
        padding: 40px 20px;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #f3f4f6;
        transition: all 0.3s ease;
    }
    
    /* 卡片内的文字 */
    .task-text {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin: 20px 0;
        line-height: 1.4;
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 按钮样式优化 */
    .stButton > button {
        border-radius: 12px;
        height: 50px;
        font-weight: bold;
        border: none;
        transition: transform 0.1s;
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* 输入框美化 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        padding: 10px 15px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 数据库连接 ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("配置错误：请检查 Secrets 是否填对了 Google Sheets 链接")
    st.stop()

def load_data():
    try:
        df = conn.read(worksheet="tasks", ttl=0)
        return df
    except:
        return pd.DataFrame(columns=["id", "text", "type", "is_urgent", "status", "created_at", "completed_at"])

def update_db(df):
    conn.update(worksheet="tasks", data=df)

# --- 4. 逻辑处理 ---
df = load_data()

def add_task(text, task_type, is_urgent):
    new_task = pd.DataFrame([{
        "id": int(datetime.now().timestamp() * 1000),
        "text": text,
        "type": task_type,
        "is_urgent": is_urgent,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed_at": ""
    }])
    updated_df = pd.concat([df, new_task], ignore_index=True)
    update_db(updated_df)

def change_status(task_id, new_status):
    idx = df[df["id"] == task_id].index
    if not idx.empty:
        df.loc[idx, "status"] = new_status
        if new_status == "completed":
            df.loc[idx, "completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif new_status == "skipped":
            df.loc[idx, "status"] = "pending"
            df.loc[idx, "is_urgent"] = False
            df.loc[idx, "created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 移到队尾
        
        update_db(df)
        if new_status == "completed":
            st.balloons()
        st.rerun()

# --- 5. 界面渲染 (仿 React 版) ---

# 顶部栏：档案室入口
col_logo, col_archive = st.columns([8, 1])
with col_logo:
    st.markdown('<div style="font-weight:900; color:#cbd5e1; letter-spacing: 2px; font-size: 12px;">ACTION LOG</div>', unsafe_allow_html=True)
with col_archive:
    # 这里用一个简单的 emoji 作为按钮，Streamlit 的 sidebar 默认是汉堡菜单
    pass 

# 主内容区
active_tasks = df[df["status"] == "pending"].sort_values(by=["is_urgent", "created_at"], ascending=[False, True])

if len(active_tasks) > 0:
    current_task = active_tasks.iloc[0]
    
    # 动态样式计算
    border_color = "#f97316" if current_task['is_urgent'] else ("#3b82f6" if current_task['type'] == 'thinking' else "#f3f4f6")
    border_width = "4px" if current_task['is_urgent'] or current_task['type'] == 'thinking' else "1px"
    tag_bg = "#fff7ed" if current_task['is_urgent'] else ("#eff6ff" if current_task['type'] == 'thinking' else "#f3f4f6")
    tag_color = "#c2410c" if current_task['is_urgent'] else ("#1d4ed8" if current_task['type'] == 'thinking' else "#6b7280")
    tag_text = "🔥 URGENT" if current_task['is_urgent'] else ("🧠 THINKING" if current_task['type'] == 'thinking' else "⚡ ACTION")
    
    # 手写 HTML 卡片
    st.markdown(f"""
    <div class="task-card" style="border: {border_width} solid {border_color};">
        <div class="tag" style="background-color: {tag_bg}; color: {tag_color};">
            {tag_text}
        </div>
        <div class="task-text">
            {current_task['text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 按钮组 (使用 columns 布局)
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        # primary 也就是重点色，Streamlit 默认是红/粉，这里没法改太细，但比默认好
        if st.button("✅ 完成任务", use_container_width=True, type="primary"):
            change_status(current_task['id'], "completed")
    with c2:
        if st.button("⏭", help="跳过", use_container_width=True):
            change_status(current_task['id'], "skipped")
    with c3:
        if st.button("🗑️", help="删除", use_container_width=True):
            change_status(current_task['id'], "deleted")

else:
    # 空状态美化
    st.markdown("""
    <div class="task-card" style="border: 2px dashed #e5e7eb; background-color: #fafafa;">
        <div style="font-size: 40px; margin-bottom: 10px;">🎉</div>
        <div style="font-weight: bold; color: #9ca3af; font-size: 20px;">All Clear</div>
        <div style="color: #d1d5db; font-size: 14px; margin-top: 5px;">大脑已清空，请输入下一步行动</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 底部输入区
with st.container():
    with st.form("input_form", clear_on_submit=True):
        # 类型选择 (用 radio 模拟 tab)
        task_type = st.radio("Type", ["action", "thinking"], horizontal=True, label_visibility="collapsed", format_func=lambda x: "⚡ 行动" if x=="action" else "🧠 思考")
        
        c_input, c_urgent = st.columns([5, 1])
        with c_input:
            new_text = st.text_input("New Task", placeholder="下一步做什么？", label_visibility="collapsed")
        with c_urgent:
            is_urgent = st.checkbox("🔥", help="标记为重要/紧急")
            
        if st.form_submit_button("添加", use_container_width=True):
            if new_text:
                add_task(new_text, task_type, is_urgent)
                st.rerun()

# 侧边栏：档案室 (保持简单)
with st.sidebar:
    st.header("🏆 档案室")
    completed = df[df["status"] == "completed"].sort_values(by="completed_at", ascending=False)
    if not completed.empty:
        completed['day'] = pd.to_datetime(completed['completed_at']).dt.strftime('%m月%d日')
        for day, group in completed.groupby('day', sort=False):
            st.caption(day)
            for _, row in group.iterrows():
                icon = "🧠" if row['type'] == 'thinking' else "⚡"
                st.markdown(f"{icon} {row['text']}")
            st.divider()
    else:
        st.caption("暂无记录")
