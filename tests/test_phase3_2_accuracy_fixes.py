"""
Phase 3-2 추천 정확도 및 결정론 보장 테스트 스위트.
향조 토큰 매칭, 성별 표준화, 브랜드/이름 정규화 매칭, 결정론적 정렬 등을 검증합니다.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import (
    normalize_note_token,
    extract_note_tokens,
    keyword_hit_score_for_row,
    normalize_gender_filter,
    normalize_brand_name,
    normalize_perfume_name,
    find_perfume_in_db,
    recommend_perfumes,
    df as master_df
)

# =========================================================
# A. 향조 토큰 매칭 테스트
# =========================================================

class TestNoteTokenMatching:
    
    def test_normalize_tokens(self):
        # 대소문자 소문자화 및 공백 단일화
        assert normalize_note_token("  Orange   Blossom-Notes! ") == "orange blossom notes"
        # 특수문자 제거
        assert normalize_note_token("Rose & Jasmine") == "rose jasmine"
    
    def test_extract_tokens_various_separators(self):
        row = {
            "Notes": "bergamot, rose/jasmine; musk|tea\nvanilla",
            "Top": "lemon",
            "Middle": None,
            "Base": np.nan,
            "matched_keywords": "sweet"
        }
        tokens = extract_note_tokens(row)
        assert "bergamot" in tokens
        assert "rose" in tokens
        assert "jasmine" in tokens
        assert "musk" in tokens
        assert "tea" in tokens
        assert "vanilla" in tokens
        assert "lemon" in tokens
        assert "sweet" in tokens
        assert "orange" not in tokens

    def test_pear_vs_spearmint(self):
        # 1. spearmint 향조에 pear가 매칭되지 않아야 함
        perfume_tokens = {"spearmint", "peppermint"}
        # 유저가 '과일향(프루티)' 선택 시 pear 키워드가 들어감
        user_keywords = ["pear"]
        score = keyword_hit_score_for_row(perfume_tokens, user_keywords)
        assert score == 0.0

        # 2. blackpepper 향조에 pear/pepper 매칭 검증
        perfume_tokens2 = {"blackpepper"}
        assert keyword_hit_score_for_row(perfume_tokens2, ["pear"]) == 0.0
        # blackpepper와 black pepper는 붙어 있으면 pepper에 단어 경계 매칭이 안 됨
        assert keyword_hit_score_for_row(perfume_tokens2, ["pepper"]) == 0.0
        
        # 3. black pepper (단어 분리) 향조에 pepper 매칭
        perfume_tokens3 = {"black pepper"}
        assert keyword_hit_score_for_row(perfume_tokens3, ["pepper"]) == 1.0

        # 4. exact match
        perfume_tokens4 = {"pear"}
        assert keyword_hit_score_for_row(perfume_tokens4, ["pear"]) == 1.0

    def test_empty_and_nan_tokens(self):
        assert keyword_hit_score_for_row(set(), ["pear"]) == 0.0
        assert keyword_hit_score_for_row({"pear"}, []) == 0.0
        assert keyword_hit_score_for_row(set(), []) == 0.0
        
    def test_additional_boundary_token_matching(self):
        # 1. None 및 NaN 입력 처리 안전성
        assert keyword_hit_score_for_row(set(), [None, np.nan]) == 0.0
        
        # 2. 중복 향조가 점수를 중복 증가시키지 않음
        # perfume_tokens 세트이므로 애초에 중복이 제거되며,
        # user_keywords 에 중복이 있어도 tags_to_keywords 에서 중복 제거됨
        perfume_tokens = {"rose", "jasmine"}
        user_keywords = ["rose", "rose"]
        # keywords 분모가 2인 경우 1 hit이면 0.5가 되어 중복 가산이 안 됨
        score = keyword_hit_score_for_row(perfume_tokens, user_keywords)
        assert score == 1.0

        # 3. 여러 사용자 키워드 중 일부만 맞을 때 정확한 비율
        user_keywords2 = ["rose", "jasmine", "musk", "vanilla"] # 4개 중 2개 매칭
        assert keyword_hit_score_for_row(perfume_tokens, user_keywords2) == pytest.approx(0.5)

        # 4. orange blossom 같은 다중 단어 매칭
        assert keyword_hit_score_for_row({"orange blossom"}, ["orange blossom"]) == 1.0
        assert keyword_hit_score_for_row({"orange"}, ["orange blossom"]) == 0.0

        # 5. 하이픈 포함 향조
        # wood-sage -> 정규화에 의해 "wood sage"가 됨
        toks = {normalize_note_token("wood-sage")}
        assert "wood sage" in toks
        assert keyword_hit_score_for_row(toks, ["wood sage"]) == 1.0

        # 6. 괄호 포함 향조
        # jasmin (egypt) -> "jasmin egypt"
        toks2 = {normalize_note_token("jasmin (egypt)")}
        assert "jasmin egypt" in toks2
        assert keyword_hit_score_for_row(toks2, ["jasmin egypt"]) == 1.0

        # 7. pepper / black pepper 관계 검증
        # 유저가 pepper를 싫어하면 black pepper도 걸려야 함
        assert keyword_hit_score_for_row({"black pepper"}, ["pepper"]) == 1.0

        # 8. fig / figs 관계 검증 (pear vs spearmint 와 동일)
        # fig가 figs에 걸리느냐? \bfig\b 는 figs에 매칭되지 않아야 함 (단어 경계)
        assert keyword_hit_score_for_row({"figs"}, ["fig"]) == 0.0

        # 9. sap / sapodilla 관계 검증
        assert keyword_hit_score_for_row({"sapodilla"}, ["sap"]) == 0.0

        # 10. mat / mate / aromatic / tomato 관계 검증
        assert keyword_hit_score_for_row({"mate"}, ["mat"]) == 0.0
        assert keyword_hit_score_for_row({"aromatic"}, ["mat"]) == 0.0
        assert keyword_hit_score_for_row({"tomato"}, ["mat"]) == 0.0


# =========================================================
# B. 성별 표준화 테스트
# =========================================================

class TestGenderNormalization:
    
    def test_normalization_mapping(self):
        # 남성 계열
        assert normalize_gender_filter("남성") == "male"
        assert normalize_gender_filter("남성향") == "male"
        assert normalize_gender_filter("male") == "male"
        assert normalize_gender_filter("man") == "male"
        assert normalize_gender_filter("  MEN ") == "male"
        
        # 여성 계열
        assert normalize_gender_filter("여성") == "female"
        assert normalize_gender_filter("여성향") == "female"
        assert normalize_gender_filter("female") == "female"
        assert normalize_gender_filter("woman") == "female"
        assert normalize_gender_filter("women") == "female"
        
        # 중성 계열
        assert normalize_gender_filter("중성") == "unisex"
        assert normalize_gender_filter("공용") == "unisex"
        assert normalize_gender_filter("unisex") == "unisex"
        
        # 무시 / 전체
        assert normalize_gender_filter("") is None
        assert normalize_gender_filter(None) is None
        assert normalize_gender_filter("xyz") is None

    def test_additional_gender_boundaries(self):
        # 1. 남성, 남성향, male의 추천 결과가 동일한지 검증하기 위한 데이터셋
        dummy_data = []
        for i in range(35):
            dummy_data.append({
                "Brand": "Test", "Name": f"P{i}",
                "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0,
                "Gender": "men" if i < 15 else "women",
                "Female_Score": 0.1 if i < 15 else 0.9,
                "Male_Score": 0.9 if i < 15 else 0.1,
                "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""
            })
        df = pd.DataFrame(dummy_data)
        for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
            df[c] = df[c].fillna("").astype(str)
        df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]

        # 남성, 남성향, male 입력 결과 비교
        res_kor = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "남성")
        res_kor_h = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "남성향")
        res_eng = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "male")
        
        assert res_kor["Name"].tolist() == res_eng["Name"].tolist()
        assert res_kor_h["Name"].tolist() == res_eng["Name"].tolist()

        # 2. 여성, 여성향, female 입력 결과 동일 비교
        res_fem_kor = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "여성")
        res_fem_kor_h = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "여성향")
        res_fem_eng = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "female")
        assert res_fem_kor["Name"].tolist() == res_fem_eng["Name"].tolist()
        assert res_fem_kor_h["Name"].tolist() == res_fem_eng["Name"].tolist()

        # 3. 후보 30개 이상일 때 필터 작동 유지 및 30개 미만일 때 전체 후보 fallback 검증
        # 10개만 있는 데이터셋
        small_df = df.iloc[:10].copy()
        res_small = recommend_perfumes(small_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "남성향")
        # 필터링 결과 30개 미만이므로 필터를 미적용한 10개 전체 결과가 리턴되어야 함
        assert len(res_small) == 10

        # 4. 빈 문자열, None 및 알 수 없는 임의 성별 문자열 입력 시 필터 작동 안하고 전체 리턴
        res_empty = recommend_perfumes(small_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "")
        res_none = recommend_perfumes(small_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", None)
        res_rand = recommend_perfumes(small_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함", "xyz")
        assert len(res_empty) == 10
        assert len(res_none) == 10
        assert len(res_rand) == 10


# =========================================================
# C. 향수명·브랜드 매칭 안전성 테스트
# =========================================================

class TestPerfumeBrandMatching:
    
    @pytest.fixture(autouse=True)
    def setup_mock_db(self, monkeypatch):
        # 테스트용 가상 db 데이터 로드
        mock_data = [
            {"Brand": "Chanel", "Name": "No.5", "Notes": "rose", "Top": "", "Middle": "", "Base": "", "Gender": "unisex"},
            {"Brand": "Dior", "Name": "No.5", "Notes": "jasmine", "Top": "", "Middle": "", "Base": "", "Gender": "unisex"},
            {"Brand": "Jo Malone", "Name": "Wood Sage & Sea Salt (Cologne)", "Notes": "sea salt", "Top": "", "Middle": "", "Base": "", "Gender": "unisex"},
            {"Brand": "Christian Dior", "Name": "Sauvage", "Notes": "lavender", "Top": "", "Middle": "", "Base": "", "Gender": "unisex"}
        ]
        mock_df = pd.DataFrame(mock_data)
        monkeypatch.setattr("main.df", mock_df)

    def test_same_name_different_brand_matching(self):
        # 1. 브랜드가 주어진 경우 정확히 그 브랜드 향수 선택
        res_chanel = find_perfume_in_db("Chanel", "No.5")
        assert res_chanel is not None
        assert res_chanel["Brand"] == "Chanel"
        assert res_chanel["Notes"] == "rose"
        
        res_dior = find_perfume_in_db("Dior", "No.5")
        assert res_dior is not None
        assert res_dior["Brand"] == "Dior"
        assert res_dior["Notes"] == "jasmine"
        
        # 2. 브랜드는 맞으나 향수명이 다른 경우 실패 (다른 브랜드 동명 제품을 선택하지 않음)
        res_wrong = find_perfume_in_db("Chanel", "Jadore")
        assert res_wrong is None

        # 3. 브랜드가 존재하지 않지만(None) 향수명만 있는 경우 매칭 허용
        res_no_brand = find_perfume_in_db("", "No.5")
        assert res_no_brand is not None
        assert res_no_brand["Name"] == "No.5"

    def test_normalization_differences(self):
        # edp/edt 등 농도 접미사 및 괄호 처리 정규화
        res = find_perfume_in_db("jo malone", "wood sage and sea salt")
        assert res is not None
        assert res["Brand"] == "Jo Malone"

    def test_additional_brand_matching_boundaries(self):
        # 1. 브랜드가 제공되었으나 존재하지 않는 브랜드인 경우 None
        assert find_perfume_in_db("NonExistBrand", "No.5") is None

        # 2. 브랜드명이 다른 브랜드명의 일부 문자열인 경우 오탐 방지
        # 예: Dior 로 검색했을 때 Christian Dior가 매칭되면 안 됨 (완전 일치 우선이므로 Dior의 No.5가 나옴)
        res = find_perfume_in_db("Dior", "Sauvage")
        assert res is None # Dior에는 Sauvage 가 없음 (Christian Dior에만 있음)


# =========================================================
# D. 결정론적 정렬 테스트
# =========================================================

class TestDeterministicSorting:
    
    def test_stable_sort_ties(self):
        # 모든 오행 및 취향 점수가 같은 4개의 향수
        data = [
            {"Brand": "BrandB", "Name": "PerfumeZ", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
            {"Brand": "BrandA", "Name": "PerfumeY", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
            {"Brand": "BrandA", "Name": "PerfumeX", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
            {"Brand": "BrandB", "Name": "PerfumeY", "Wood": 1.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "bergamot", "Top": "", "Middle": "", "Base": ""},
        ]
        df = pd.DataFrame(data)
        for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
            df[c] = df[c].fillna("").astype(str)
        df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]
        
        # 다중 정렬 기준: Brand ASC -> Name ASC
        res = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        
        assert res.iloc[0]["Brand"] == "BrandA" and res.iloc[0]["Name"] == "PerfumeX"
        assert res.iloc[1]["Brand"] == "BrandA" and res.iloc[1]["Name"] == "PerfumeY"
        assert res.iloc[2]["Brand"] == "BrandB" and res.iloc[2]["Name"] == "PerfumeY"
        assert res.iloc[3]["Brand"] == "BrandB" and res.iloc[3]["Name"] == "PerfumeZ"

        # 입력 데이터 순서를 뒤섞어서 셔플링한 다음 정렬해도 결과는 완벽히 같아야 함 (결정론적 재현성)
        df_shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        res_shuffled = recommend_perfumes(df_shuffled, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        
        assert res["Name"].tolist() == res_shuffled["Name"].tolist()
        assert res["Brand"].tolist() == res_shuffled["Brand"].tolist()

    def test_deterministic_sorting_individual_scores(self):
        # final_score, sim, weak_fill_avg, pref_score, dislike_score 간의 정렬 관계가 명확히 작동하는지 확인
        data = [
            # 1. score가 더 높은 것 우선
            {"Brand": "BrandA", "Name": "HighPerfume", "Wood": 0.8, "Fire": 0.2, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "tea, bergamot", "Top": "", "Middle": "", "Base": ""},
            # 2. score 동점, sim이 높은 것 우선
            {"Brand": "BrandB", "Name": "HighSimPerfume", "Wood": 0.5, "Fire": 0.5, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "tea", "Top": "", "Middle": "", "Base": ""},
            # 3. score, sim 동점, weak_fill_avg 높은 것 우선
            {"Brand": "BrandC", "Name": "HighWeakPerfume", "Wood": 0.3, "Fire": 0.7, "Earth": 0.0, "Metal": 0.0, "Water": 0.0, "Gender": "unisex", "Female_Score": 0.5, "Male_Score": 0.5, "Notes": "tea", "Top": "", "Middle": "", "Base": ""},
        ]
        df = pd.DataFrame(data)
        for c in ["Name", "Brand", "Notes", "Top", "Middle", "Base", "Gender"]:
            df[c] = df[c].fillna("").astype(str)
        df["all_text"] = df["Name"] + " " + df["Brand"] + " " + df["Notes"]
        
        res = recommend_perfumes(df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
        # 정렬이 예외 없이 수행되는지 검증
        assert len(res) == 3
