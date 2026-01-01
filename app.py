import streamlit as st
from pyairtable import Api
from datetime import datetime

# --- 1. 页面配置 ---
st.set_page_config(page_title="Action Log", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #ffffff;}
    header, footer {visibility: hidden;}
    .task-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Action Log (Airtable版)")

# --- 2. 连接 Airtable ---
try:
    # 从 Secrets 读取配置
    api_key = st.secrets["AIRTABLE"]["API_KEY"]
    base_id = st.secrets["AIRTABLE"]["BASE_ID"]
    table_name = "Table 1" # 你的表格名字叫 Table 1
    
    api = Api(api_key)
    table = api.table(base_id, table_name)
except Exception as e:
    st.error("⚠️ Secrets 配置未找到，请检查 Streamlit 后台 Secrets 是否填对")
    st.stop()

# --- 3. 功能函数 ---
def add_task(text, t_type, urgent):
    try:
        table.create({
            "text": text,
            "type": t_type,
            "is_urgent": urgent,
            "status": "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True
    except Exception as e:
        st.error(f"写入失败: {e}")
        return False

def get_tasks():
    try:
        # 获取所有数据
        return table.all(sort=["created_at"]) 
    except Exception as e:
        st.error(f"读取失败: {e}")
        return []

# --- 4. 界面逻辑 ---

# 输入区
with st.container():
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_text = st.text_input("任务", placeholder="下一步做什么？", label_visibility="collapsed")
        with col2:
            is_urgent = st.checkbox("🔥 紧急")
        
        task_type = st.radio("类型", ["action", "thinking"], horizontal=True, label_visibility="collapsed")
        
        if st.form_submit_button("添加任务", use_container_width=True):
            if new_text:
                if add_task(new_text, task_type, is_urgent):
                    st.success("✅ 已保存到 Airtable")
                    st.rerun()

# 列表展示区
st.markdown("---")
tasks = get_tasks()

if tasks:
    # 倒序显示（新的在上面）
    for record in reversed(tasks):
        data = record['fields']
        # 只显示未完成的 (pending)
        if data.get('status') == 'pending':
            is_urgent = data.get('is_urgent', False)
            t_type = data.get('type', 'action')
            
            icon = "🔥" if is_urgent else ("🧠" if t_type == 'thinking' else "⚡")
            border_color = "#ff4b4b" if is_urgent else "#e5e7eb"
            
            st.markdown(f"""
            <div class="task-card" style="border-left: 5px solid {border_color};">
                <div style="font-weight:bold; font-size:18px; color: #333;">
                    {icon} {data.get('text', '')}
                </div>
                <div style="color:#999; font-size:12px; margin-top:8px;">
                    {data.get('created_at', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.caption("表格是空的，开始你的第一条记录吧！")
