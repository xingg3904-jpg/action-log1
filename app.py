import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. 页面基础设置 ---
st.set_page_config(page_title="Action Log", page_icon="⚡", layout="centered")

# --- 2. 注入 CSS (美化界面) ---
st.markdown("""
<style>
    .stApp {background-color: #ffffff;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .task-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Action Log (直连版)")

# --- 3. 核弹级配置：直接在代码里写死钥匙 ---
# 既然 Secrets 不听话，我们就把钥匙直接放在这
credentials_dict = {
  "type": "service_account",
  "project_id": "ringed-cell-483007-a2",
  "private_key_id": "325459e370db378a0425dee5711ac9e430337444",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2E6ngQdh5ZLA1\nB6cvDre8i7UkfUVUcIToFDLNcOlUUG4ztBxHv9/AKdnNJW3KtIq4LvWrKf3qIoJl\nvWqBe6lVH3KeTiLnxWR/2PgaPHF/ql/6Idc5IUD9TJtp6Mvky8U1B36aDRfTFCKv\n5GsJrddPQMxYG6M5ESS/7ybDMJq/qxsqs4gbVM0GBLz7kA17fjjLsR6fsZ9CVaQD\nsxybQ1Fvkk3uzlsr2ivT2yuVNMx3FYSOK2iAV78vBshqsBT+HLpCKXbkHyNgkMmB\npH5Goc7nauPznqn9xpT4xcu12FrkyIWOgbdEGpoAGJ8hytGjrT9alCsZQ0Kp7+gM\naW0cJAiRAgMBAAECggEAAxLpvofmDMXwJUkL38MWw4JeocR9T+ZhZrNL7e95ektW\n/PJOEEEImOuBSjxsR4HiSKc++Fo1DPJIXh7Ym4yCqJWnafhFkGui8syZ2FmLt1J2\nnIKx6ec/kWHXytiGXrEOUy2dS80A9Aw7j1l4HCRORaqBTf3TdN0ZpXrhs5BlwGrE\nC43SAyHgJvphYfdbwy8cQ7ZdbiQ2fg2xB2so9i/XD8duimpakD2uhjI5pCtJ4CW5\nc5Nb+9kXFU9Hmx5A7dlKWLq90cPs968aaU9SJqSkd7bnatf5BZI3zOGI2WVxC1pr\n0TDkWZNPzyl6vUTJ2RXxjzioEre3jYblb1W4rpnKJQKBgQDihPRnenzWWRW54Uxq\n+LbKYbv6yM8HsGwvXNDwLrrPvahj9QXCpoXUxBWzcx0c353gY0xTRlJ1F0M51Wjx\ny3lAjMTH042jpIgHem9mY3L0CroS8x9LIn+9xJEfQTfEY1t7Bx5a81CEkCyaOSwX\niVu0Em4xsisejDYQqkRhYHGSPQKBgQDNxf8+BjGTaOucu/XqiV04vJtGUCvF13m4\nRAqibGLjikXGJcUNiZKO0DNVhzOTar/xdI0VmlVwaLNcW/ehCyNODPzmUuXSHjzV\nmYTtef4a4+6BgUjautQRi8gkk2kNP+9OS+oNLDavMZN2g/bfxPMqkQBnVg86cglK\nMIkwmhiY5QKBgFdzBrvwQMOrrsSNIyhlDoSBSMYfwjVwucNrLMqc78gFqz2zuV6V\nVTN34/zcYw/jkJqxGyVHD8xeh7iLGDHI4O23qryOgq77dPyWGu3HVPi8L2vjamBi\nWDiV64TKc9IgnY+YhvKL3rjexCliCxCnGb0iJGKRKy5m6PR0F2QUjKPtAoGBAJZ0\nBJInGSx89Hje/YmE8kI/tRCOIdNAH2FZbqUftpZETYv5pcCmLCB7nm0Us+M/lCRJ\nYba/52SPSUVogQChEilJWchWKG+faD+NRiIUpnSm34aVLt2u6MwDdk038wGbE7Ad\n1X3YLAugpf9rsaAfcuRWrQLha7UCGETEhCqjIQT5AoGADXHzNpXvCLJKfApl4x61\n606E8xTi5iCDVUu0dL3r0bPiNoyBTYXLDW0bEzaJ/w0LE+eVqmZyjxfYIYsPaSXe\nAzgwSgLk6s+YY/ncvZ58w+yUDIh3TjBkcmMlYxvTNHHRuCl2dZJs7GV96Ece6aKU\nEmQ6g6u5G6CTo53Mv7OW7jA=\\n-----END PRIVATE KEY-----\\n",
  "client_email": "my-app@ringed-cell-483007-a2.iam.gserviceaccount.com",
  "client_id": "102026785703103060711",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-app%40ringed-cell-483007-a2.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

SPREADSHEET_ID = "1o6lZxWzJ6Roi83cKraXrOpuP7-OAwlImENGKyq6C1iw"

# --- 4. 核心功能函数 ---
def get_worksheet():
    # 使用 gspread 直接连接，不走 Streamlit 的 connection
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    client = gspread.authorize(creds)
    # 打开表格，获取第1张工作表
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def load_data():
    try:
        sheet = get_worksheet()
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"读取失败: {e}")
        return pd.DataFrame()

def add_task_to_sheet(text, task_type, is_urgent):
    try:
        sheet = get_worksheet()
        # 准备要写入的一行数据
        new_row = [
            int(datetime.now().timestamp() * 1000), # id
            text,                                   # text
            task_type,                              # type
            "TRUE" if is_urgent else "FALSE",       # is_urgent
            "pending",                              # status
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # created_at
            ""                                      # completed_at
        ]
        # 追加到最后一行
        sheet.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"写入失败: {e}")
        return False

# --- 5. 界面逻辑 ---

# 读取数据
df = load_data()

# 输入区
with st.container():
    with st.form("input_form", clear_on_submit=True):
        task_type = st.radio("Type", ["action", "thinking"], horizontal=True, label_visibility="collapsed", format_func=lambda x: "⚡ 行动" if x=="action" else "🧠 思考")
        c1, c2 = st.columns([5, 1])
        with c1:
            new_text = st.text_input("New Task", placeholder="下一步做什么？", label_visibility="collapsed")
        with c2:
            is_urgent = st.checkbox("🔥", help="标记为重要/紧急")
            
        if st.form_submit_button("添加任务", use_container_width=True):
            if new_text:
                if add_task_to_sheet(new_text, task_type, is_urgent):
                    st.success("✅ 添加成功！")
                    st.rerun()

# 列表展示区
st.markdown("---")
if not df.empty:
    # 过滤未完成的任务
    active_tasks = df[df["status"] == "pending"]
    if not active_tasks.empty:
        for index, row in active_tasks.iterrows():
            # 简单的卡片显示
            border = "2px solid #f97316" if row.get('is_urgent') == "TRUE" else "1px solid #e5e7eb"
            icon = "🔥" if row.get('is_urgent') == "TRUE" else ("🧠" if row['type'] == 'thinking' else "⚡")
            
            st.markdown(f"""
            <div class="task-card" style="border: {border};">
                <div style="font-size: 20px; font-weight: bold;">{icon} {row['text']}</div>
                <div style="color: gray; font-size: 12px; margin-top: 5px;">{row['created_at']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🎉 所有任务都完成了！")
else:
    st.write("表格是空的，或者读取出错了。")
