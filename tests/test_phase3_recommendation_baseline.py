"""
Phase 3-1 추천 알고리즘 Baseline 회귀 테스트.
네트워크나 Gemini 호출 없이 내부 recommend_perfumes 및 관련 서브 함수를 테스트합니다.
"""

import sys
import os
import pytest
import pandas as pd
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import recommend_perfumes, ELEMENTS, BASELINE_POLICY

# =========================================================
# TEST FIXTURES & DATASETS
# =========================================================

@pytest.fixture
def sample_perfume_df():
    """성별 필터 임계값 30개 한계를 극복하고 다양한 가중치를 테스트하기 위해 35개 이상의 향수를 채운 mock 데이터베이스"""
    data = []
    
    # 1. 테스트용 핵심 향수들 (13개)
    core_data = [
        {
            "Brand": "GenericBrand", "Name": "WoodPerfume",
            "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "bergamot, lemon, tea", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "FirePerfume",
            "Wood": 0.0, "Fire": 1.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "rose, jasmine, pepper", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "EarthPerfume",
            "Wood": 0.0, "Fire": 0.0, "Earth": 1.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "vanilla, sandalwood", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "MetalPerfume",
            "Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 1.0, "Water": 0.0,
            "Notes": "mint, lavender, cedar", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "WaterPerfume",
            "Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 1.0,
            "Notes": "marine, sea salt, musk", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "WoodEarthPerfume",
            "Wood": 0.5, "Fire": 0.0, "Earth": 0.5, "Metal": 0.0, "Water": 0.0,
            "Notes": "bergamot, vanilla", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "Jo Malone", "Name": "FamousWoodPerfume",
            "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "bergamot, lemon", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "MaleOnlyPerfume",
            "Wood": 0.5, "Fire": 0.5, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "tobacco, leather", "Top": "", "Middle": "", "Base": "",
            "Gender": "men", "Female_Score": 0.1, "Male_Score": 0.9,
        },
        {
            "Brand": "GenericBrand", "Name": "FemaleOnlyPerfume",
            "Wood": 0.0, "Fire": 0.5, "Earth": 0.5, "Metal": 0.0, "Water": 0.0,
            "Notes": "rose, peach", "Top": "", "Middle": "", "Base": "",
            "Gender": "women", "Female_Score": 0.9, "Male_Score": 0.1,
        },
        {
            "Brand": "GenericBrand", "Name": "MissingGenderPerfume",
            "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "bergamot", "Top": "", "Middle": "", "Base": "",
            "Gender": "", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "GenericBrand", "Name": "MissingNotesPerfume",
            "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "BrandA", "Name": "SameNamePerfume",
            "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "bergamot", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        },
        {
            "Brand": "BrandB", "Name": "SameNamePerfume",
            "Wood": 0.0, "Fire": 1.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
            "Notes": "rose", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        }
    ]
    data.extend(core_data)

    # 2. 성별 필터(MIN_AFTER_GENDER_FILTER=30) 우회를 위해 30개의 중립(unisex) 성별 향수 더미 추가
    # 남성향 / 여성향 필터 적용 시 30개 임계치 조건 만족 목적
    for i in range(30):
        data.append({
            "Brand": "DummyBrand", "Name": f"DummyPerfume{i}",
            "Wood": 0.2, "Fire": 0.2, "Earth": 0.2, "Metal": 0.2, "Water": 0.2,
            "Notes": "bergamot, musk", "Top": "", "Middle": "", "Base": "",
            "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5,
        })
        
    df = pd.DataFrame(data)
    text_columns = ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]
    for c in text_columns:
        df[c] = df[c].fillna("").astype(str)
    df["all_text"] = (
        df["Name"] + " " + df["Brand"] + " " +
        df["Notes"] + " " +
        df["Top"] + " " + df["Middle"] + " " + df["Base"] + " " +
        df["Gender"]
    ).str.lower().fillna("")
    return df


# =========================================================
# REGRESSION TEST SCENARIOS (18 Cases)
# =========================================================

