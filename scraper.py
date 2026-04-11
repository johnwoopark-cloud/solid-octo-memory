import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_daum_ratings():
    # 다음 검색의 지상파 시청률 페이지 (해외 서버에서도 접속이 원활합니다)
    url = "https://search.daum.net/search?w=tot&q=%EC%A7%80%EC%83%81%ED%8C%8C%EC%8B%9C%EC%B2%AD%EB%A5%A0"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("--- 다음(Daum) 시청률 데이터 수집 시작 ---")
        res = requests.get(url, headers=headers, timeout=20)
        
        if res.status_code != 200:
            print(f"❌ 접속 실패: 상태 코드 {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 다음 시청률 테이블의 특성상 클래스명이 복잡할 수 있어 테이블 내 텍스트로 탐색
        rows = []
        tables = soup.find_all('table')
        for t in tables:
            if '순위' in t.text and '프로그램' in t.text:
                rows = t.find_all('tr')
                break
        
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            # 텍스트만 깨끗하게 추출
            txt = [c.get_text(strip=True) for c in cols]
            
            # 첫 번째 칸이 숫자인 행(순위 데이터)만 골라내기
            if len(txt) >= 4 and txt[0].isdigit():
                data.append({
                    'rank': txt[0],
                    'program': txt[1],
                    'channel': txt[2],
                    'rate': txt[3].replace('%', '')
                })
        
        if not data:
            print("⚠️ 데이터를 찾지 못했습니다. 구조가 변경되었을 수 있습니다.")
        else:
            print(f"✅ 수집 성공: {len(data)}건 추출 완료")
            
        return data[:20]

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

# 실행 및 저장
ratings = get_daum_ratings()

# 한국 시간으로 업데이트 시간 기록
kst = timezone(timedelta(hours=9))
current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')

result = {
    'date': current_time,
    'terrestrial': ratings
}

# 최종 데이터 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
