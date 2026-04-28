import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# ✅ 텔레그램 설정 (GitHub Secrets에서 자동으로 가져옴)
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ✅ 검색할 키워드 목록
KEYWORDS = [
    "음극재",
    "포스코퓨처엠",
    "대주전자재료",
    "BTR",
    "음극재 배터리",
]

# ✅ 네이버 뉴스 검색 함수
def fetch_naver_news(keyword, max_results=3):
    url = f"https://search.naver.com/search.naver?where=news&query={requests.utils.quote(keyword)}&sort=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = []
        items = soup.select("div.news_wrap")[:max_results]
        for item in items:
            title_tag = item.select_one("a.news_tit")
            press_tag = item.select_one("a.info.press")
            desc_tag = item.select_one("div.dsc_wrap")
            if title_tag:
                articles.append({
                    "title": title_tag.get_text(strip=True),
                    "url": title_tag["href"],
                    "press": press_tag.get_text(strip=True) if press_tag else "언론사 미상",
                    "desc": desc_tag.get_text(strip=True)[:80] + "..." if desc_tag else "",
                })
        return articles
    except Exception as e:
        print(f"[오류] {keyword} 크롤링 실패: {e}")
        return []

# ✅ 텔레그램 메시지 전송 함수
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

# ✅ 메인 실행
def main():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    header = f"🔋 <b>음극재 업계 뉴스 브리핑</b>\n📅 {today}\n{'─'*30}\n\n"
    full_message = header

    seen_titles = set()  # 중복 제거용

    for keyword in KEYWORDS:
        articles = fetch_naver_news(keyword, max_results=3)
        new_articles = [a for a in articles if a["title"] not in seen_titles]

        if new_articles:
            full_message += f"🔍 <b>[{keyword}]</b>\n"
            for a in new_articles:
                seen_titles.add(a["title"])
                full_message += f"• <a href='{a['url']}'>{a['title']}</a>\n"
                full_message += f"  <i>{a['press']}</i> — {a['desc']}\n\n"

    if len(full_message) <= len(header):
        full_message += "오늘은 새로운 뉴스가 없습니다."

    # 텔레그램 메시지 길이 제한(4096자) 처리
    if len(full_message) > 4000:
        full_message = full_message[:4000] + "\n\n... (더 보기: 네이버 뉴스)"

    send_telegram(full_message)
    print("✅ 텔레그램 전송 완료!")

if __name__ == "__main__":
    main()
