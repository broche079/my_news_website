import requests
from bs4 import BeautifulSoup

def get_google_trends():
    url = "https://trends.google.com/trending/rss?geo=TW"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        items = soup.find_all('item')
        
        trends = []
        for index, item in enumerate(items, 1):
            title = item.find('title').text
            if len(title) < 2:
                continue
                
            traffic = item.find('ht:approx_traffic')
            traffic_text = traffic.text if traffic else "熱門搜尋"
            
            news_items = item.find_all('ht:news_item')
            news_list = []
            for news in news_items:
                news_title = news.find('ht:news_item_title').text
                news_url = news.find('ht:news_item_url').text
                news_list.append({"title": news_title, "url": news_url})
                
            trends.append({
                "rank": len(trends) + 1,
                "keyword": title,
                "traffic": traffic_text,
                "news": news_list
            })
        return trends
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []

print("正在同步全台最新熱搜數據...")
trends_data = get_google_trends()

# 開始組裝 HTML 內容
html_cards = ""
for item in trends_data:
    main_news = item['news'][0]['title'] if item['news'] else "目前全台搜尋量激增，大家正高度關注最新動態。"
    news_link_html = f'<a href="{item["news"][0]["url"]}" target="_blank">🔗 {main_news}</a>' if item['news'] else ""
    
    card_html = f"""
            <div class="trend-card">
                <div class="card-header">
                    <span class="rank">#{item['rank']}</span>
                    <span class="traffic">🔥 {item['traffic']}</span>
                </div>
                <h2>{item['keyword']}</h2>
                <p class="ai-summary">💡 <strong>AI 摘要：</strong> 網友正高度關注「{item['keyword']}」。核心話題：【{main_news}】。</p>
                <div class="news-links">
                    {news_link_html}
                </div>
            </div>
    """
    html_cards += card_html

# 讀取原本的 index.html 結構，或者我們直接生成全新的 index.html
full_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的每日熱搜儀表板</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <header class="header">
        <h1>🔥 每日全台熱搜焦點</h1>
        <p>告別垃圾新聞，掌握全台大眾今日最新關注話題</p>
    </header>

    <main class="container">
        <div class="trends-grid" id="trendsContainer">
            {html_cards}
        </div>
    </main>

    <footer class="footer">
        <p>© 2026 Designed for 許肇睿 | Personal Information Dashboard</p>
    </footer>

</body>
</html>
"""

# 寫入 index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("✨ 網頁更新成功！請重新整理 index.html 查看最新熱搜！")
