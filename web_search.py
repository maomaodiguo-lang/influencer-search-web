import streamlit as pd
import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer

# 頁面標題設定
st.set_page_config(page_title="網紅 AI 搜尋器", layout="centered")
st.title("🔍 全平台網紅 AI 語意搜尋器")
st.write("輸入你想尋找的網紅類型或影片風格，AI 將自動為您匹配！")

# 1. 初始化 AI 模型與資料庫（加上快取，避免重複載入變慢）
@st.cache_resource
def init_tools():
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    chroma_client = chromadb.PersistentClient(path="./my_influencer_db")
    collection = chroma_client.get_or_create_collection(name="influencers")
    return model, collection

model, collection = init_tools()

# 2. 模擬假資料導入（第一次開啟網頁時會自動寫入）
def seed_data():
    raw_data = [
        {"id": "yt_1", "name": "老高與小茉", "platform": "YouTube", "fans": "600萬", "content": "世界未解之謎、外星人、科幻、歷史故事說書。", "url": "https://www.youtube.com/"},
        {"id": "ig_1", "name": "莫莉 Molly", "platform": "Instagram", "fans": "80萬", "content": "時裝週直擊、美妝保養、時尚穿搭、歐美風街拍。", "url": "https://www.instagram.com/"},
        {"id": "yt_2", "name": "Joeman", "platform": "YouTube", "fans": "250萬", "content": "奢華便宜對決、豪宅看房開箱、高端3C產品評測。", "url": "https://www.youtube.com/"}
    ]
    for item in raw_data:
        text_to_embed = f"名字:{item['name']} 平台:{item['platform']} 內容:{item['content']}"
        embedding = model.encode(text_to_embed).tolist()
        collection.upsert(
            ids=[item['id']],
            embeddings=[embedding],
            metadatas={"name": item['name'], "platform": item['platform'], "fans": item['fans'], "content": item['content'], "url": item['url']},
            documents=[text_to_embed]
        )

# 執行寫入資料
seed_data()

# 3. 網頁前端介面設計
user_query = st.text_input("💡 請輸入你想找的網紅類型（例如：想找看房子的、時尚穿搭...）", "")

if user_query:
    # AI 向量搜尋
    query_embedding = model.encode(user_query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    
    st.write("### 🎯 為您精選的網紅結果：")
    
    # 顯示結果
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        
        # 用網頁卡片樣式呈現
        with st.container():
            st.markdown(f"### 🏆 {meta['name']} ({meta['platform']})")
            st.write(f"📊 **粉絲數量：** {meta['fans']}")
            st.write(f"📝 **風格內容：** {meta['content']}")
            # 提供直接點擊前往該網紅平台的超連結
            st.markdown(f"[🔗 點我前往該網紅主頁]({meta['url']})")
            st.write("---")