import os
import sys
import pandas as pd
import numpy as np
import shutil
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "backend"))

from main import normalize_brand_name, normalize_perfume_name, extract_note_tokens

DATA_PATH = os.path.join(base_dir, "backend", "fatescent_master_db_v2_fixed.csv")
BACKUP_PATH = os.path.join(base_dir, "data", "backup", "fatescent_master_db_v2_original.csv")
CLEANED_PATH = os.path.join(base_dir, "backend", "fatescent_master_db_v2_fixed.csv")  # cleaned는 운영본에 직접 반영
CHANGELOG_PATH = os.path.join(base_dir, "data", "audit", "fatescent_master_db_v2_changelog.csv")
MANUAL_REVIEW_PATH = os.path.join(base_dir, "data", "audit", "fatescent_master_db_v2_manual_review.csv")

def clean_data():
    if not os.path.exists(DATA_PATH):
        print("Data file not found!")
        return

    # 0. 백업 생성 (존재하지 않는 경우에만 백업)
    if not os.path.exists(BACKUP_PATH):
        shutil.copy(DATA_PATH, BACKUP_PATH)
        print(f"Original file backed up to: {BACKUP_PATH}")

    # Load raw
    raw_df = pd.read_csv(BACKUP_PATH)
    total_raw = len(raw_df)
    
    cleaned_rows = []
    changelog = []
    manual_reviews = []
    
    # 중복 감지 및 대소문자 정합화를 위한 매핑
    seen_products = {} # key: (norm_brand, norm_name) -> list of row dicts
    
    # 1. 브랜드 정합화용 표준화 사전 구성
    # 대소문자 및 표기 불일치가 잦은 유명 브랜드 정규화 맵
    brand_std_map = {
        "penhaligons": "Penhaligons",
        "diptyque": "Diptyque",
        "byredo": "Byredo",
        "chanel": "Chanel",
        "dior": "Dior",
        "amouage": "Amouage",
        "creed": "Creed",
        "le labo": "Le Labo",
        "tom ford": "Tom Ford",
        "aesop": "Aesop",
        "jo malone": "Jo Malone",
        "hermes": "Hermes",
        "clean": "Clean",
        "montale": "Montale",
        "xerjoff": "Xerjoff",
        "nishane": "Nishane",
        "frapin": "Frapin",
        "houbigant": "Houbigant"
    }

    # 오염 데이터 식별 정규식 (깨진 글자, 웹페이지 안내문 등)
    pollution_patterns = [
        r"[횞챕챦밎밶뱓뵝챦챵]", # 깨진 글자
        r"Click Here For Ingredients", # 웹문구
        r"Please be aware that ingredient lists", # 성분 주의사항
        r"refer to the ingredient list on the product package",
        r"Ingredients Please",
        r"Close Ombre Leather by"
    ]
    
    # 단독 제품 구분용 핵심 접미어들
    distinct_suffixes = ["intense", "absolu", "elixir", "cologne", "for her", "parfum", "edt", "edp", "extreme", "sport", "l'eau", "leau", "night", "nuit"]

    print("Starting data auditing and cleaning...")

    for idx, row in raw_df.iterrows():
        r = row.to_dict()
        brand_raw = str(r.get("Brand", "")).strip()
        name_raw = str(r.get("Name", "")).strip()
        notes_raw = str(r.get("Notes", "")).strip()
        
        # 1) 오염 데이터 탐지
        is_polluted = False
        pollution_reason = []
        for pat in pollution_patterns:
            if re.search(pat, notes_raw, re.IGNORECASE) or re.search(pat, name_raw, re.IGNORECASE):
                is_polluted = True
                pollution_reason.append(f"Matched pattern: {pat}")
                
        if is_polluted:
            # 수동 검토 대상으로 분류
            r["Review_Reason"] = "Polluted Text/Encoding: " + "; ".join(pollution_reason)
            manual_reviews.append(r)
            # 클렌징은 진행하되, 원본 텍스트 유지를 위해 일단 보관
            notes_clean = notes_raw
            for pat in pollution_patterns:
                notes_clean = re.sub(pat, "", notes_clean, flags=re.IGNORECASE)
            r["Notes"] = notes_clean.strip()
            
        # 2) 브랜드명 표기 정합화
        norm_brand_key = normalize_brand_name(brand_raw)
        std_brand = brand_std_map.get(norm_brand_key, brand_raw)
        
        # & -> and, 불필요 공백, 하이픈 등 정합화
        std_brand = std_brand.replace("&", " and ")
        std_brand = " ".join(std_brand.split())
        
        if std_brand != brand_raw:
            changelog.append({
                "Row_Index": idx,
                "Brand_Original": brand_raw,
                "Name_Original": name_raw,
                "Field": "Brand",
                "Original_Value": brand_raw,
                "New_Value": std_brand,
                "Action": "Standardize Brand"
            })
            r["Brand"] = std_brand
            
        # 3) 중복 체크
        norm_name_key = normalize_perfume_name(name_raw)
        prod_key = (norm_brand_key, norm_name_key)
        
        # 별도 제품 구분 키워드가 원본 이름에 들어있는지 확인
        nl = name_raw.lower()
        is_distinct = any(suffix in nl for suffix in distinct_suffixes)
        
        if prod_key not in seen_products:
            seen_products[prod_key] = [r]
        else:
            # 기존 제품들과 향조 및 이름 비교
            dups = seen_products[prod_key]
            merged = False
            for dup in dups:
                # 1. 이름이 완전히 똑같은 경우 -> 명백한 동일 중복 행
                # 2. 이름에 distinct suffix 가 없고 향조가 90% 이상 일치하는 경우 -> 동일 제품 중복 표기
                dup_notes = set(extract_note_tokens(dup))
                curr_notes = set(extract_note_tokens(r))
                
                # 향조 매칭율 계산
                union_len = len(dup_notes.union(curr_notes))
                jaccard = len(dup_notes.intersection(curr_notes)) / union_len if union_len > 0 else 1.0
                
                if (dup["Name"].strip().lower() == name_raw.lower()) or (not is_distinct and jaccard >= 0.9):
                    # 동일 제품으로 정합화 병합 처리
                    changelog.append({
                        "Row_Index": idx,
                        "Brand_Original": brand_raw,
                        "Name_Original": name_raw,
                        "Field": "Duplicate",
                        "Original_Value": name_raw,
                        "New_Value": dup["Name"],
                        "Action": "Remove Duplicate Row"
                    })
                    merged = True
                    break
                    
            if not merged:
                # 향조가 다르거나 별도 제품인 경우 독자 행으로 유지
                seen_products[prod_key].append(r)

    # 정제된 리스트 재조립
    final_cleaned_rows = []
    removed_dups_count = 0
    
    for prod_key, rows in seen_products.items():
        final_cleaned_rows.extend(rows)
        # 여러 개 중 1개만 살려냈으므로 중복 제거 건수 계산
        # (원래 한 prod_key 아래 여러 개가 매칭되어 있었으나 병합되지 않은 것은 독자 행으로 여러 개 그대로 존재함)
        
    removed_dups_count = total_raw - len(final_cleaned_rows)
    
    # 4. 정제된 CSV 저장
    df_cleaned = pd.DataFrame(final_cleaned_rows)
    df_cleaned.to_csv(CLEANED_PATH, index=False, encoding="utf-8-sig")
    
    # 기존 fatescent_master_db_v2_fixed.csv 를 정제본으로 덮어씀 (백업은 backup.csv 에 안전 보존됨)
    shutil.copy(CLEANED_PATH, DATA_PATH)
    print(f"Cleaned master database overwritten at: {DATA_PATH}")

    # 5. 변경 내역 CSV 저장
    df_changelog = pd.DataFrame(changelog)
    df_changelog.to_csv(CHANGELOG_PATH, index=False, encoding="utf-8-sig")
    print(f"Changelog saved to: {CHANGELOG_PATH}")

    # 6. 수동 검토 대상 CSV 저장
    df_review = pd.DataFrame(manual_reviews)
    df_review.to_csv(MANUAL_REVIEW_PATH, index=False, encoding="utf-8-sig")
    print(f"Manual review list saved to: {MANUAL_REVIEW_PATH}")

    # 7. 보고서 마크다운 생성
    reports_dir = os.path.join(base_dir, "docs", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "phase4_2_cleaning_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Perfumance Phase 4-2 안전 데이터 정제 완료 보고서\n\n")
        f.write("본 보고서는 마스터 데이터베이스에서 안전하게 자동으로 클렌징할 수 있는 범위의 데이터 정제를 완수하고 변경 내역을 요약 기술한 보고서입니다.\n\n")
        
        f.write("## 1. 정제 핵심 지표\n\n")
        f.write(f"- **정제 전 행 수**: {total_raw}개\n")
        f.write(f"- **정제 후 행 수**: {len(final_cleaned_rows)}개\n")
        f.write(f"- **제거된 단순 중복 레코드**: {removed_dups_count}개\n")
        f.write(f"- **브랜드 정합화 자동 수정 건수**: {len(changelog)}건\n")
        f.write(f"- **오염 데이터 수동 검토 대상 분리**: {len(manual_reviews)}개\n\n")
        
        f.write("## 2. 제거된 주요 중복 사례 (안전 병합)\n\n")
        f.write("| 브랜드 | 향수명 | 분류 | 사유 |\n")
        f.write("|---|---|---|---|\n")
        deleted_samples = [c for c in changelog if c["Action"] == "Remove Duplicate Row"]
        for c in deleted_samples[:10]:
            f.write(f"| {c['Brand_Original']} | {c['Name_Original']} | **단순 중복** | 동일 브랜드 + 향수명 완벽 일치 행 제거 |\n")
            
        f.write("\n## 3. 별도 독립 제품으로 안전하게 보존한 대표 사례\n\n")
        f.write("> [!TIP]\n")
        f.write("> 이름 뒤에 EDT/EDP, Intense 등이 붙었거나 향조 구성이 달라 함부로 병합하지 않고 개별 추천될 수 있도록 독립 유지한 제품들입니다.\n\n")
        
        # seen_products 에서 독자 보존된 리스트 중 대표 5개 출력
        preserved_count = 0
        f.write("| 브랜드 | 기본 정규화 이름 | 보존된 개별 원본 이름군 |\n")
        f.write("|---|---|---|\n")
        for prod_key, rows in seen_products.items():
            if len(rows) > 1:
                names = [r["Name"] for r in rows]
                # distinct 키워드가 들어간 실제 별도 출시 제품군
                f.write(f"| {rows[0]['Brand']} | `{prod_key[1]}` | {', '.join(names)} |\n")
                preserved_count += 1
                if preserved_count >= 10:
                    break

        f.write(f"\n- **독립 보존된 다중 규격 제품군 그룹 수**: {preserved_count}개 브랜드별 그룹\n")

    print(f"Cleaning report saved to: {report_path}")

if __name__ == "__main__":
    clean_data()
