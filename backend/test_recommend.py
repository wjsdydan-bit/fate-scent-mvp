import requests
import json
import time

url = "http://localhost:8000/api/recommend"
headers = {"Content-Type": "application/json"}
data = {
    "user_name": "테스터",
    "gender": "여성",
    "saju_data": {
        "saju_name": "갑자 을축 병인 (시간 모름·6글자 기준)",
        "counts": {"Wood": 2, "Fire": 1, "Earth": 1, "Metal": 0, "Water": 2},
        "strongest": "Wood",
        "weakest": "Metal",
        "gapja_str": "갑자 을축 병인",
        "pillars": {
            "year": {"stem": "갑", "branch": "자", "stem_element": "Wood", "branch_element": "Water"},
            "month": {"stem": "을", "branch": "축", "stem_element": "Wood", "branch_element": "Earth"},
            "day": {"stem": "병", "branch": "인", "stem_element": "Fire", "branch_element": "Wood"},
            "hour": {"stem": "?", "branch": "?", "stem_element": "Unknown", "branch_element": "Unknown"}
        }
    },
    "pref_tags": ["꽃향기(플로럴)"],
    "dislike_tags": ["스모키/가죽"],
    "gender_filter": "전체",
    "brand_filter_mode": "전체 뷰티 브랜드 포함",
    "interests": ["연애운 💕"]
}

print("Sending request...")
try:
    start_time = time.time()
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Elapsed: {time.time() - start_time:.2f}s")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! JSON response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:500] + "...")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception exactly: {e}")
