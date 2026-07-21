import sys
import os
import time
import asyncio
import pandas as pd
from dotenv import load_dotenv

sys.path.append(r"c:\Users\user\Desktop\사주\fate-scent-mvp\backend")

# Don't use real .env to force fallback
os.environ.pop("GEMINI_API_KEY", None)

from main import get_perfume_notes_via_ai, generate_compatibility_result, generate_comprehensive_reading_json

async def run_tests():
    print("Running Fallback Tests...")
    
    # 1. get_perfume_notes_via_ai
    notes = await get_perfume_notes_via_ai("TestBrand", "TestName")
    assert notes == "", f"Expected empty string for fallback notes, got {notes}"
    print("[get_perfume_notes_via_ai] Fallback Test Passed")
    
    # 2. generate_compatibility_result
    res1 = await generate_compatibility_result(
        user_name="test", gender="여성", saju_name="test_saju", strong="Wood", weak="Water",
        perf_brand="TestBrand", perf_name="TestName", notes_text="water, sea", score=80, perf_vec={"Wood": 0.1, "Water": 0.8}
    )
    assert isinstance(res1, dict), "Expected dict"
    assert "one_liner" in res1, "Missing expected fallback key"
    print("[generate_compatibility_result] Fallback Test Passed")
    
    # 3. generate_comprehensive_reading_json
    df = pd.DataFrame([{"Brand": "TestBrand", "Name": "TestName", "Notes": "water", "Wood": 0.1, "Water": 0.8}])
    res2 = await generate_comprehensive_reading_json(
        user_name="test", gender="여성", saju_name="test_saju", strongest="Wood", weakest="Water",
        top3_df=df, is_birth_time_unknown=True, interests=["연애운"]
    )
    assert isinstance(res2, dict), "Expected dict"
    assert "hero_title" in res2, "Missing expected fallback key"
    print("[generate_comprehensive_reading_json] Fallback Test Passed")

asyncio.run(run_tests())
