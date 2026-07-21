import os
import sys
import pandas as pd
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "backend"))

from main import (
    normalize_brand_name,
    normalize_perfume_name,
    normalize_note_token,
    extract_note_tokens,
    TAG_TO_KEYWORDS,
    FAMOUS_BRANDS
)

DATA_PATH = os.path.join(base_dir, "backend", "fatescent_master_db_v2_fixed.csv")

def audit_data():
    if not os.path.exists(DATA_PATH):
        print("Data file not found!")
        return

    df = pd.read_csv(DATA_PATH)
    total_perfumes = len(df)
    
    # 1. Notes/Top/Middle/Base가 모두 빈 향수
    empty_notes_mask = (
        df["Notes"].fillna("").str.strip() == ""
    ) & (
        df["Top"].fillna("").str.strip() == ""
    ) & (
        df["Middle"].fillna("").str.strip() == ""
    ) & (
        df["Base"].fillna("").str.strip() == ""
    )
    empty_notes_count = empty_notes_mask.sum()
    empty_notes_examples = df[empty_notes_mask][["Brand", "Name"]].head(10).values.tolist()

    # 2. 성별 unknown 데이터
    gender_col = df["Gender"].fillna("").str.strip().str.lower()
    unknown_gender_mask = (gender_col == "") | (gender_col == "unknown")
    unknown_gender_count = unknown_gender_mask.sum()
    unknown_gender_examples = df[unknown_gender_mask][["Brand", "Name", "Gender"]].head(5).values.tolist()

    # 3. 정규화 후 중복 향수명 분석 & 실제 다른 제품 오병합 위험 사례 식별
    df["brand_norm"] = df["Brand"].fillna("").apply(normalize_brand_name)
    df["name_norm"] = df["Name"].fillna("").apply(normalize_perfume_name)
    
    # 동일 브랜드 내 정규화 이름이 중복되는 경우 추출
    dups = df[df.duplicated(subset=["brand_norm", "name_norm"], keep=False)].copy()
    
    unique_dup_groups = dups.groupby(["brand_norm", "name_norm"])
    dup_details = []
    
    # 오병합 위험 키워드 (농도, 한정판, 출시연도 등)
    diff_product_keywords = ["intense", "absolu", "elixir", "edt", "edp", "parfum", "cologne", "extreme", "sport", "l'eau", "leau", "night", "nuit", "black", "gold", "red", "summer", "edition", "limited", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    
    risk_cases = []
    safe_dups = []
    
    for (b_norm, n_norm), group in unique_dup_groups:
        row_list = group.to_dict(orient="records")
        # 이 그룹 내에서 향조 차이 체크
        notes_list = [set(extract_note_tokens(r)) for r in row_list]
        names_list = [r["Name"] for r in row_list]
        
        # 이름들 사이에 실제 제품 구분 키워드가 들어있는지 확인
        is_actually_different = False
        for name in names_list:
            nl = name.lower()
            if any(k in nl for k in diff_product_keywords):
                is_actually_different = True
                break
                
        # 향조 차이 세트 분석
        notes_diff = set()
        if len(notes_list) >= 2:
            notes_diff = notes_list[0].symmetric_difference(notes_list[1])
            
        case_info = {
            "brand": row_list[0]["Brand"],
            "names": names_list,
            "norm_name": n_norm,
            "notes_diff": list(notes_diff)[:5],
            "notes_diff_count": len(notes_diff)
        }
        
        if is_actually_different:
            risk_cases.append(case_info)
        else:
            safe_dups.append(case_info)

    # 4. 동일 브랜드 내 이름이 비슷한 제품 (정규화는 다르지만 유사)
    # 예: "Acqua Di Gio" 와 "Acqua Di Gio Profondo"
    similar_names = []
    # 간단히 동일 브랜드 내에서 한 이름이 다른 이름의 접두사/포함되는 관계를 일부 조사
    brand_groups = df.groupby("Brand")
    for b_name, group in brand_groups:
        names = group["Name"].tolist()
        if len(names) < 2:
            continue
        names = sorted(list(set(names)), key=len)
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                n1 = names[i]
                n2 = names[j]
                if len(n1) > 4 and n1.lower() in n2.lower():
                    # 너무 긴 접미어가 붙은 실제 독립 제품
                    # 예: Chanel Chance / Chanel Chance Eau Tendre
                    similar_names.append((b_name, n1, n2))
                    if len(similar_names) >= 15:
                        break
            if len(similar_names) >= 15:
                break
        if len(similar_names) >= 15:
            break

    # 5. 브랜드명 표기 불일치 (정규화 후 동일해지는 브랜드 수 분석)
    raw_brands = set(df["Brand"].fillna("").str.strip().unique())
    norm_brand_map = {}
    for rb in raw_brands:
        nb = normalize_brand_name(rb)
        if nb:
            if nb not in norm_brand_map:
                norm_brand_map[nb] = []
            norm_brand_map[nb].append(rb)
            
    brand_mismatches = {k: v for k, v in norm_brand_map.items() if len(v) > 1}

    # 6. TAG_TO_KEYWORDS 미사용 키워드
    unused_kws = {}
    for tag, kws in TAG_TO_KEYWORDS.items():
        unused_for_tag = []
        for kw in kws:
            norm_kw = normalize_note_token(kw)
            # check if exists
            matched_any = False
            for _, row in df.iterrows():
                p_toks = row.get("note_tokens_set")
                if p_toks is None or not isinstance(p_toks, set):
                    p_toks = extract_note_tokens(row)
                if any(re.search(rf"\b{re.escape(norm_kw)}\b", t) for t in p_toks):
                    matched_any = True
                    break
            if not matched_any:
                unused_for_tag.append(kw)
        if unused_for_tag:
            unused_kws[tag] = unused_for_tag

    # 7. 한글 향조와 영문 향조의 매칭 공백
    # Notes 데이터에 한글이 포함된 향수 건수 검토
    korean_in_notes_count = 0
    korean_examples = []
    for _, row in df.iterrows():
        notes_str = str(row.get("Notes", ""))
        # 한글 검사 정규식
        if re.search(r"[ㄱ-ㅎㅏ-ㅣ가-힣]", notes_str):
            korean_in_notes_count += 1
            if len(korean_examples) < 10:
                korean_examples.append((row["Brand"], row["Name"], notes_str))

    # docs/reports 디렉토리 생성 및 마크다운 파일 쓰기
    os.makedirs(os.path.join(base_dir, "docs", "reports"), exist_ok=True)
    report_path = os.path.join(base_dir, "docs", "reports", "phase4_data_quality_audit.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Perfumance Phase 4-1 데이터 품질 진단 보고서\n\n")
        f.write("본 문서는 추천 알고리즘 정밀화를 위해 마스터 데이터베이스 내의 오차 요인을 상세 진단하고 분류한 감사 보고서입니다.\n\n")
        
        f.write("## 1. 품질 핵심 통계 요약\n\n")
        f.write(f"- **전체 향수 수**: {total_perfumes}개\n")
        f.write(f"- **향조 데이터 결측 (Notes/Top/Middle/Base가 모두 빈 것)**: {empty_notes_count}개 (전체 대비 {empty_notes_count/total_perfumes*100:.2f}%)\n")
        f.write(f"- **성별 Unknown (알 수 없음) 향수**: {unknown_gender_count}개 (전체 대비 {unknown_gender_count/total_perfumes*100:.2f}%)\n")
        f.write(f"- **정규화 후 이름이 중복되는 그룹**: {len(risk_cases) + len(safe_dups)}개\n")
        f.write(f"  - *오병합 위험이 높은 제품 (EDT/EDP, Intense 등)*: {len(risk_cases)}개\n")
        f.write(f"  - *단순 중복/병합 안전 제품*: {len(safe_dups)}개\n")
        f.write(f"- **브랜드 표기 불일치 종류**: {len(brand_mismatches)}건\n")
        f.write(f"- **한글 포함 향조 데이터 수**: {korean_in_notes_count}개\n\n")
        
        f.write("## 2. 오병합 위험도가 높은 중복 사례 (Intense, Absolu, Elixir, EDT/EDP 등)\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> 아래 향수들은 정규화 시 이름이 같아져 중복 필터링될 위험이 있으나, 실제로는 완전히 다른 제품군(농도, 한정판, 리뉴얼 등)으로 향조와 용도가 다른 경우입니다.\n\n")
        f.write("| 브랜드 | 정규화 이름 | 원본 이름들 | 향조 차이 개수 | 주요 상이 향조 | 분류 |\n")
        f.write("|---|---|---|---|---|---|\n")
        for c in risk_cases[:15]:
            diff_notes_str = ", ".join(c["notes_diff"]) if c["notes_diff"] else "없음"
            f.write(f"| {c['brand']} | `{c['norm_name']}` | {', '.join(c['names'])} | {c['notes_diff_count']} | {diff_notes_str} | **수동 검토 (병합 금지)** |\n")
            
        f.write("\n## 3. 단순 중복 및 안전 병합 대상 사례\n\n")
        f.write("| 브랜드 | 정규화 이름 | 원본 이름들 | 향조 차이 개수 | 분류 |\n")
        f.write("|---|---|---|---|---|\n")
        for c in safe_dups[:15]:
            f.write(f"| {c['brand']} | `{c['norm_name']}` | {', '.join(c['names'])} | {c['notes_diff_count']} | **자동 병합/삭제 가능** |\n")
            
        f.write("\n## 4. 동일 브랜드 내 이름이 유사한 실제 별도 제품\n\n")
        f.write("| 브랜드 | 기본 제품명 | 유사 하위 제품명 | 분류 |\n")
        f.write("|---|---|---|---|\n")
        for b, n1, n2 in similar_names[:15]:
            f.write(f"| {b} | {n1} | {n2} | **유지 (독립 제품)** |\n")

        f.write("\n## 5. 브랜드명 표기 불일치 리스트\n\n")
        f.write("| 정규화 브랜드명 | 데이터 상의 실제 브랜드 표기 종류 | 분류 |\n")
        f.write("|---|---|---|\n")
        for k, v in list(brand_mismatches.items())[:15]:
            f.write(f"| `{k}` | {', '.join(v)} | **자동 수정 가능 (정합화)** |\n")

        f.write("\n## 6. 향조 데이터 누락 (Notes 결측) 주요 사례\n\n")
        f.write("| 브랜드 | 향수명 | 분류 |\n")
        f.write("|---|---|---|\n")
        for b, n in empty_notes_examples[:15]:
            f.write(f"| {b} | {n} | **수동 보완 필요 (Gemini 오프라인 정제)** |\n")

        f.write("\n## 7. TAG_TO_KEYWORDS 미사용 키워드 리스트\n\n")
        f.write("| 태그 종류 | 미사용 키워드 리스트 | 분류 |\n")
        f.write("|---|---|---|\n")
        for tag, kws in list(unused_kws.items())[:10]:
            f.write(f"| {tag} | {', '.join(kws)} | **유지 또는 대체** |\n")
            
        f.write("\n## 8. 한글 향조 포함 주요 사례 (매칭 공백 발생)\n\n")
        f.write("| 브랜드 | 향수명 | 한글 포함 향조 데이터 | 분류 |\n")
        f.write("|---|---|---|---|\n")
        for b, n, note in korean_examples[:10]:
            f.write(f"| {b} | {n} | `{note}` | **수동 번역/정제 필요** |\n")

    print(f"Data Quality Audit successfully generated at: {report_path}")

if __name__ == "__main__":
    audit_data()
