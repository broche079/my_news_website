import requests
from bs4 import BeautifulSoup

# ==========================================
# 1. 資料抓取模組 (Data Fetching)
# ==========================================

def get_google_trends(limit=20):
    """抓取 Google 台灣綜合熱搜"""
    url = "https://trends.google.com/trending/rss?geo=TW"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml") 
        items = soup.find_all("item")
        
        trends = []
        for index, item in enumerate(items[:limit], 1): 
            title = item.find("title").text
            
            # 處理搜尋熱度
            traffic = item.find("ht:approx_traffic")
            traffic_text = traffic.text if traffic else ""
            
            # 處理相關新聞
            news_items = item.find_all("ht:news_item")
            news_list = []
            if news_items:
                news_title = news_items[0].find("ht:news_item_title").text
                news_url = news_items[0].find("ht:news_item_url").text
                news_list.append({"title": news_title, "url": news_url})
                
            trends.append({
                "rank": index,
                "keyword": title,
                "traffic": traffic_text,
                "news": news_list
            })
        return trends
    except Exception as e:
        print(f"抓取 Google 熱搜失敗: {e}")
        return []

def get_google_news(topic_code, limit=20):
    """抓取 Google 新聞指定分類 (NATION, BUSINESS, ENTERTAINMENT)"""
    url = f"https://news.google.com/rss/headlines/section/topic/{topic_code}?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        news_list = []
        for index, item in enumerate(items[:limit], 1): 
            title = item.find("title").text
            link = item.find("link").text
            
            # 分離新聞標題與來源
            if " - " in title:
                clean_title, source = title.rsplit(" - ", 1)
            else:
                clean_title, source = title, "新聞"
                
            news_list.append({
                "rank": index,
                "title": clean_title,
                "url": link,
                "source": source
            })
        return news_list
    except Exception as e:
        print(f"抓取新聞分類 {topic_code} 失敗: {e}")
        return []


# ==========================================
# 2. HTML 元素生成模組 (HTML Generation)
# ==========================================

def generate_trend_cards(data):
    """生成綜合熱搜的 HTML 卡片"""
    if not data:
        return "<p style='text-align:center; padding: 20px; color: #888;'>目前暫無資料，請稍後再試。</p>"
        
    html = ""
    for item in data:
        main_news = item["news"][0]["title"] if item["news"] else "大眾正高度關注此話題最新動態。"
        news_url = item["news"][0]["url"] if item["news"] else "#"
        html += f"""
        <div class="trend-card">
            <div class="card-header">
                <span class="rank">#{item["rank"]}</span>
                <span class="traffic">🔥 {item["traffic"]}</span>
            </div>
            <h2>{item["keyword"]}</h2>
            <p class="ai-summary">💡 <strong>熱點追蹤：</strong> {main_news}</p>
            <div class="news-links"><a href="{news_url}" target="_blank">🔗 閱讀相關報導</a></div>
        </div>
        """
    return html

def generate_news_cards(data, icon):
    """生成新聞分類的 HTML 卡片"""
    if not data:
        return "<p style='text-align:center; padding: 20px; color: #888;'>目前暫無資料，請稍後再試。</p>"
        
    html = ""
    for item in data:
        html += f"""
        <div class="trend-card">
            <div class="card-header">
                <span class="rank">#{item["rank"]}</span>
                <span class="traffic">{icon} {item["source"]}</span>
            </div>
            <h2 style="font-size: 1.25rem; margin-bottom: 15px; color: #222;">{item["title"]}</h2>
            <div class="news-links"><a href="{item["url"]}" target="_blank">🔗 閱讀完整內容</a></div>
        </div>
        """
    return html


# ==========================================
# 3. 主程式執行模組 (Main Execution)
# ==========================================

def main():
    print("開始抓取跨領域分類數據 (每組 20 筆)...")
    
    # 1. 抓取資料
    trends_data = get_google_trends(limit=20)
    politics_news = get_google_news("NATION", limit=20)
    finance_news = get_google_news("BUSINESS", limit=20)
    fashion_news = get_google_news("ENTERTAINMENT", limit=20)

    # 2. 生成各區塊 HTML
    trends_html = generate_trend_cards(trends_data)
    politics_html = generate_news_cards(politics_news, "📰")
    finance_html = generate_news_cards(finance_news, "💰")
    fashion_html = generate_news_cards(fashion_news, "👗")

    # 3. 組裝完整網頁
    full_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的全方位資訊儀表板</title>
    <link rel="stylesheet" href="style.css?v=2026">
</head>
<body>

    <header class="header">
        <h1>🔥 全方位資訊儀表板</h1>
        <p>政治、潮流、時尚、股票，全台最新話題一次精準掌握</p>
    </header>

    <main class="container">
        
        <!-- 導覽標籤 (Tabs) -->
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('tab-trends', this)">🔥 綜合熱搜</button>
            <button class="tab-btn" onclick="showTab('tab-politics', this)">🏛️ 政治與新聞</button>
            <button class="tab-btn" onclick="showTab('tab-finance', this)">📈 股票與財經</button>
            <button class="tab-btn" onclick="showTab('tab-fashion', this)">✨ 潮流與時尚</button>
        </div>

        <!-- 各分類內容區塊 -->
        <div id="tab-trends" class="tab-content active">
            <div class="trends-grid">{trends_html}</div>
        </div>
        
        <div id="tab-politics" class="tab-content">
            <div class="trends-grid">{politics_html}</div>
        </div>
        
        <div id="tab-finance" class="tab-content">
            <div class="trends-grid">{finance_html}</div>
        </div>
        
        <div id="tab-fashion" class="tab-content">
            <div class="trends-grid">{fashion_html}</div>
        </div>

    </main>

    <footer class="footer">
        <p>© 2026 Designed for 許肇睿 | Personal Information Dashboard</p>
    </footer>

    <!-- 負責切換標籤的輕量級 JavaScript -->
    <script>
        function showTab(tabId, btnElement) {{
            // 隱藏所有內容
            document.querySelectorAll(".tab-content").forEach(tab => {{
                tab.classList.remove("active");
            }});
            // 取消所有按鈕的選中狀態
            document.querySelectorAll(".tab-btn").forEach(btn => {{
                btn.classList.remove("active");
            }});
            
            // 顯示被點擊的內容區塊
            document.getElementById(tabId).classList.add("active");
            // 讓被點擊的按鈕變暗色
            btnElement.classList.add("active");
        }}
    </script>

</body>
</html>
"""

    # 4. 寫入檔案
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print("✨ 網頁更新成功！已生成手機相容且分類整齊的 HTML！")

if __name__ == "__main__":
    main()
