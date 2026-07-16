import streamlit as st
from google import genai
from google.genai import types
import json

# 1. 網頁基本設定
st.set_page_config(
    page_title="AI 全網網紅雷達", 
    page_icon="🛰️",
    layout="centered"
)

st.title("🛰️ AI 全網自動網紅搜尋器")
st.write("輸入你想尋找的任何領域、類型或網紅名稱，AI 將自動連網搜尋並整理給您！")

# 2. 從 Streamlit 後台 Secrets 安全取得 API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 網站管理員尚未在 Streamlit Secrets 後台設定 API 金鑰。")
    st.info("請至 Streamlit 控制台的 Settings -> Secrets 寫入：GEMINI_API_KEY = \"您的金鑰\"")
    st.stop()

# 3. 提供乾淨的搜尋框給所有使用者
user_query = st.text_input(
    "💡 想要搜尋什麼？", 
    placeholder="例如：台灣3C開箱YouTuber、風格幽默的旅遊部落客、或是特定網紅名稱..."
)

if user_query:
    with st.spinner("🚀 AI 正在全網搜尋最新資訊並分析中，請稍候..."):
        try:
            # 設計精準的提示詞，強迫 AI 回傳標準的 JSON 格式
            prompt = f"""
            請上網搜尋符合以下條件的網紅（KOL / YouTuber / Instagrammer / TikToker）："{user_query}"。
            請找出 3 到 5 位最符合、最真實存在的網紅，並以嚴格的 JSON 格式輸出，不要有任何 Markdown 包裹（如 ```json 等標籤）或額外的文字解釋。
            
            回傳的格式必須完全符合以下結構：
            [
              {{
                "name": "網紅的名字",
                "platform": "主要平台（例如 YouTube, Instagram 等）",
                "fans": "約略的粉絲數或訂閱數（例如 50萬、1.2M）",
                "content": "一小段關於他的特色、影片風格及推薦原因的中文介紹",
                "url": "他的頻道或個人主頁完整網址連結"
              }}
            ]
            """
            
            # 呼叫最新穩定的 Gemini 2.5 Flash 聯網模型
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    # 啟動 Google 搜尋功能（Grounding with Google Search）
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json"
                ),
            )
            
            # 解析 AI 回傳的 JSON 資料
            results = json.loads(response.text)
            
            st.write("### 🎯 AI 聯網搜尋結果：")
            
            # 漂亮地渲染成卡片呈現
            for item in results:
                with st.container():
                    st.markdown(f"### 🏆 {item['name']} ({item['platform']})")
                    st.write(f"📊 **粉絲數量：** {item['fans']}")
                    st.write(f"📝 **風格介紹：** {item['content']}")
                    st.markdown(f"[🔗 點我前往該網紅主頁]({item['url']})")
                    st.write("---")
                    
        except json.JSONDecodeError:
            # 預防 AI 偶爾沒給出標準 JSON 格式的備用容錯機制
            st.warning("⚠️ 搜尋結果格式解析失敗，以下為 AI 原始回傳內容：")
            st.write(response.text)
        except Exception as e:
            st.error(f"搜尋過程中發生錯誤，請稍後再試。錯誤訊息：{e}")
            
