import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🛡️ 核弹级修复：直连模式")

# --- 1. 这里是你的钥匙 (直接写在代码里，绕过 Secrets) ---
# 我已经把你之前提供的 JSON 信息填好了
keys = {
  "type": "service_account",
  "project_id": "ringed-cell-483007-a2",
  "private_key_id": "325459e370db378a0425dee5711ac9e430337444",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2E6ngQdh5ZLA1\nB6cvDre8i7UkfUVUcIToFDLNcOlUUG4ztBxHv9/AKdnNJW3KtIq4LvWrKf3qIoJl\nvWqBe6lVH3KeTiLnxWR/2PgaPHF/ql/6Idc5IUD9TJtp6Mvky8U1B36aDRfTFCKv\n5GsJrddPQMxYG6M5ESS/7ybDMJq/qxsqs4gbVM0GBLz7kA17fjjLsR6fsZ9CVaQD\nsxybQ1Fvkk3uzlsr2ivT2yuVNMx3FYSOK2iAV78vBshqsBT+HLpCKXbkHyNgkMmB\npH5Goc7nauPznqn9xpT4xcu12FrkyIWOgbdEGpoAGJ8hytGjrT9alCsZQ0Kp7+gM\naW0cJAiRAgMBAAECggEAAxLpvofmDMXwJUkL38MWw4JeocR9T+ZhZrNL7e95ektW\n/PJOEEEImOuBSjxsR4HiSKc++Fo1DPJIXh7Ym4yCqJWnafhFkGui8syZ2FmLt1J2\nnIKx6ec/kWHXytiGXrEOUy2dS80A9Aw7j1l4HCRORaqBTf3TdN0ZpXrhs5BlwGrE\nC43SAyHgJvphYfdbwy8cQ7ZdbiQ2fg2xB2so9i/XD8duimpakD2uhjI5pCtJ4CW5\nc5Nb+9kXFU9Hmx5A7dlKWLq90cPs968aaU9SJqSkd7bnatf5BZI3zOGI2WVxC1pr\n0TDkWZNPzyl6vUTJ2RXxjzioEre3jYblb1W4rpnKJQKBgQDihPRnenzWWRW54Uxq\n+LbKYbv6yM8HsGwvXNDwLrrPvahj9QXCpoXUxBWzcx0c353gY0xTRlJ1F0M51Wjx\ny3lAjMTH042jpIgHem9mY3L0CroS8x9LIn+9xJEfQTfEY1t7Bx5a81CEkCyaOSwX\niVu0Em4xsisejDYQqkRhYHGSPQKBgQDNxf8+BjGTaOucu/XqiV04vJtGUCvF13m4\nRAqibGLjikXGJcUNiZKO0DNVhzOTar/xdI0VmlVwaLNcW/ehCyNODPzmUuXSHjzV\nmYTtef4a4+6BgUjautQRi8gkk2kNP+9OS+oNLDavMZN2g/bfxPMqkQBnVg86cglK\nMIkwmhiY5QKBgFdzBrvwQMOrrsSNIyhlDoSBSMYfwjVwucNrLMqc78gFqz2zuV6V\nVTN34/zcYw/jkJqxGyVHD8xeh7iLGDHI4O23qryOgq77dPyWGu3HVPi8L2vjamBi\nWDiV64TKc9IgnY+YhvKL3rjexCliCxCnGb0iJGKRKy5m6PR0F2QUjKPtAoGBAJZ0\nBJInGSx89Hje/YmE8kI/tRCOIdNAH2FZbqUftpZETYv5pcCmLCB7nm0Us+M/lCRJ\nYba/52SPSUVogQChEilJWchWKG+faD+NRiIUpnSm34aVLt2u6MwDdk038wGbE7Ad\n1X3YLAugpf9rsaAfcuRWrQLha7UCGETEhCqjIQT5AoGADXHzNpXvCLJKfApl4x61\n606E8xTi5iCDVUu0dL3r0bPiNoyBTYXLDW0bEzaJ/w0LE+eVqmZyjxfYIYsPaSXe\nAzgwSgLk6s+YY/ncvZ58w+yUDIh3TjBkcmMlYxvTNHHRuCl2dZJs7GV96Ece6aKU\nEmQ6g6u5G6CTo53Mv7OW7jA=\n-----END PRIVATE KEY-----\n",
  "client_email": "my-app@ringed-cell-483007-a2.iam.gserviceaccount.com",
  "client_id": "102026785703103060711",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-app%40ringed-cell-483007-a2.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# --- 2. 强制连接 ---
# 注意：我们在这里直接把 keys 塞给了连接器，强迫它使用这个身份
try:
    conn = st.connection("gsheets", type=GSheetsConnection, service_account=keys)
    st.success("✅ 强制身份认证成功！")
except Exception as e:
    st.error(f"❌ 认证失败: {e}")
    st.stop()

# --- 3. 你的表格 ID ---
SHEET_ID = "1o6lZxWzJ6Roi83cKraXrOpuP7-OAwlImENGKyq6C1iw"

st.write("正在写入表格...")

try:
    # 先读取
    df = conn.read(spreadsheet=SHEET_ID, worksheet=0, ttl=0)
    st.write("当前数据预览：")
    st.dataframe(df.head())

    # 写入测试
    if st.button("🚀 点击发射 (写入测试)"):
        new_row = pd.DataFrame([{
            "id": 9999, 
            "text": "核弹级修复成功", 
            "type": "test", 
            "is_urgent": False, 
            "status": "pending",
            "created_at": "2024-01-01",
            "completed_at": ""
        }])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        # 写入
        conn.update(spreadsheet=SHEET_ID, worksheet=0, data=updated_df)
        
        st.balloons()
        st.success("🎉 终于写入成功了！所有的配置都通了！")
        st.info("快告诉我成功了，我把之前那个漂亮的界面（带这个修复补丁）发给你！")

except Exception as e:
    st.error("😭 还是不行，报错如下：")
    st.code(str(e))
