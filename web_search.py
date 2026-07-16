import streamlit as st
from google import genai
from google.genai import types
import json

# 頁面標題設定
st.set_page_config(page_title="AI 網紅雷達", layout="centered")
st.title("🛰️ AI 全網自動網紅搜尋器")
st.write("輸入你想尋找的任何類型或網紅名稱，AI 將自動連網搜尋並整理給您！")

# 從 Streamlit 後台安全取得 API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 網站管理員尚未設定後台 API Key，請至 Streamlit Secrets 設定。")
    st.stop()

# 直接讓使用者輸入想搜尋的內容（每個人來都可以直接用！）
user_query = st.text_input("💡 想要搜尋什麼？（例如：風格幽默的旅遊 Vlogger、美妝網紅、或是特定網紅名字...）")

if user_query:
    with st.spinner("🚀 AI 正在連網搜尋並分析中，請稍候..."):
        try:
            # 提示詞引導
            prompt = f"""
            請上網搜尋符合以下條件的網紅（KOL / YouTuber / Instagrammer / TikToker）："{user_query}"。
            請找出 3-5 位最符合的網紅，並以嚴格的 JSON 格式輸出，不要有任何額外的文字解釋。格式必須如下：
            [
              {{
                "name": "網紅名字",
                "platform": "平台（如 YouTube, Instagram, TikTok）",
                "fans": "粉絲數/訂閱數",
                "content": "一小段關於他拍什麼影片、風格特色的介紹",
                "url": "他的頻道或個人主頁完整連結"
              }}
            ]
            """
            
            # 呼叫 Gemini 連網搜尋
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json"
                ),
            )
            
            # 解析並呈現結果
            results = json.loads(response.text)
            
            st.write("### 🎯 AI 連網搜尋結果：")
            
            for item in results:
                with st.container():
                    st.markdown(f"### 🏆 {item['name']} ({item['platform']})")
                    st.write(f"📊 **粉絲數量：** {item['fans']}")
                    st.write(f"📝 **風格內容：** {item['content']}")
                    st.markdown(f"[🔗 點我前往該網紅主頁]({item['url']})")
                    st.write("---")
                    
        except Exception as e:
            st.error(f"搜尋過程中發生錯誤，請稍後再試。錯誤訊息：{e}")
            
