import sys
import os
import time
import asyncio
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

base_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
load_dotenv(os.path.join(base_dir, ".env"))

if "GEMINI_API_KEY" not in os.environ:
    print("Test Skipped: GEMINI_API_KEY is not set in backend/.env")
    sys.exit(0)

from main import get_perfume_notes_via_ai, generate_compatibility_result, generate_comprehensive_reading_json

async def run_tests():
    print("Running Live Gemini Tests...")
    
    start = time.time()
    notes = await get_perfume_notes_via_ai("TestBrand", "TestName")
    elapsed = time.time() - start
    print(f"[get_perfume_notes_via_ai] Time: {elapsed:.2f}s, Fallback used: {notes == ''}, Type: {type(notes).__name__}")
    
    start = time.time()
    res1 = await generate_compatibility_result(
        user_name="test", gender="여성", saju_name="test_saju", strong="Wood", weak="Water",
        perf_brand="TestBrand", perf_name="TestName", notes_text="water, sea", score=80, perf_vec={"Wood": 0.1, "Water": 0.8}
    )
    elapsed = time.time() - start
    is_fallback = (res1.get("one_liner") == "운명의 향✨")
    print(f"[generate_compatibility_result] Time: {elapsed:.2f}s, Fallback used: {is_fallback}, Type: {type(res1).__name__}")
    
    start = time.time()
    df = pd.DataFrame([{"Brand": "TestBrand", "Name": "TestName", "Notes": "water", "Wood": 0.1, "Water": 0.8}])
    res2 = await generate_comprehensive_reading_json(
        user_name="test", gender="여성", saju_name="test_saju", strongest="Wood", weakest="Water",
        top3_df=df, know_time=True, interests=["연애운"]
    )
    elapsed = time.time() - start
    is_fallback2 = ("'당신의 흐름은 분명합니다.'" in res2.get("hero_title", ""))
    print(f"[generate_comprehensive_reading_json] Time: {elapsed:.2f}s, Fallback used: {is_fallback2}, Type: {type(res2).__name__}")

asyncio.run(run_tests())
