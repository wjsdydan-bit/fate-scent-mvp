"""
Phase 3-3 추천 품질 평가 원칙 검증용 테스트 스위트.
기존/신규 정책에 따른 원칙적인 추천 순위를 검증합니다.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import recommend_perfumes, BASELINE_POLICY, RecommendationPolicy

# 테스트용 간이 정책 (결측 패널티가 들어간 가상 정책)
MISSING_PENALTY_POLICY = RecommendationPolicy(
    name="TEST_PENALTY",
    sim_weight=0.55,
    weak_fill_weight=0.20,
    preference_weight=0.18,
    dislike_weight=-0.20,
    brand_bonus=0.0,
    strong_dislike_threshold=None,
    strong_dislike_penalty=0.0,
    hard_filter_threshold=None,
    missing_notes_policy="penalty" # 결측 패널티 적용
)

@pytest.fixture
def policy_expectations_df():
    data = [
        # A: 오행보완 아주 좋음, 취향 전혀 없음
        {"Brand": "BrandX", "Name": "SajuOnly",
         "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
         "Notes": "bergamot", "Top": "", "Middle": "", "Base": "",
         "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5},
        
        # B: 오행보완 중간, 선호 완벽 일치 (우디 선호 시 cedar, sandalwood)
        {"Brand": "BrandY", "Name": "PrefMatch",
         "Wood": 0.5, "Fire": 0.5, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
         "Notes": "cedar, sandalwood", "Top": "", "Middle": "", "Base": "",
         "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5},
         
        # C: 오행보완 매우 높으나 비선호 1개 포함 (스모키/가죽 비선호 시 leather)
        {"Brand": "BrandX", "Name": "SajuWithDislike",
         "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
         "Notes": "bergamot, leather", "Top": "", "Middle": "", "Base": "",
         "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5},
         
        # D: 유명 브랜드이나 본질 점수(오행 및 취향) 매우 낮음
        {"Brand": "Chanel", "Name": "FamousPoorMatch",
         "Wood": 0.0, "Fire": 1.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
         "Notes": "rose", "Top": "", "Middle": "", "Base": "",
         "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5},
         
        # E: 향조 정보 완전 누락 제품
        {"Brand": "BrandZ", "Name": "NoNotesPerfume",
         "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
         "Notes": "", "Top": "", "Middle": "", "Base": "",
         "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5}
    ]
    df = pd.DataFrame(data)
    for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
        df[c] = df[c].fillna("").astype(str)
    df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]
    return df


class TestRecommendationPolicyExpectations:

    def test_principle_1_preference_preference(self, policy_expectations_df):
        res = recommend_perfumes(policy_expectations_df, ["Wood"], ["Fire"], ["나무향(우디)"], [], "전체 뷰티 브랜드 포함")
        pref_match_rank = res[res["Name"] == "PrefMatch"].index[0]
        assert res.loc[pref_match_rank]["pref_score"] > 0.0

    def test_principle_2_dislike_penalty(self, policy_expectations_df):
        res = recommend_perfumes(policy_expectations_df, ["Wood"], ["Fire"], [], ["스모키/가죽"], "전체 뷰티 브랜드 포함")
        dislike_perf = res[res["Name"] == "SajuWithDislike"].iloc[0]
        assert dislike_perf["dislike_score"] > 0.0
        
        saju_only_rank = res[res["Name"] == "SajuOnly"].index[0]
        dislike_rank = res[res["Name"] == "SajuWithDislike"].index[0]
        assert saju_only_rank < dislike_rank

    def test_principle_6_famous_brand_not_overlord(self, policy_expectations_df):
        res = recommend_perfumes(policy_expectations_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        saju_only_rank = res[res["Name"] == "SajuOnly"].index[0]
        famous_poor_rank = res[res["Name"] == "FamousPoorMatch"].index[0]
        assert saju_only_rank < famous_poor_rank

    def test_principle_8_missing_notes_should_not_overrule(self, policy_expectations_df):
        # 결측 패널티가 동작하는 정책 하에서는 취향이 매칭된 PrefMatch가 결측 NoNotesPerfume 보다 우위여야 함
        res = recommend_perfumes(policy_expectations_df, ["Wood"], ["Fire"], ["나무향(우디)"], [], "전체 뷰티 브랜드 포함", policy=MISSING_PENALTY_POLICY)
        
        pref_match_rank = res[res["Name"] == "PrefMatch"].index[0]
        no_notes_rank = res[res["Name"] == "NoNotesPerfume"].index[0]
        assert pref_match_rank < no_notes_rank

    def test_principle_10_multiple_weakest_elements_supported(self, policy_expectations_df):
        res = recommend_perfumes(policy_expectations_df, ["Wood", "Earth"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        assert not res.empty
        # Wood 1.0, Earth 0.0 -> 평균 0.5
        assert res.iloc[0]["weak_fill_avg"] == 0.5

    def test_normalized_deduplication(self):
        # 동일 브랜드, 농도/설명 차이의 두 향수가 하나로 중복 제거되는지 검증
        data = [
            {"Brand": "Creed", "Name": "Millesime Imperial", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
            {"Brand": "Creed", "Name": "Millesime Imperial Eau de Parfum", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""}
        ]
        df = pd.DataFrame(data)
        for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
            df[c] = df[c].fillna("").astype(str)
        df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]
        
        res = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        # 정규화된 기준 ["creed", "millesime imperial"] 에 의해 중복 제거되어 1개만 남아 있어야 함
        assert len(res) == 1

    def test_famous_brand_normalization_matching(self):
        # Jo Malone & London 같은 브랜드도 대소문자 & -> and 치환 후 Jo Malone 보너스가 정상적으로 들어가는지 확인
        data = [
            {"Brand": "Jo Malone & London", "Name": "Wood Sage", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
            {"Brand": "Unknown Brand", "Name": "Some scent", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""}
        ]
        df = pd.DataFrame(data)
        for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
            df[c] = df[c].fillna("").astype(str)
        df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]
        
        # 유명 보너스가 있는 BALANCED_POLICY (0.03 가점) 및 가점 없는 NO_BRAND_BONUS_POLICY 비교
        from main import BALANCED_POLICY, NO_BRAND_BONUS_POLICY
        res_famous = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", policy=BALANCED_POLICY)
        res_nofamous = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", policy=NO_BRAND_BONUS_POLICY)
        
        # BALANCED_POLICY 의 Jo Malone & London 의 점수가 Unknown Brand 의 점수보다 보너스(0.03) 만큼 높아야 함
        score_famous = res_famous[res_famous["Brand"] == "Jo Malone & London"].iloc[0]["score"]
        score_unknown = res_famous[res_famous["Brand"] == "Unknown Brand"].iloc[0]["score"]
        assert score_famous > score_unknown
        
        # NO_BRAND_BONUS_POLICY 에서는 브랜드 가점이 없으므로 두 향수 점수가 완벽히 같아야 함
        score_famous_no = res_nofamous[res_nofamous["Brand"] == "Jo Malone & London"].iloc[0]["score"]
        score_unknown_no = res_nofamous[res_nofamous["Brand"] == "Unknown Brand"].iloc[0]["score"]
        assert score_famous_no == pytest.approx(score_unknown_no)
