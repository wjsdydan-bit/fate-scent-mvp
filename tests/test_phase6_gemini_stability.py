import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import backend.main as main

# Mock Data
mock_df = pd.DataFrame([
    {
        "Brand": "Diptyque", "Name": "Philosykos", "Notes": "fig leaf, fig, coconut, cedar",
        "Top": "fig leaf", "Middle": "fig", "Base": "cedar", "Gender": "unisex",
        "Male_Score": 0.5, "Female_Score": 0.5,
        "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0
    }
])

@pytest.mark.asyncio
async def test_gemini_timeout_fallback():
    """
    1. Gemini API 호출 시 TimeoutError 발생 상황 검증
    """
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=asyncio.TimeoutError("Gemini Request Timeout"))
    
    with patch("backend.main.client", mock_client):
        reading_res = await main.generate_comprehensive_reading_json(
            user_name="홍길동",
            gender="남성",
            saju_name="갑자 월경 신축",
            strongest="Wood",
            weakest="Water",
            top3_df=mock_df,
            is_birth_time_unknown=False,
            interests=["재물운"]
        )
        assert reading_res is not None
        assert "hero_title" in reading_res
        # summary 에 가장 강한 오행인 Wood(나무) 또는 부족한 오행 Water(물) 기운 설명이 들어가는지 검증
        assert "나무" in reading_res["summary"] or "Wood" in reading_res["summary"]
        assert "물" in reading_res["summary"] or "Water" in reading_res["summary"]
        
        compat_res = await main.generate_compatibility_result(
            user_name="홍길동",
            gender="남성",
            saju_name="갑자 월경 신축",
            strong="Wood",
            weak="Water",
            perf_brand="Diptyque",
            perf_name="Philosykos",
            notes_text="fig leaf, fig, coconut, cedar",
            score=85,
            perf_vec={"Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0}
        )
        assert compat_res is not None
        assert "one_liner" in compat_res
        assert compat_res["good_reasons"] != []

@pytest.mark.asyncio
async def test_gemini_500_error_fallback():
    """
    2. Gemini API 호출 시 500/429 Exception 발생 상황 검증
    """
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("Internal Server Error (500)"))
    
    with patch("backend.main.client", mock_client):
        reading_res = await main.generate_comprehensive_reading_json(
            user_name="성춘향",
            gender="여성",
            saju_name="병인 정묘 기사",
            strongest="Fire",
            weakest="Metal",
            top3_df=mock_df,
            is_birth_time_unknown=True,
            interests=["연애운"]
        )
        assert reading_res is not None
        assert "advantages" in reading_res["saju_analysis"]
        assert "불" in reading_res["summary"] or "Fire" in reading_res["summary"]

@pytest.mark.asyncio
async def test_gemini_malformed_json_fallback():
    """
    3. Gemini API가 깨진 JSON 또는 비정상 포맷을 반환할 때 JSON 파싱 예외 복구 검증
    """
    mock_resp = MagicMock()
    mock_resp.text = "MALFORMED_JSON_TEXT_FROM_GEMINI"
    mock_resp.parsed = None
    
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    
    with patch("backend.main.client", mock_client):
        compat_res = await main.generate_compatibility_result(
            user_name="홍길동",
            gender="남성",
            saju_name="갑자 월경 신축",
            strong="Wood",
            weak="Water",
            perf_brand="Diptyque",
            perf_name="Philosykos",
            notes_text="fig leaf, fig, coconut, cedar",
            score=60,
            perf_vec={"Wood": 1.0}
        )
        assert compat_res is not None
        assert "one_liner" in compat_res
        assert any(keyword in compat_res["compatibility_detail"] for keyword in ["편이에요", "수준이에요", "아쉬운"])

@pytest.mark.asyncio
async def test_gemini_missing_api_key_fallback():
    """
    4. API 키 누락(client = None) 상태 시 즉시 fallback 반환 검증
    """
    with patch("backend.main.client", None):
        reading_res = await main.generate_comprehensive_reading_json(
            user_name="임꺽정",
            gender="남성",
            saju_name="무진 기사 경오",
            strongest="Earth",
            weakest="Wood",
            top3_df=mock_df,
            is_birth_time_unknown=False,
            interests=["직업운"]
        )
        assert reading_res is not None
        assert "흙" in reading_res["summary"] or "Earth" in reading_res["summary"]