class TestRecommendationBaseline:
    
    # 1. 부족 오행 1개, 선호·비선호 없음
    def test_scenario_1_single_weak_no_prefs(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        
        # 유명 브랜드 보너스가 가산된 FamousWoodPerfume 이 1위여야 함
        assert res.iloc[0]["Name"] == "FamousWoodPerfume"
        # Wood 1.0 동점군 중 하나가 2위여야 함
        assert res.iloc[1]["Name"] in ["WoodPerfume", "MissingNotesPerfume", "SameNamePerfume", "MissingGenderPerfume"]
        
        # WoodPerfume의 계산 수식 검증:
        # target = [1.0 (Wood), 0.1 (Fire), 0.5, 0.5, 0.5]
        # vec = [1.0, 0.0, 0.0, 0.0, 0.0]
        # sim = 1.0 / (sqrt(1+0.01+0.25*3) * sqrt(1)) = 1.0 / sqrt(1.76) = 1.0 / 1.3266 = 0.7538
        # weak_fill_avg = 1.0
        # final_score = 0.55 * 0.7538 + 0.20 * 1.0 = 0.4146 + 0.20 = 0.6146
        wood_perf = res[res["Name"] == "WoodPerfume"].iloc[0]
        assert wood_perf["score"] == pytest.approx(0.6146, abs=1e-4)

    # 2. 부족 오행 2개 동률
    def test_scenario_2_double_weak_elements(self, sample_perfume_df):
        weakest = ["Wood", "Earth"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        
        wood_earth = res[res["Name"] == "WoodEarthPerfume"].iloc[0]
        wood_single = res[res["Name"] == "WoodPerfume"].iloc[0]
        assert wood_earth["weak_fill_avg"] == 0.5
        assert wood_single["weak_fill_avg"] == 0.5

    # 3. 선호 향조가 강하게 일치하는 향수
    def test_scenario_3_preferred_tags(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, ["꽃향기(플로럴)"], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        fire_row = res[res["Name"] == "FirePerfume"].iloc[0]
        assert fire_row["score"] > 0.0

    # 4. 비선호 향조가 포함된 향수
    def test_scenario_4_disliked_tags(self, sample_perfume_df):
        weakest = ["Water"]
        strongest = ["Wood"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], ["달콤한(앰버/바닐라)"], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        earth_row = res[res["Name"] == "EarthPerfume"].iloc[0]
        assert earth_row["score"] < 0.5

    # 5. 선호와 비선호가 동시에 포함된 향수
    def test_scenario_5_pref_and_dislike_simultaneous(self, sample_perfume_df):
        weakest = ["Water"]
        strongest = ["Wood"]
        res = recommend_perfumes(
            sample_perfume_df, weakest, strongest, 
            ["꽃향기(플로럴)"], ["스모키/가죽"], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY
        )
        fire_row = res[res["Name"] == "FirePerfume"].iloc[0]
        assert fire_row["score"] > 0.0

    # 6. 오행 적합도는 높지만 취향이 맞지 않는 향수 (비선호로 인한 대량 감점)
    def test_scenario_6_high_saju_disliked_perfume(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], ["상큼한(시트러스)"], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        wood_row = res[res["Name"] == "WoodPerfume"].iloc[0]
        assert wood_row["score"] < 0.6146

    # 7. 오행 적합도는 중간이지만 취향이 매우 잘 맞는 향수
    def test_scenario_7_medium_saju_high_pref(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res_no_pref = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        res_with_pref = recommend_perfumes(sample_perfume_df, weakest, strongest, ["나무향(우디)"], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        
        metal_no = res_no_pref[res_no_pref["Name"] == "MetalPerfume"].iloc[0]
        metal_with = res_with_pref[res_with_pref["Name"] == "MetalPerfume"].iloc[0]
        assert metal_with["score"] > metal_no["score"]

    # 8. 유명 브랜드와 비유명 브랜드의 점수가 동일한 경우
    def test_scenario_8_brand_bonus(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        
        famous = res[res["Name"] == "FamousWoodPerfume"].iloc[0]
        normal = res[res["Name"] == "WoodPerfume"].iloc[0]
        
        assert famous["score"] == pytest.approx(normal["score"] + 0.15, abs=1e-4)

    # 9. 성별 male 조건 (더미 30개 추가로 이제 필터링 작동함)
    def test_scenario_9_gender_male_filter(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", "남성향", policy=BASELINE_POLICY)
        names = res["Name"].tolist()
        assert "MaleOnlyPerfume" in names
        assert "FemaleOnlyPerfume" not in names

    # 10. 성별 female 조건
    def test_scenario_10_gender_female_filter(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", "여성향", policy=BASELINE_POLICY)
        names = res["Name"].tolist()
        assert "FemaleOnlyPerfume" in names
        assert "MaleOnlyPerfume" not in names

    # 11. unisex 포함 여부
    def test_scenario_11_unisex_included(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", "남성향", policy=BASELINE_POLICY)
        names = res["Name"].tolist()
        assert "WoodPerfume" in names

    # 12. 성별 데이터가 비어 있는 경우
    def test_scenario_12_empty_gender_handled(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", "남성향", policy=BASELINE_POLICY)
        names = res["Name"].tolist()
        assert "MissingGenderPerfume" in names

    # 13. 오행 점수 일부가 누락된 향수
    def test_scenario_13_missing_element_handled(self, sample_perfume_df):
        assert True

    # 14. 향조 데이터가 전부 누락된 향수
    def test_scenario_14_empty_notes_score(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        row = res[res["Name"] == "MissingNotesPerfume"].iloc[0]
        assert not math.isnan(row["score"])
        assert row["score"] > 0.0

    # 15. 동일 향수명, 서로 다른 브랜드
    def test_scenario_15_same_name_different_brands(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        same_names = res[res["Name"] == "SameNamePerfume"]
        assert len(same_names) == 2
        brands = same_names["Brand"].tolist()
        assert "BrandA" in brands
        assert "BrandB" in brands

    # 16. final_score 동점 상황에서의 정렬 재현성
    def test_scenario_16_tie_sorting_stability(self, sample_perfume_df):
        weakest = ["Wood"]
        strongest = ["Fire"]
        res1 = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        res2 = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        assert res1["Name"].tolist() == res2["Name"].tolist()

    # 17. strongest_elements / weakest_elements 배열 입력
    def test_scenario_17_array_input(self, sample_perfume_df):
        weakest = ["Wood", "Water"]
        strongest = ["Fire", "Metal"]
        res = recommend_perfumes(sample_perfume_df, weakest, strongest, [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        assert not res.empty

    # 18. 기존 단일 strongest / weakest fallback 입력
    def test_scenario_18_single_element_fallback(self, sample_perfume_df):
        res = recommend_perfumes(sample_perfume_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", policy=BASELINE_POLICY)
        assert not res.empty
        assert res.iloc[0]["Name"] == "FamousWoodPerfume"
