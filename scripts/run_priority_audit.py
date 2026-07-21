import os
import sys
import pandas as pd
import numpy as np
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "backend"))

from main import recommend_perfumes, df as master_df, ELEMENTS

CLEANED_PATH = os.path.join(base_dir, "backend", "fatescent_master_db_v2_fixed.csv")
PRIORITY_CSV_PATH = os.path.join(base_dir, "data", "audit", "fatescent_priority_audit.csv")
MANUAL_REVIEW_PATH = os.path.join(base_dir, "data", "audit", "fatescent_master_db_v2_manual_review.csv")
CLEANING_REPORT_PATH = os.path.join(base_dir, "docs", "reports", "phase4_3_priority_report.md")

def run_priority_audit():
    if not os.path.exists(CLEANED_PATH):
        print("Cleaned data not found!")
        return

    df = pd.read_csv(CLEANED_PATH)
    
    # 1. 대상 식별
    # Notes 결측 79개
    empty_notes_mask = (df["Notes"].fillna("").str.strip() == "") & \
                       (df["Top"].fillna("").str.strip() == "") & \
                       (df["Middle"].fillna("").str.strip() == "") & \
                       (df["Base"].fillna("").str.strip() == "")
    
    # 오염 데이터 식별 패턴 (이전 단계 분류 기준 유지)
    pollution_patterns = [
        r"[횞챕챦밎밶뱓뵝챦챵]", 
        r"Click Here For Ingredients",
        r"Please be aware that ingredient lists",
        r"refer to the ingredient list on the product package",
        r"Ingredients Please",
        r"Close Ombre Leather by"
    ]
    
    polluted_mask = df.apply(lambda r: any(re.search(pat, str(r.get("Notes", "")), re.IGNORECASE) or 
                                           re.search(pat, str(r.get("Name", "")), re.IGNORECASE) for pat in pollution_patterns), axis=1)
    
    target_mask = empty_notes_mask | polluted_mask
    target_df = df[target_mask].copy()
    
    # 2. 추천 노출 빈도 시뮬레이션
    # 대표적인 사주 입력 프로필 조합 25종 생성
    sim_profiles = []
    # 각 오행이 단독 부족인 경우 5종
    for e in ELEMENTS:
        sim_profiles.append({"weak": [e], "strong": [ELEMENTS[(ELEMENTS.index(e)+2)%5]], "pref": [], "dislike": []})
    # 오행 2개 동률 부족인 경우 10종
    for i in range(len(ELEMENTS)):
        for j in range(i+1, len(ELEMENTS)):
            sim_profiles.append({"weak": [ELEMENTS[i], ELEMENTS[j]], "strong": [ELEMENTS[(i+3)%5]], "pref": [], "dislike": []})
    # 선호/비선호 태그 추가 프로필 10종
    pref_tags_pool = ["나무향(우디)", "꽃향기(플로럴)", "상큼한(시트러스)", "시원한(아쿠아/마린)", "달콤한(앰버/바닐라)"]
    dislike_tags_pool = ["꽃향기(플로럴)", "스모키/가죽", "포근한(머스크)", "과일향(프루티)"]
    for idx in range(10):
        sim_profiles.append({
            "weak": [ELEMENTS[idx % 5]],
            "strong": [ELEMENTS[(idx+2) % 5]],
            "pref": [pref_tags_pool[idx % 5]],
            "dislike": [dislike_tags_pool[idx % 4]]
        })

    # 노출 카운트 맵 구성
    exposure_counts = { (row["Brand"], row["Name"]): 0 for _, row in target_df.iterrows() }

    print(f"Running simulation for {len(sim_profiles)} profiles to check recommendations...")
    for idx, prof in enumerate(sim_profiles, 1):
        res = recommend_perfumes(
            df,
            prof["weak"],
            prof["strong"],
            prof["pref"],
            prof["dislike"],
            "전체 뷰티 브랜드 포함",
            "전체"
        )
        if not res.empty:
            # Top 10에 해당하는 제품들 추출
            top10 = res.head(10)
            for _, row in top10.iterrows():
                key = (row["Brand"], row["Name"])
                if key in exposure_counts:
                    exposure_counts[key] += 1

    # 3. 우선순위 부여
    priority_rows = []
    p1_count, p2_count, p3_count = 0, 0, 0
    auto_cleaned_count = 0
    
    for idx, row in target_df.iterrows():
        b = row["Brand"]
        n = row["Name"]
        notes = str(row["Notes"])
        
        exp = exposure_counts[(b, n)]
        
        # P1/P2/P3 분류
        if exp >= 5:
            pri = "P1"
            p1_count += 1
        elif exp >= 1:
            pri = "P2"
            p2_count += 1
        else:
            pri = "P3"
            p3_count += 1
            
        # 오염 자동 정리가 가능한 부분 처리 (웹페이지 문구나 불필요 성분구문 제거)
        is_cleaned = False
        new_notes = notes
        
        # Click Here 문구 지우기
        if "Click Here For Ingredients" in new_notes:
            new_notes = re.sub(r"Click Here For Ingredients.*", "", new_notes, flags=re.IGNORECASE).strip()
            is_cleaned = True
            
        # 깨진 철자 교정 (Ta챦f -> Taif, h챕liotrope -> heliotrope, mat챕 -> mate, c챔dre -> cedre 등)
        charmap = {
            "Ta챦f": "Taif",
            "h챕liotrope": "heliotrope",
            "mat챕": "mate",
            "c챔dre": "cedre",
            "ol챕or챕sin": "oleoresin"
        }
        for k, v in charmap.items():
            if k in new_notes:
                new_notes = new_notes.replace(k, v)
                is_cleaned = True
                
        # 깨진 유니코드 밎rand Cru뵝 -> Grand Cru 치환
        if "밎rand Cru뵝" in new_notes:
            new_notes = new_notes.replace("밎rand Cru뵝", "Grand Cru")
            is_cleaned = True
        if "밶lcoolat뵝" in new_notes:
            new_notes = new_notes.replace("밶lcoolat뵝", "alcoolat")
            is_cleaned = True
        if "뱓abac blond뵝" in new_notes:
            new_notes = new_notes.replace("뱓abac blond뵝", "tabac blond")
            is_cleaned = True
            
        if is_cleaned:
            auto_cleaned_count += 1
            df.loc[df["Name"] == n, "Notes"] = new_notes
            action = "Auto-Cleaned Encoding/Web Text"
        else:
            action = "Manual Review Required"

        priority_rows.append({
            "Brand": b,
            "Name": n,
            "Notes": notes,
            "Cleaned_Notes": new_notes,
            "Exposure_Count": exp,
            "Priority": pri,
            "Action": action
        })

    # 정제된 본 마스터 DB 갱신 저장
    df.to_csv(CLEANED_PATH, index=False, encoding="utf-8-sig")
    print(f"Notes field auto-cleaned in master database: {CLEANED_PATH}")

    # 우선순위 CSV 저장
    df_priority = pd.DataFrame(priority_rows)
    df_priority.to_csv(PRIORITY_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"Priority Audit list saved to: {PRIORITY_CSV_PATH}")
    
    # 보고서 작성
    with open(CLEANING_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Perfumance Phase 4-3 결측·오염 데이터 우선순위화 보고서\n\n")
        f.write("본 보고서는 결측 및 오염이 포함된 향수들을 실제 추천 시뮬레이션의 노출 빈도 기준으로 우선순위(P1/P2/P3)로 매핑하고 가공한 보고서입니다.\n\n")
        
        f.write("## 1. 우선순위 분류 지표\n\n")
        f.write(f"- **P1 (자주 추천되는 핵심 제품, 노출수 >= 5)**: {p1_count}개\n")
        f.write(f"- **P2 (가끔 추천되는 제품, 노출수 1~4)**: {p2_count}개\n")
        f.write(f"- **P3 (추천에 거의 미노출되는 제품, 노출수 0)**: {p3_count}개\n")
        f.write(f"- **자동으로 인코딩/웹문구가 정제된 건수**: {auto_cleaned_count}건\n\n")
        
        f.write("## 2. 노출빈도가 높은 최우선 해결 대상 (P1 목록 샘플)\n\n")
        f.write("| 브랜드 | 향수명 | 노출 횟수 | 우선순위 | 조치 내역 |\n")
        f.write("|---|---|---|---|---|\n")
        p1_samples = df_priority[df_priority["Priority"] == "P1"]
        for _, r in p1_samples.head(15).iterrows():
            f.write(f"| {r['Brand']} | {r['Name']} | {r['Exposure_Count']} | {r['Priority']} | {r['Action']} |\n")
            
        f.write("\n## 3. P2 분류 목록 샘플 (가끔 노출)\n\n")
        f.write("| 브랜드 | 향수명 | 노출 횟수 | 우선순위 | 조치 내역 |\n")
        f.write("|---|---|---|---|---|\n")
        p2_samples = df_priority[df_priority["Priority"] == "P2"]
        for _, r in p2_samples.head(10).iterrows():
            f.write(f"| {r['Brand']} | {r['Name']} | {r['Exposure_Count']} | {r['Priority']} | {r['Action']} |\n")
            
        f.write("\n## 4. 자동 정제 전후 대조표 예시\n\n")
        f.write("| 브랜드 | 향수명 | 기존 Notes | 정제 후 Notes |\n")
        f.write("|---|---|---|---|\n")
        cleaned_samples = df_priority[df_priority["Action"] == "Auto-Cleaned Encoding/Web Text"]
        for _, r in cleaned_samples.head(10).iterrows():
            f.write(f"| {r['Brand']} | {r['Name']} | `{r['Notes']}` | `{r['Cleaned_Notes']}` |\n")

    print(f"Priority Audit report saved to: {CLEANING_REPORT_PATH}")

if __name__ == "__main__":
    run_priority_audit()
