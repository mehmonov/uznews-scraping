from scraper import UzNewsScraper
from webpage.excel_writer import ExcelWriter

def main():
    try:
        days_ago = int(input("Necha kun oldingi yangiliklar kerak? (0 - bugun, 1 - kecha, ...): "))
        
        scraper = UzNewsScraper()
        articles = scraper.get_articles_by_day(days_ago)
        
        if not articles:
            print("Berilgan sana uchun yangiliklar topilmadi!")
            return
            
        filename = f"uznews_articles_{days_ago}_days_ago.xlsx"
        excel_writer = ExcelWriter(filename)
        excel_writer.write_articles(articles)
        excel_writer.save()
        
        print(f"Jami {len(articles)} ta yangilik '{filename}' fayliga saqlandi!")
        
    except ValueError:
        print("Xatolik: Iltimos, to'g'ri raqam kiriting!")
    except Exception as e:
        print(f"Xatolik yuz berdi: {str(e)}")

if __name__ == "__main__":
    main()