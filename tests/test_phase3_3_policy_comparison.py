"""
Phase 3-3 추천 정책 다각도 비교 시뮬레이션 (경량 버전).
BASELINE, BALANCED, NO_BRAND_BONUS 3가지 정책만 효율적으로 비교합니다.
"""

import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import (
    RecommendationPolicy,
    BASELINE_POLICY,
    recommend_perfumes,
    df as master_df,
    TAG_TO_KEYWORDS
)

# ---------------------------------------------------------
# 비교할 3가지 정책 선언
# ---------------------------------------------------------
POLICIES = {
    "BASELINE": BASELINE_POLICY,
    
    "BALANCED": RecommendationPolicy(
        name="BALANCED",
        sim_weight=0.40,
        weak_fill_weight=0.20,
        preference_weight=0.35,
        dislike_weight=-0.35,
        brand_bonus=0.03,
        strong_dislike_threshold=0.4,
        strong_dislike_penalty=-0.4,
        hard_filter_threshold=None,
        missing_notes_policy="keep"
    ),
    
    "NO_BRAND_BONUS": RecommendationPolicy(
        name="NO_BRAND_BONUS",
        sim_weight=0.40,
        weak_fill_weight=0.20,
        preference_weight=0.35,
        dislike_weight=-0.35,
        brand_bonus=0.00,
        strong_dislike_threshold=0.4,
        strong_dislike_penalty=-0.4,
        hard_filter_threshold=None,
        missing_notes_policy="keep"
    )
}

# ---------------------------------------------------------
# 대표적인 3가지 시나리오 프로필
# ---------------------------------------------------------
USER_PROFILES = [
    {
        "id": 1, 
        "gender": "남성향", 
        "weak": ["Wood"], 
        "strong": ["Fire"], 
        "pref": ["나무향(우디)"], 
        "dislike": ["꽃향기(플로럴)"],
        "desc": "남성 / 우디 선호 / 플로럴 비선호"
    },
    {
        "id": 2, 
        "gender": "여성향", 
        "weak": ["Fire"], 
        "strong": ["Water"], 
        "pref": ["꽃향기(플로럴)"], 
        "dislike": ["스모키/가죽"],
        "desc": "여성 / 플로럴 선호 / 레더 비선호"
    },
    {
        "id": 3, 
        "gender": "전체", 
        "weak": ["Water"], 
        "strong": ["Metal"], 
        "pref": ["시원한(아쿠아/마린)"], 
        "dislike": ["달콤한(앰버/바닐라)"],
        "desc": "공용 / 아쿠아 선호 / 앰버바닐라 비선호"
    }
]


class TestPolicyComparisonAndStats:
    
    def test_run_policy_experiments(self):
        """3가지 핵심 정책에 따른 추천 결과를 추출하고 순위 변화를 진단합니다."""
        if master_df.empty:
            pytest.skip("향수 데이터가 로드되지 않았습니다")
            
        comparison_records = []
        
        print("\n\n=== 3개 정책 비교 시뮬레이션 결과 ===")
        
        for prof in USER_PROFILES:
            print(f"\n[시나리오 {prof['id']}] {prof['desc']}")
            print(f" - 부족오행: {prof['weak']}, 강한오행: {prof['strong']}")
            print(f" - 선호향조: {prof['pref']}, 비선호향조: {prof['dislike']}")
            
            for p_name, policy in POLICIES.items():
                res = recommend_perfumes(
                    master_df, 
                    prof["weak"], 
                    prof["strong"], 
                    prof["pref"], 
                    prof["dislike"], 
                    "전체 뷰티 브랜드 포함", 
                    prof["gender"],
                    policy=policy
                )
                
                top3 = res.head(3)
                print(f"   ▶ 정책: {p_name}")
                for idx, (_, row) in enumerate(top3.iterrows(), 1):
                    famous_mark = "★" if any(b.lower() in str(row.get("Brand", "")).lower() for b in ["Chanel", "Dior", "Jo Malone", "Diptyque", "Byredo", "Aesop"]) else "  "
                    print(f"      {idx}위. {famous_mark} [{row.get('Brand')}] {row.get('Name')} | 점수: {row.get('score'):.4f} (sim: {row.get('sim'):.2f}, weak: {row.get('weak_fill_avg'):.2f}, pref: {row.get('pref_score'):.2f}, dis: {row.get('dislike_score'):.2f})")
        
        assert True
