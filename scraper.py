import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_naver_ratings():
    # 네이버 지상파 시청률 검색 결과 (닐슨 코리아 제공 데이터)
    url = "https://search.naver.com/search.naver?query=지상파+시청률"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 네이버 시청률 테이블의 행(tr)들을 찾습니다.
        rows = soup.select('table._rating_list tbody tr')
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # 순위는 보통 th나 첫 td에 있습니다.
                rank = row.find('th', {'scope': 'row'}).get_text(strip=True)
                program = cols[0].get_text(strip=True)
                channel = cols[1].get_text(strip=True)
                rate = cols[2].get_text(strip=True).replace('%', '')
                
                data.append({
                    'rank': rank,
                    'channel': channel,
                    'program': program,
                    'rate': rate
                })
        
        if not data:
            print("⚠️ 네이버에서 데이터를 찾지 못했습니다. 구조 확인이 필요합니다.")
        else:
            print(f"✅ 수집 성공: {len(data)}건의 데이터를 가져왔습니다.")
            
        return data[:20]

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

# 실행 및 저장
ratings = get_naver_ratings()

# 한국 시간으로 업데이트 시간 기록
kst = timezone(timedelta(hours=9))
current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')

result = {
    'date': current_time,
    'terrestrial': ratings
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
