import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🚀 最终强制连接版")

# 1. 认证 (只用 Secrets 里的机器人身份，忽略里面的链接)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ 机器人身份认证成功")
except Exception as e:
    st.error(f"身份配置出错: {e}")
    st.stop()

# 2. 强制指定链接 (这是你提供的真实链接，直接写死在这里)
MANUAL_URL = "https://docs.google.com/spreadsheets/d/1o6lZxWzJ6Roi83cKraXrOpuP7-OAwlImENGKyq6C1iw/edit"

st.write("正在强制连接表格...")

try:
    # 关键点：我们在这里直接告诉它地址，不让它去 Secrets 里猜
    df = conn.read(spreadsheet=MANUAL_URL, worksheet="tasks", ttl=0)
    st.success("✅ 终于连上了！读取成功！")
    st.dataframe(df.head())

    # 3. 写入测试
    if st.button("👉 点击这里测试写入"):
        new_row = pd.DataFrame([{
            "id": 999, 
            "text": "强制写入测试成功", 
            "type": "test", 
            "is_urgent": False, 
            "status": "pending",
            "created_at": "2024-01-01",
            "completed_at": ""
        }])
        
        # 写入时也强制指定链接
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=MANUAL_URL, worksheet="tasks", data=updated_df)
        st.balloons()
        st.success("🎉 写入成功！问题彻底解决！")
        
except Exception as e:
    st.error("❌ 还是报错，详细信息如下：")
    st.code(str(e))
