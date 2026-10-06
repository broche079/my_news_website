import requests
from bs4 import BeautifulSoup

# 1. 抓取原本的 Google 全台綜合熱搜
def get_google_trends():
    url = "https://trends.google.com/trending/rss?geo=TW"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        items = soup.find_all('item')
        
        trends = []
        # 這裡改為取前 20 筆
        for index, item in enumerate(items[:20], 1): 
            title = item.find('title').text
            traffic = item.find('ht:approx_traffic')
            traffic_text = traffic.text if traffic else ""
            
            news_items = item.find_all('ht:news_item')
            news_list = []
            if news_items:
                news_list.append({
                    "title": news_items[0].find('ht:news_item_title').text,
                    "url": news_items[0].find('ht:news_item_url').text
                })
                
            trends.append({
                "rank": index,
                "keyword": title,
                "traffic": traffic_text,
                "news": news_list
            })
        return trends
    except Exception as e:
        return []

# 2. 抓取 Google 新聞各大分類 RSS (政治/財經/娛樂)
def get_google_news(topic_code):
    # NATION (政治/國內), BUSINESS (股票/財經), ENTERTAINMENT (潮流/時尚/娛樂)
    url = f"https://news.google.com/rss/headlines/section/topic/{topic_code}?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        news_list = []
        # 這裡也改為取前 20 筆最新熱門話題
        for index, item in enumerate(items[:20], 1): 
            title = item.find('title').text
            link = item.find('link').text
            
            # Google News 標題通常會有 " - 媒體名稱"，我們把它切開讓版面更乾淨
            if " - " in title:
                clean_title = title.rsplit(" - ", 1)[0]
                source = title.rsplit(" - ", 1)[1]
            else:
                clean_title = title
                source = "新聞"
                
            news_list.append({
                "rank": index,
                "title": clean_title,
                "url": link,
                "source": source
            })
        return news_list
    except Exception as e:
        return []

print("正在抓取跨領域分類數據 (每組 20 筆)...")
trends_data = get_google_trends()
politics_news = get_google_news("NATION")
finance_news = get_google_news("BUSINESS")
fashion_news = get_google_news("ENTERTAINMENT")

# 3. 準備生成 HTML 卡片區塊
def generate_trend_cards(data):
    html = ""
    for item in data:
        main_news = item['news'][0]['title'] if item['news'] else "大眾正高度關注此話題最新動態。"
        news_url = item['news'][0]['url'] if item['news'] else "#"
        html += f"""
        <div class="trend-card">
            <div class="card-header">
                <span class="rank">#{item['rank']}</span>
                <span class="traffic">🔥 {item['traffic']}</span>
            </div>
            <h2>{item['keyword']}</h2>
            <p class="ai-summary">💡 <strong>熱點追蹤：</strong> {main_news}</p>
            <div class="news-links"><a href="{news_url}" target="_blank">🔗 閱讀相關報導</a></div>
        </div>
        """
    return html

def generate_news_cards(data, icon):
    html = ""
    for item in data:
        html += f"""
        <div class="trend-card">
            <div class="card-header">
                <span class="rank">#{item['rank']}</span>
                <span class="traffic">{icon} {item['source']}</span>
            </div>
            <h2 style="font-size: 1.25rem; margin-bottom: 15px; color: #222;">{item['title']}</h2>
            <div class="news-links"><a href="{item['url']}" target="_blank">🔗 閱讀完整內容</a></div>
        </div>
        """
    return html

# 4. 組裝最終 HTML (加入分頁 Tab 與 JavaScript)
full_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的全方位資訊儀表板</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <header class="header">
        <h1>🔥 全方位資訊儀表板</h1>
        <p>政治、潮流、時尚、股票，全台最新話題一次精準掌握</p>
    </header>

    <main class="container">
        
        <!-- 導覽標籤 (Tabs) -->
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('tab-trends')">🔥 綜合熱搜</button>
            <button class="tab-btn" onclick="showTab('tab-politics')">🏛️ 政治與新聞</button>
            <button class="tab-btn" onclick="showTab('tab-finance')">📈 股票與財經</button>
            <button class="tab-btn" onclick="showTab('tab-fashion')">✨ 潮流與時尚</button>
        </div>

        <!-- 各分類內容區塊 -->
        <div id="tab-trends" class="tab-content active">
            <div class="trends-grid">{generate_trend_cards(trends_data)}</div>
        </div>
        
        <div id="tab-politics" class="tab-content">
            <div class="trends-grid">{generate_news_cards(politics_news, "📰")}</div>
        </div>
        
        <div id="tab-finance" class="tab-content">
            <div class="trends-grid">{generate_news_cards(finance_news, "💰")}</div>
        </div>
        
        <div id="tab-fashion" class="tab-content">
            <div class="trends-grid">{generate_news_cards(fashion_news, "👗")}</div>
        </div>

    </main>

    <footer class="footer">
        <p>© 2026 Designed for 許肇睿 | Personal Information Dashboard</p>
    </footer>

    <!-- 負責切換標籤的輕量級 JavaScript -->
    <script>
        function showTab(tabId) {{
            // 隱藏所有內容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            // 取消所有按鈕的選中狀態
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // 顯示被點擊的內容區塊
            document.getElementById(tabId).classList.add('active');
            // 讓被點擊的按鈕變暗色 (Active 狀態)
            event.currentTarget.classList.add('active');
        }}
    </script>

</body>
</html>
"""

# 寫入 index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("✨ 網頁更新成功！已生成多重分類與擴充至每區 20 筆選項！")