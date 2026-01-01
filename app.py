import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


# --- 1. 页面配置 ---
st.set_page_config(page_title="Action Log", page_icon="⚡", layout="centered")


# 自定义 CSS 让界面更像你的 V8 版本 (Zen White)
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-task-card {
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 2rem;
    }
    .action-tag { color: #f97316; font-weight: bold; font-size: 0.8em; text-transform: uppercase; }
    .thinking-tag { color: #3b82f6; font-weight: bold; font-size: 0.8em; text-transform: uppercase; }
    .big-text { font-size: 2rem; font-weight: 800; color: #1f2937; margin: 1rem 0; }
    /* 隐藏掉 Streamlit 默认的菜单以保持整洁 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 2. 数据库连接 (Google Sheets) ---
# 建立连接
conn = st.connection("gsheets", type=GSheetsConnection)


# 读取数据函数 (带缓存，减少请求次数)
def load_data():
    try:
        # 读取名为 "tasks" 的工作表
        df = conn.read(worksheet="tasks", ttl=0) # ttl=0 意味着每次刷新都重新拉取，保证实时同步
        return df
    except Exception:
        # 如果表是空的或者不存在，初始化一个空的 DataFrame
        return pd.DataFrame(columns=["id", "text", "type", "is_urgent", "status", "created_at", "completed_at"])


# --- 3. 逻辑处理函数 ---


def get_active_tasks(df):
    return df[df["status"] == "pending"].sort_values(by=["is_urgent", "created_at"], ascending=[False, True])


def add_task(text, task_type, is_urgent):
    df = load_data()
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
    conn.update(worksheet="tasks", data=updated_df)
    st.toast("任务已添加！", icon="📥")


def update_task_status(task_id, new_status):
    df = load_data()
    # 找到对应的行并更新状态
    idx = df[df["id"] == task_id].index
    if not idx.empty:
        df.loc[idx, "status"] = new_status
        if new_status == "completed":
            df.loc[idx, "completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果是 skip (跳过)，我们这里简单的策略是把它放到队尾
        # 在 Streamlit/Pandas 里，我们可以通过更新 created_at 来实现“排到最后”
        if new_status == "skipped":
            df.loc[idx, "status"] = "pending" # 状态还是 pending
            df.loc[idx, "is_urgent"] = False  # 跳过就不再紧急
            df.loc[idx, "created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 时间变新，排到后面
            st.toast("已跳过，下一个！", icon="⏭️")
        elif new_status == "completed":
             st.toast("太棒了！任务完成！", icon="🎉")
             st.balloons() # 放气球！
        elif new_status == "deleted":
            st.toast("已断舍离。", icon="🗑️")


        conn.update(worksheet="tasks", data=updated_df)


# --- 4. 界面渲染 ---


# 初始化数据
try:
    df = load_data()
except:
    st.error("无法连接到 Google Sheets，请检查 Secrets 配置。")
    st.stop()


# 侧边栏：档案室
with st.sidebar:
    st.title("📂 档案室")
    st.caption("Archives & History")
    
    completed_tasks = df[df["status"] == "completed"].sort_values(by="completed_at", ascending=False)
    
    if completed_tasks.empty:
        st.info("档案室是空的...去行动吧！")
    else:
        # 按日期分组显示
        completed_tasks['date_key'] = pd.to_datetime(completed_tasks['completed_at']).dt.strftime('%Y年%m月%d日')
        for date, group in completed_tasks.groupby('date_key', sort=False):
            st.markdown(f"**{date}**")
            for _, row in group.iterrows():
                icon = "⚡" if row['type'] == 'action' else "🧠"
                st.text(f"{icon} {row['text']}")
            st.divider()


# 主界面：Focus Funnel
st.title("Action Log")


active_tasks = get_active_tasks(df)
pending_count = len(active_tasks)


if pending_count > 0:
    st.caption(f"PENDING: {pending_count} TASKS")
    
    # 获取第一个任务（单线程）
    current_task = active_tasks.iloc[0]
    
    # 渲染任务卡片
    card_border = "orange" if current_task['is_urgent'] else ("blue" if current_task['type'] == 'thinking' else "gray")
    
    with st.container():
        st.markdown(f"""
        <div class="main-task-card" style="border-left: 10px solid {card_border};">
            <div class="{current_task['type']}-tag">
                { "🔥 URGENT" if current_task['is_urgent'] else current_task['type'].upper() }
            </div>
            <div class="big-text">{current_task['text']}</div>
        </div>
        """, unsafe_allow_html=True)


        # 操作按钮
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("✅ 完成", use_container_width=True, type="primary"):
                update_task_status(current_task['id'], "completed")
                st.rerun() # 刷新页面
        with col2:
            if st.button("⏭ 跳过", use_container_width=True):
                update_task_status(current_task['id'], "skipped")
                st.rerun()
        with col3:
            if st.button("🗑️ 删除", use_container_width=True):
                update_task_status(current_task['id'], "deleted")
                st.rerun()


else:
    # 空状态
    st.markdown("""
    <div class="main-task-card" style="border: 2px dashed #ddd;">
        <div style="font-size: 3rem;">🎉</div>
        <div class="big-text" style="color: #bbb;">All Clear</div>
        <div style="color: #999;">准备就绪，输入下一步行动</div>
    </div>
    """, unsafe_allow_html=True)


# 底部：输入区
st.divider()
with st.form("add_task_form", clear_on_submit=True):
    col_type, col_urgent = st.columns(2)
    with col_type:
        task_type = st.radio("类型", ["action", "thinking"], horizontal=True, label_visibility="collapsed", format_func=lambda x: "⚡ 行动" if x=="action" else "🧠 思考")
    with col_urgent:
        is_urgent = st.checkbox("🔥 重要/紧急")
        
    new_task_text = st.text_input("输入任务...", placeholder="下一步做什么？")
    submitted = st.form_submit_button("添加任务", use_container_width=True)


    if submitted and new_task_text:
        add_task(new_task_text, task_type, is_urgent)
        st.rerun()


# 破冰行动
if st.button("我卡住了 / 脑子转不动了?"):
    import random
    steps = ["深呼吸 5 秒", "喝一口水", "转动一下脖子", "把手机反扣在桌上", "闭眼数到 10"]
    st.toast(f"破冰微行动: {random.choice(steps)}", icon="🧊")