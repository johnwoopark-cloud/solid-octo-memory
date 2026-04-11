import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_terrestrial_ratings():
    # 한국 시간 기준 '어제' 날짜 구하기
    kst = timezone(timedelta(hours=9))
    yesterday = (datetime.now(kst) - timedelta(days=1)).strftime('%Y%m%d')
    
    # 지상파 일일 순위 URL (어제 날짜 파라미터 포함)
    url = f"https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_1&area=01&report_date_YMD={yesterday}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.nielsenkorea.co.kr/',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        print(f"--- {yesterday} 자 지상파 데이터 수집 시작 ---")
        res = requests.get(url, headers=headers, timeout=30)
        res.encoding = 'euc-kr' # 닐슨 전용 인코딩
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 클래스명으로 찾기 시도
        table = soup.find('table', {'class': 'rtg_table'})
        
        # 2. 실패 시 '순위' 글자가 들어있는 테이블 찾기
        if not table:
            for t in soup.find_all('table'):
                if '순위' in t.get_text() and '프로그램명' in t.get_text():
                    table = t
                    break
        
        if not table:
            print("⚠️ 데이터를 찾지 못했습니다. 사이트에서 차단했거나 구조가 바뀌었을 수 있습니다.")
            print("로그 확인용 HTML 일부:", res.text[:300]) # 진단용 로그
            return []

        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            txt = [c.get_text(strip=True) for c in cols]
            
            # 첫 번째 칸이 숫자인 경우(순위 데이터)만 수집
            if len(txt) >= 4 and txt[0].isdigit():
                data.append({
                    'rank': txt[0],
                    'channel': txt[1],
                    'program': txt[2],
                    'rate': txt[3]
                })
        
        print(f"✅ 수집 성공: {len(data)}건")
        return data[:20]

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

# 실행 및 저장
ratings = get_terrestrial_ratings()
result = {
    'date': datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M'),
    'terrestrial': ratings
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
