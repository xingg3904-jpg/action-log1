import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🛠️ 连接诊断模式")

# 1. 检查 Secrets 是否读到了
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ 第一步：Secrets 读取成功")
except Exception as e:
    st.error(f"❌ 第一步失败：Secrets 配置格式有误\n{e}")
    st.stop()

# 2. 尝试连接表格
st.write("正在尝试连接 Google 表格...")
try:
    # 强制读取一次，不使用缓存
    df = conn.read(worksheet="tasks", ttl=0)
    st.success("✅ 第二步：读取表格成功！")
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ 第二步失败：无法读取表格")
    st.code(str(e)) # 这里会显示真正的错误原因
    st.stop()

# 3. 尝试写入测试
if st.button("🧪 点击测试写入数据"):
    try:
        # 创建一个测试数据
        new_data = pd.DataFrame([{
            "id": 123, "text": "测试写入", "type": "test", 
            "is_urgent": False, "status": "pending", 
            "created_at": "2024-01-01", "completed_at": ""
        }])
        # 尝试追加
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="tasks", data=updated_df)
        st.balloons()
        st.success("🎉 第三步：写入成功！问题已解决！")
    except Exception as e:
        st.error("❌ 第三步失败：无法写入")
        # 关键！打印出具体的 API 报错信息
        st.warning("👇 请截图下面这段报错信息发给我：")
        st.code(str(e))
