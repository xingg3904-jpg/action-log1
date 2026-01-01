import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🛡️ 极简连接模式")

# 1. 身份认证
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ 机器人已就位")
except Exception as e:
    st.error(f"❌ 认证失败: {e}")
    st.stop()

# 2. 关键修改：只填 ID，不填链接
SHEET_ID = "1o6lZxWzJ6Roi83cKraXrOpuP7-OAwlImENGKyq6C1iw"

st.write("正在通过 ID 读取表格...")

try:
    # 这里的修改：
    # 1. spreadsheet 只传 ID
    # 2. worksheet 传 0 (意思是“读取第1张表”，不管它叫 tasks 还是什么，这样绝对不会错)
    df = conn.read(spreadsheet=SHEET_ID, worksheet=0, ttl=0)
    
    st.success("🎉 成功了！读到了！")
    st.dataframe(df.head())

    # 3. 写入测试
    if st.button("👉 点击测试写入"):
        new_row = pd.DataFrame([{
            "id": 1001, 
            "text": "ID连接模式测试成功", 
            "type": "test", 
            "is_urgent": False, 
            "status": "pending",
            "created_at": "2024-01-01",
            "completed_at": ""
        }])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_ID, worksheet=0, data=updated_df)
        st.balloons()
        st.success("✅ 写入也成功了！")
        st.info("太棒了！请告诉我成功了，我把最终的漂亮界面代码发给你！")

except Exception as e:
    st.error("😭 还是不行，报错如下：")
    st.code(str(e))
