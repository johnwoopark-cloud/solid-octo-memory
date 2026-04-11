import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone

def get_ratings():
    # 1. 닐슨 모바일 페이지가 차단이 가장 적고 구조가 단순합니다.
    url = "https://m.nielsenkorea.co.kr/main/main_1.asp"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://m.nielsenkorea.co.kr/'
    }
    
    try:
        print(f"--- 데이터 수집 시작 ({datetime.now().strftime('%H:%M:%S')}) ---")
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8' # 모바일은 utf-8인 경우가 많습니다.
        
        print(f"상태 코드: {res.status_code}, 응답 길이: {len(res.text)}")
        
        if res.status_code != 200:
            print("❌ 웹사이트 접속에 실패했습니다.")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 모바일 페이지의 순위 리스트(태그 구조에 맞춰 최적화)
        # 닐슨 모바일은 보통 .tb_type_1 혹은 table 태그를 사용합니다.
        data = []
        table = soup.find('table') # 가장 첫 번째 테이블 탐색
        
        if not table:
            print("⚠️ 테이블을 찾을 수 없습니다. 사이트 구조를 다시 확인해야 합니다.")
            return []

        rows = table.find_all('tr')
        print(f"발견된 행(row) 개수: {len(rows)}")

        for row in rows:
            cols = row.find_all(['td', 'th'])
            txt = [c.get_text(strip=True) for c in cols]
            
            # 첫 번째 칸이 숫자인 행만 수집 (순위 데이터)
            if len(txt) >= 3 and txt[0].isdigit():
                data.append({
                    'rank': txt[0],
                    'channel': txt[1] if len(txt) > 2 else "",
                    'program': txt[2] if len(txt) > 2 else txt[1],
                    'rate': txt[-1].replace('%', '')
                })
        
        if not data:
            print("⚠️ 데이터 매칭에 실패했습니다. (숫자로 시작하는 행이 없음)")
            # 로그 확인용: 첫 5행의 내용을 출력해봅니다.
            for i, r in enumerate(rows[:5]):
                print(f"행 {i} 내용: {r.get_text(strip=True)}")

        print(f"✅ 수집 성공: {len(data)}건")
        return data[:20]

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

# 실행 및 저장
ratings = get_ratings()
kst = timezone(timedelta(hours=9))
result = {
    'date': datetime.now(kst).strftime('%Y-%m-%d %H:%M'),
    'terrestrial': ratings
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
