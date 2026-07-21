import os
import sys
import pandas as pd
import re

# Add backend to path to reuse the same data path and helper functions
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "backend"))

from main import (
    normalize_brand_name,
    normalize_perfume_name,
    normalize_note_token,
    extract_note_tokens,
    TAG_TO_KEYWORDS,
    FAMOUS_BRANDS,
    ELEMENTS,
    recommend_perfumes
)

DATA_PATH = os.path.join(base_dir, "backend", "fatescent_master_db_v2_fixed.csv")

def run_diagnostics():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    print("==================================================")
    print("Fate Scent MVP Recommendation Data Diagnostics (v2)")
    print("==================================================")
    
    # Load raw file
    raw_df = pd.read_csv(DATA_PATH)
    print(f"1. Raw CSV total rows: {len(raw_df)}")

    # Clean & fill na as done in main.py to analyze exact runtime state
    df_clean = raw_df.copy()
    text_columns = ["Name", "Brand", "Notes", "Description", "matched_keywords", "Top", "Middle", "Base", "Gender"]
    for c in text_columns:
        if c not in df_clean.columns:
            df_clean[c] = ""
        df_clean[c] = df_clean[c].fillna("").astype(str)

    # 1. 동일한 Name을 가진 서로 다른 Brand 조합 수
    name_groups = df_clean.groupby("Name")["Brand"].nunique()
    diff_brands_same_name = (name_groups > 1).sum()
    print(f"2. Number of perfume Names appearing in multiple brands: {diff_brands_same_name}")

    # 2. 정규화 후 동일해지는 Name 수
    norm_names = df_clean["Name"].apply(normalize_perfume_name)
    duplicated_norm_names = norm_names.duplicated().sum()
    print(f"3. Duplicated Names after normalization: {duplicated_norm_names} (out of {len(df_clean)})")

    # 3. 정규화 후 동일해지는 Brand 수
    unique_raw_brands = df_clean["Brand"].nunique()
    unique_norm_brands = df_clean["Brand"].apply(normalize_brand_name).nunique()
    print(f"4. Unique Brands: Raw={unique_raw_brands}, Normalized={unique_norm_brands}")

    # 4. 향조 토큰 중 다른 토큰 내부의 부분 문자열이 되는 키워드 사례
    all_tokens = set()
    for _, row in df_clean.iterrows():
        all_tokens.update(extract_note_tokens(row))
    
    print("\n[Substring Conflicts in Note Tokens]")
    sorted_tokens = sorted(list(all_tokens), key=len)
    conflict_examples = []
    for tok in sorted_tokens:
        if len(tok) < 3 or len(tok) > 12:
            continue
        # Find if tok is a substring of a longer token
        for other in sorted_tokens:
            if len(other) > len(tok) and tok in other:
                # check if not word boundary
                if not re.search(rf"\b{re.escape(tok)}\b", other):
                    conflict_examples.append((tok, other))
                    if len(conflict_examples) >= 7:
                        break
        if len(conflict_examples) >= 7:
            break
            
    for short, long in conflict_examples:
        print(f" - '{short}' is a substring of '{long}' (potential false positive in simple 'in' match)")

    # 5. TAG_TO_KEYWORDS 키워드 중 데이터에서 한 번도 정확 매칭되지 않는 항목
    print("\n[Unused TAG_TO_KEYWORDS Keywords]")
    unused_kws = {}
    for tag, kws in TAG_TO_KEYWORDS.items():
        unused_for_tag = []
        for kw in kws:
            norm_kw = normalize_note_token(kw)
            # check if norm_kw exists as word boundary in any perfume's tokens
            matched_any = False
            for _, row in df_clean.iterrows():
                p_toks = extract_note_tokens(row)
                if any(re.search(rf"\b{re.escape(norm_kw)}\b", t) for t in p_toks):
                    matched_any = True
                    break
            if not matched_any:
                unused_for_tag.append(kw)
        if unused_for_tag:
            unused_kws[tag] = unused_for_tag
            
    for tag, kws in unused_kws.items():
        print(f" - {tag}: {kws}")

    # 6. 성별 필터 입력값으로 실제 프런트가 전송하는 값
    # frontend/src/components/InputForm.tsx를 보면 gender state의 초기값 및 라디오그룹 값은 "여성", "남성"입니다.
    print("\n5. Actual Gender inputs sent by frontend standard flows:")
    print(" - '여성' (from InputForm / DirectRecommendForm)")
    print(" - '남성' (from InputForm / DirectRecommendForm)")

    # 7. final_score 동점 발생 건수 (대표 입력 기준)
    print("\n[Deterministic Tie-breaking Test]")
    # Wood 1.0, Fire 0.0 인 표준 케이스 기준 시뮬레이션
    sim_df = df_clean.copy()
    for c in ["Female_Score", "Male_Score"]:
        sim_df[c] = pd.to_numeric(sim_df[c], errors="coerce").fillna(0.5)
    for e in ELEMENTS:
        sim_df[e] = pd.to_numeric(sim_df[e], errors="coerce").fillna(0.0)
    
    sim_df["element_sum"] = sim_df[ELEMENTS].sum(axis=1)
    sim_df = sim_df[sim_df["element_sum"] > 0].copy()
    
    res = recommend_perfumes(sim_df, ["Wood"], ["Fire"], [], [], "전체 뷰티 브랜드 포함")
    score_counts = res["score"].value_counts()
    ties = score_counts[score_counts > 1]
    print(f" - Total score tie groups: {len(ties)}")
    print(f" - Largest tie group size: {ties.max() if not ties.empty else 0} perfumes sharing the exact same score")
    
    # 8. 유명 브랜드 통계
    famous_brand_perfumes = df_clean[df_clean["Brand"].apply(lambda b: any(f.lower() in str(b).lower() for f in FAMOUS_BRANDS))]
    print(f"\n6. Famous brand bonus eligible perfumes: {len(famous_brand_perfumes)}")

if __name__ == "__main__":
    run_diagnostics()
