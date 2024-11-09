import requests
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
import json
import re

@dataclass
class NewsArticle:
    title: str
    description: Optional[str]
    views_count: int
    published_date: str
    article_id: str

class UzNewsScraper:
    def __init__(self):
        self.base_url = "https://api.uznews.uz/api/v1"
        self.latest_id = 77697
        self.check_limit = 50
    
    def get_article_from_api(self, article_id: str) -> Optional[NewsArticle]:
        try:
            url = f"{self.base_url}/posts/{article_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('success'):
                return None
            
            post = data['result']['post']
            
            # JSON dan description ni olish va tozalash
            description_json = json.loads(post.get('description', '{}'))
            description_text = ''
            if 'blocks' in description_json:
                # Barcha bloklardan matnni yig'ish
                description_text = ' '.join(
                    block['data'].get('text', '').replace('\\', '')
                    for block in description_json['blocks']
                    if block['type'] == 'paragraph'
                )
            
            return NewsArticle(
                title=post['title'],
                description=description_text,
                views_count=post.get('views_count', 0),
                published_date=post.get('created_at', ''),
                article_id=str(post['id'])
            )
            
        except Exception as e:
            print(f"Xatolik: {article_id} uchun API so'rovi xatoligi: {str(e)}")
            return None

    def is_target_date(self, date_str: str, days_ago: int) -> bool:
        """Yangilik sanasi berilgan kunga to'g'ri kelishini tekshirish"""
        try:
            # "Сегодня, 07:36" formati uchun
            if "Сегодня" in date_str or "Бугун" in date_str:
                return days_ago == 0
                
            # "Вчера, 16:51" formati uchun
            if "Вчера" in date_str or "Кеча" in date_str:
                return days_ago == 1
                
            # "12 март, 16:51" formatidagi sana uchun
            try:
                today = datetime.now().date()
                # Kunni ajratib olish
                day_match = re.search(r'(\d+)', date_str)
                if day_match:
                    news_day = int(day_match.group(1))
                    target_date = (today - timedelta(days=days_ago)).day
                    return news_day == target_date
            except:
                pass
                
            return False
                
        except Exception as e:
            print(f"Sana tekshirishda xatolik: {str(e)}")
            return False

    def get_articles_by_day(self, days_ago: int) -> List[NewsArticle]:
        """Berilgan kundagi yangiliklarni olish"""
        articles = []
        filtered_articles = []
        
        # Avval barcha yangiliklarni olish
        for article_id in range(self.latest_id, self.latest_id - self.check_limit, -1):
            article = self.get_article_from_api(str(article_id))
            if article:
                articles.append(article)
        
        # So'ng sanaga qarab filterlash
        for article in articles:
            if self.is_target_date(article.published_date, days_ago):
                filtered_articles.append(article)
                print(f"Saralandi: {article.title} - Ko'rishlar: {article.views_count}")
        
        return filtered_articles