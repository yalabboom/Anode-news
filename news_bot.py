import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# ✅ 텔레그램 설정
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ✅ 검색할 키워드 목록
KEYWORDS = [
    "음극재",
    "포스코퓨처엠 음극재",
    "대주전자재료",
    "음극재 배터리",
    "anode material battery korea",
]

# ✅ Google 뉴스 RSS 크롤링
def fetch_google_news(keyword, max_results=3):
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(res.content)
        articles = []
        items = root.findall(".//item")[:max_results]
        for item in items:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            source = item.findtext("source", "언론사 미상")
            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "press": source,
                })
        return articles
    except Exception as e:
        print(f"[오류] {keyword} 크롤링 실패: {e}")
        return []

# ✅ 텔레그램 전송
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    res = requests.post(url, json=payload)
    if res.status_code != 200:
        print(f"[오류] 텔레그램 전송 실패: {res.text}")
    else:
        print("✅ 텔레그램 전송 완료!")

# ✅ 메인
def main():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    header = f"🔋 음극재 업계 뉴스 브리핑\n📅 {today}\n{'─'*30}\n\n"
    full_message = header

    seen_titles = set()

    for keyword in KEYWORDS:
        articles = fetch_google_news(keyword, max_results=3)
        new_articles = [a for a in articles if a["title"] not in seen_titles]

        if new_articles:
            full_message += f"🔍 [{keyword}]\n"
            for a in new_articles:
                seen_titles.add(a["title"])
                full_message += f"• {a['title']}\n"
                full_message += f"  {a['press']}\n"
                full_message += f"  {a['url']}\n\n"

    if len(full_message) <= len(header):
        full_message += "오늘은 새로운 뉴스가 없습니다."

    if len(full_message) > 4000:
        full_message = full_message[:4000] + "\n\n... (더 보기: 구글 뉴스)"

    send_telegram(full_message)

if __name__ == "__main__":
    main()
