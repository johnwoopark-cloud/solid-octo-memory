import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_ratings(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    table = soup.find('table', {'class': 'rtg_table'})
    rows = table.find_all('tr')[2:]  # 헤더 제외
    
    data = []
    for row in rows[:20]: # TOP 20만 추출
        cols = row.find_all('td')
        if len(cols) < 4: continue
        data.append({
            'rank': cols[0].text.strip(),
            'channel': cols[1].text.strip(),
            'program': cols[2].text.strip(),
            'rate': cols[3].text.strip() # 시청률만 가져옴
        })
    return data

# 닐슨 코리아 메뉴별 URL (01:지상파, 02:종편, 03:케이블)
urls = {
    'terrestrial': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01',
    'comprehensive': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_1&area=01',
    'cable': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_1&area=01'
}

result = {'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, url in urls.items():
    try:
        result[key] = get_ratings(url)
    except Exception as e:
        print(f"Error fetching {key}: {e}")

# data.json 파일로 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
