import sys
import os
import time
import asyncio
import pandas as pd
from dotenv import load_dotenv

sys.path.append(r"c:\Users\user\Desktop\사주\fate-scent-mvp\backend")

base_dir = r"c:\Users\user\Desktop\사주\fate-scent-mvp\backend"
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

has_key = "GEMINI_API_KEY" in os.environ
print(f"Env Loaded (GEMINI_API_KEY exists): {has_key}")

from main import get_perfume_notes_via_ai, generate_compatibility_result, generate_comprehensive_reading_json, GEMINI_MODEL_NAME

async def run_tests():
    print(f"Testing config: Timeout 30s, Model {GEMINI_MODEL_NAME}")
    
    start = time.time()
    notes = await get_perfume_notes_via_ai("TestBrand", "TestName")
    elapsed = time.time() - start
    print(f"[get_perfume_notes_via_ai] Time: {elapsed:.2f}s, Type: {type(notes).__name__}, Value: '{notes}'")
    
    start = time.time()
    res1 = await generate_compatibility_result(
        user_name="test", gender="여성", saju_name="test_saju", strong="Wood", weak="Water",
        perf_brand="TestBrand", perf_name="TestName", notes_text="water, sea", score=80, perf_vec={"Wood": 0.1, "Water": 0.8}
    )
    elapsed = time.time() - start
    print(f"[generate_compatibility_result] Time: {elapsed:.2f}s, Type: {type(res1).__name__}")
    
    start = time.time()
    df = pd.DataFrame([{"Brand": "TestBrand", "Name": "TestName", "Notes": "water", "Wood": 0.1, "Water": 0.8}])
    res2 = await generate_comprehensive_reading_json(
        user_name="test", gender="여성", saju_name="test_saju", strongest="Wood", weakest="Water",
        top3_df=df, is_birth_time_unknown=True, interests=["연애운"]
    )
    elapsed = time.time() - start
    print(f"[generate_comprehensive_reading_json] Time: {elapsed:.2f}s, Type: {type(res2).__name__}")

asyncio.run(run_tests())
