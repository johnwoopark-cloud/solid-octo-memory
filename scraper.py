import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_ratings(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.nielsenkorea.co.kr/'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8' # 닐슨은 대개 utf-8 또는 euc-kr입니다.
        
        if res.status_code != 200:
            print(f"접속 실패: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # [핵심 변경] 모든 table을 다 뒤져서 '순위'라는 글자가 있는 표를 찾습니다.
        target_table = None
        tables = soup.find_all('table')
        for t in tables:
            if '순위' in t.text and '프로그램명' in t.text:
                target_table = t
                break
        
        if not target_table:
            print(f"표를 찾을 수 없습니다: {url}")
            return []

        rows = target_table.find_all('tr')
        data = []
        
        for row in rows:
            cols = row.find_all('td')
            # 불필요한 공백 제거 및 텍스트 추출
            clean_cols = [c.text.strip().replace('\t', '').replace('\n', '') for c in cols]
            
            # 첫 번째 칸이 숫자인 경우에만 데이터로 간주 (순위 데이터)
            if len(clean_cols) >= 4 and clean_cols[0].isdigit():
                data.append({
                    'rank': clean_cols[0],
                    'channel': clean_cols[1],
                    'program': clean_cols[2],
                    'rate': clean_cols[3]
                })
        
        print(f"추출 성공: {len(data)}건")
        return data[:20]

    except Exception as e:
        print(f"에러 발생: {e}")
        return []

# 데이터 수집 실행
urls = {
    'terrestrial': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01',
    'comprehensive': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_1&area=01',
    'cable': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_1&area=01'
}

# 한국 시간(KST)으로 업데이트 시간 기록
from datetime import timedelta, timezone
KST = timezone(timedelta(hours=9))
current_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M')

result = {'date': current_time, 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, url in urls.items():
    print(f"시작: {key} 데이터 가져오는 중...")
    result[key] = get_ratings(url)

# 결과 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
