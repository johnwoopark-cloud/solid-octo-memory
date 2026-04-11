import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_ratings(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        # [중요] 닐슨코리아는 EUC-KR 인코딩을 사용하므로 강제 지정
        res.encoding = 'euc-kr' 
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 'rtg_table' 클래스를 가진 모든 테이블 검색
        tables = soup.find_all('table', {'class': 'rtg_table'})
        
        if not tables:
            print(f"표를 찾지 못함: {url}")
            return []

        # 보통 첫 번째 혹은 두 번째 테이블에 실제 데이터가 있습니다.
        data = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                # 공백 및 탭 제거
                clean_cols = [c.get_text(strip=True) for c in cols]
                
                # 첫 번째 칸이 '숫자'인 경우만 데이터로 수집
                if len(clean_cols) >= 4 and clean_cols[0].isdigit():
                    data.append({
                        'rank': clean_cols[0],
                        'channel': clean_cols[1],
                        'program': clean_cols[2],
                        'rate': clean_cols[3]
                    })
            
            # 데이터를 하나라도 찾았다면 해당 테이블에서 중단
            if data:
                break
        
        return data[:20]

    except Exception as e:
        print(f"에러: {e}")
        return []

# URL 설정
urls = {
    'terrestrial': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01',
    'comprehensive': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_1&area=01',
    'cable': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_1&area=01'
}

# 한국 시간 설정
KST = timezone(timedelta(hours=9))
current_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M')

result = {'date': current_time, 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, url in urls.items():
    print(f"{key} 수집 시작...")
    result[key] = get_ratings(url)
    print(f"{key} 수집 완료: {len(result[key])}개")

# 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
