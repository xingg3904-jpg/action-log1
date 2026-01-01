import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🛠️ 最终修复：强制导航模式")

# 1. 连接服务 (Secrets 里只要有 Service Account 就行)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ 账号认证成功")
except Exception as e:
    st.error(f"❌ 账号配置出错: {e}")
    st.stop()

# --- 关键修改：直接在这里填入完整链接，不依赖 Secrets ---
# 这是你刚才提供的真实链接
MANUAL_URL = "https://docs.google.com/spreadsheets/d/1o6lZxWzJ6Roi83cKraXrOpuP7-OAwlImENGKyq6C1iw/edit"

# 2. 尝试读取
st.write("正在精准定位表格...")
try:
    # 强制指定 spreadsheet 链接，确保万无一失
    df = conn.read(spreadsheet=MANUAL_URL, worksheet="tasks", ttl=0)
    st.success("✅ 终于连上了！表格读取成功！")
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ 还是读不到，请看下方详细原因：")
    st.warning("⚠️ 请检查：你的 Google 表格左下角的工作表名字，真的是叫 'tasks' 吗？有没有多余的空格？")
    st.code(str(e))
    st.stop()

# 3. 写入测试
if st.button("d(^_^o) 点击测试写入"):
    try:
        new_data = pd.DataFrame([{
            "id": 888, "text": "连接修复成功", "type": "test", 
            "is_urgent": False, "status": "pending", 
            "created_at": "2024-01-01", "completed_at": ""
        }])
        # 同样强制指定链接
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(spreadsheet=MANUAL_URL, worksheet="tasks", data=updated_df)
        st.balloons()
        st.success("🎉 写入成功！你的 App 复活了！")
        st.info("💡 下一步：确信成功后，我会给你原本的漂亮界面代码。")
    except Exception as e:
        st.error("❌ 写入失败")
        st.code(str(e))
