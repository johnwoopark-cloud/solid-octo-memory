import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_ratings(base_url, category_name):
    # 한국 시간(KST) 기준으로 '어제' 날짜 계산
    KST = timezone(timedelta(hours=9))
    yesterday = (datetime.now(KST) - timedelta(days=1)).strftime('%Y%m%d')
    
    # URL에 어제 날짜 파라미터(?report_date_YMD=YYYYMMDD) 강제 삽입
    url = f"{base_url}&report_date_YMD={yesterday}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"[{category_name}] {yesterday} 자 데이터 수집 중...")
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'euc-kr' 
        
        if "데이터가 없습니다" in res.text:
            print(f"[{category_name}] 해당 날짜에 데이터가 아직 업로드되지 않았습니다.")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 닐슨의 순위 테이블(rtg_table 클래스) 찾기
        table = soup.find('table', {'class': 'rtg_table'})
        if not table:
            # 클래스로 못 찾을 경우 모든 테이블 중 '순위' 텍스트가 있는 것을 탐색
            for t in soup.find_all('table'):
                if '순위' in t.get_text():
                    table = t
                    break

        if not table:
            return []

        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            txt_cols = [c.get_text(strip=True) for c in cols]
            
            # 첫 번째 칸이 숫자인 행만 데이터로 수집
            if len(txt_cols) >= 4 and txt_cols[0].isdigit():
                data.append({
                    'rank': txt_cols[0],
                    'channel': txt_cols[1],
                    'program': txt_cols[2],
                    'rate': txt_cols[3]
                })
        
        print(f"[{category_name}] {len(data)}건 추출 완료")
        return data[:20]

    except Exception as e:
        print(f"[{category_name}] 에러 발생: {e}")
        return []

# 각 카테고리별 기본 URL
urls = {
    'terrestrial': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01',
    'comprehensive': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_1&area=01',
    'cable': 'https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_1&area=01'
}

KST = timezone(timedelta(hours=9))
current_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
result = {'date': current_time, 'terrestrial': [], 'comprehensive': [], 'cable': []}

for key, val in urls.items():
    result[key] = get_ratings(val, key)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
