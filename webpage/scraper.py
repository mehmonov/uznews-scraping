import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
import re

@dataclass
class NewsArticle:
    title: str
    description: Optional[str]
    image_url: Optional[str]
    article_id: str
    views_count: int
    published_date: str

class UzNewsScraper:
    def __init__(self, base_url: str = "https://uznews.uz"):
        self.base_url = base_url
        self.latest_id = 77696
        self.check_limit = 50
    
    def get_page_content(self, article_id: str) -> str:
        try:
            url = f"{self.base_url}/uz/posts/{article_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return ""
    
    def parse_article(self, html: str, article_id: str) -> Optional[NewsArticle]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            title = soup.find('h1', {'class': 'font-bold', 'itemprop': 'name'})
            if not title:
                return None
            
            description = soup.find('p', {'class': 'font-normal', 'itemprop': 'description'})
            
            # Rasm URL'ini topish
            image_url = None
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'api.uznews.uz/storage/uploads' in src:
                    image_url = src
                    break
            
            # Ko'rishlar soni - yangilangan qism
            views_count = 0
            views_element = soup.find('span', class_='inline-flex items-center text-black opacity-70 font-medium text_13 gap-2')
            if views_element:
                # SVG dan keyingi span elementini topish
                spans = views_element.find_all('span')
                if len(spans) >= 2:  # Birinchi span ko'rishlar soni, ikkinchisi "views" text
                    try:
                        views_count = int(spans[0].text.strip())
                    except ValueError:
                        views_count = 0
            
            # Sana
            time_element = soup.find('time', {'itemprop': 'datePublished'})
            published_date = time_element.text.strip() if time_element else ''
            
            article = NewsArticle(
                title=title.text.strip(),
                description=description.text.strip() if description else None,
                image_url=image_url,
                article_id=article_id,
                views_count=views_count,
                published_date=published_date
            )
        
            return article
            
        except Exception as e:
            print(f"Xatolik: {article_id} uchun parsing xatoligi: {str(e)}")
            return None

    def is_target_date(self, date_str: str, days_ago: int) -> bool:
        """Yangilik sanasi berilgan kunga to'g'ri kelishini tekshirish"""
        today = datetime.now().date()
        
        if "Бугун" in date_str:
            return days_ago == 0
            
        if "Кеча" in date_str:
            return days_ago == 1
            
        # "8 ноябр, 16:51" formatidagi sana uchun
        try:
            # Faqat kunni ajratib olish
            day_match = re.search(r'(\d+)', date_str)
            if day_match:
                news_day = int(day_match.group(1))
                target_date = (today - timedelta(days=days_ago)).day
                return news_day == target_date
        except Exception:
            pass
            
        return False

    def get_articles_by_day(self, days_ago: int) -> List[NewsArticle]:
        """Berilgan kundagi yangiliklarni olish"""
        articles = []
        filtered_articles = []
        
        # Avval barcha yangiliklarni olish
        for article_id in range(self.latest_id, self.latest_id - self.check_limit, -1):
            html_content = self.get_page_content(str(article_id))
            if not html_content:
                continue
                
            article = self.parse_article(html_content, str(article_id))
            if article:
                articles.append(article)
        
        # So'ng sanaga qarab filterlash
        for article in articles:
            if self.is_target_date(article.published_date, days_ago):
                filtered_articles.append(article)
        
        return filtered_articles
