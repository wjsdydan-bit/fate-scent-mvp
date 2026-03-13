import time
import requests

BASE_URL = "http://localhost:8000"

def test_compatibility():
    print("--- [1] Testing /api/compatibility ---")
    payload = {
        "user_name": "김테스트",
        "gender": "여성향",
        "year": 1995,
        "month": 5,
        "day": 10,
        "know_time": False,
        "perf_brand": "Jo Malone",
        "perf_name": "Wood Sage & Sea Salt"
    }
    
    start_time = time.time()
    try:
        res = requests.post(f"{BASE_URL}/api/compatibility", json=payload)
        end_time = time.time()
        
        if res.status_code == 200:
            data = res.json()
            score = data.get("compatibility_score")
            print(f"✅ Success! Score: {score}")
            print(f"⏱️ Time Taken: {end_time - start_time:.2f} seconds")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"🚨 Error: {e}")
        
def test_recommend_direct():
    print("\n--- [2] Testing /api/recommend_direct ---")
    payload = {
        "user_name": "이기적",
        "gender": "남성향",
        "year": 1990,
        "month": 11,
        "day": 20,
        "know_time": False,
        "pref_tags": ["시원한(아쿠아/마린)"],
        "dislike_tags": ["달콤한(앰버/바닐라)"],
        "gender_filter": "남성향",
        "brand_filter_mode": "전체 브랜드",
        "interests": ["재물운", "직장운"]
    }
    
    start_time = time.time()
    try:
        res = requests.post(f"{BASE_URL}/api/recommend_direct", json=payload)
        end_time = time.time()
        
        if res.status_code == 200:
            data = res.json()
            top3 = data.get("top3", [])
            print(f"✅ Success! Returned {len(top3)} perfumes.")
            print(f"⏱️ Time Taken: {end_time - start_time:.2f} seconds")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"🚨 Error: {e}")

if __name__ == "__main__":
    print("Starting Latency Tests...")
    test_compatibility()
    test_recommend_direct()
    print("\nTests Completed.")
