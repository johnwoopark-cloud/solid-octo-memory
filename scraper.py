import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_ratings(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    res = requests.get(url, headers=headers)
    # 닐슨코리아는 EUC-KR을 사용하는 경우가 많으므로 자동 인코딩 설정
    res.encoding = res.apparent_encoding 
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 테이블을 찾는 더 정확한 방법
    table = soup.find('table', {'class': 'rtg_table'})
    if not table:
        return []

    rows = table.find_all('tr')
    
    data = []
    for row in rows:
        cols = row.find_all('td')
        # 데이터가 있는 행만 골라냄 (순위가 숫자인 것만)
        if len(cols) >= 4 and cols[0].text.strip().isdigit():
            data.append({
                'rank': cols[0].text.strip(),
                'channel': cols[1].text.strip(),
                'program': cols[2].text.strip(),
                'rate': cols[3].text.strip()
            })
    return data[:20] # 상위 20개만

urls = {
    'terrestrial': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01',
    'comprehensive': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_1&area=01',
    'cable': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_1&area=01'
}

# 현재 한국 시간 (UTC+9) 반영
current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
result = {'date': current_time, 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, url in urls.items():
    try:
        ratings = get_ratings(url)
        if ratings:
            result[key] = ratings
        print(f"Successfully fetched {key}: {len(ratings)} items")
    except Exception as e:
        print(f"Error fetching {key}: {e}")

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
