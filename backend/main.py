from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import math
import os
import json
import asyncio
import time

from dotenv import load_dotenv
load_dotenv()

from korean_lunar_calendar import KoreanLunarCalendar
from duckduckgo_search import DDGS
try:
    from openai import AsyncOpenAI
    OPENAI_SDK_AVAILABLE = True
except Exception:
    OPENAI_SDK_AVAILABLE = False

app = FastAPI(title="Fate Scent API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(base_dir, "fatescent_master_db_v2_fixed.csv")

ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
ELEMENTS_KO = {
    "Wood": "목(木/나무)", "Fire": "화(火/불)", "Earth": "토(土/흙)",
    "Metal": "금(金/쇠)", "Water": "수(水/물)"
}
ELEMENT_EMOJI = {"Wood": "🌳", "Fire": "🔥", "Earth": "🏔️", "Metal": "⚙️", "Water": "💧"}


TAG_TO_KEYWORDS = {
    "꽃향기(플로럴)": ["floral", "rose", "jasmine", "white floral", "neroli", "ylang", "tuberose", "iris"],
    "과일향(프루티)": ["fruity", "berry", "apple", "pear", "peach", "plum", "fig", "blackcurrant"],
    "나무향(우디)": ["woody", "cedar", "sandalwood", "vetiver", "patchouli", "moss", "oud"],
    "상큼한(시트러스)": ["citrus", "bergamot", "lemon", "orange", "grapefruit", "yuzu", "lime", "mandarin"],
    "포근한(머스크)": ["musk", "white musk", "clean musk", "soft musk"],
    "달콤한(앰버/바닐라)": ["amber", "vanilla", "tonka", "benzoin", "gourmand", "sweet"],
    "시원한(아쿠아/마린)": ["aquatic", "marine", "sea", "sea salt", "watery", "ozonic"],
    "스모키/가죽": ["smoky", "incense", "leather", "tobacco", "animalic"]
}

ELEMENT_KEYWORDS = {
    "Wood": [
        "bergamot", "lemon", "mandarin", "grapefruit", "orange", 
        "petitgrain", "green", "galbanum", "bamboo", "tea", "cypress",
        "apple", "fig", "neroli", "citrus"
    ],
    "Fire": [
        "jasmine", "rose", "ylang", "tuberose", "blossom", "peony", 
        "geranium", "lily", "saffron", "leather", "tobacco", "incense", 
        "pepper", "cinnamon", "carnation", "magnolia", "freesia", "orchid", "spicy"
    ],
    "Earth": [
        "vanilla", "tonka", "patchouli", "iris", "benzoin", "peach", 
        "pear", "heliotrope", "violet", "oakmoss", "vetiver", "sandalwood", 
        "chocolate", "caramel", "honey", "almond", "plum", "amber", "sweet"
    ],
    "Metal": [
        "white musk", "lavender", "cardamom", "nutmeg", "coriander", 
        "ginger", "mint", "aldehyde", "cedar", "metallic", 
        "eucalyptus", "rosemary", "juniper", "sage", "pine", "herb"
    ],
    "Water": [
        "musk", "ambergris", "sea", "marine", "aquatic", "salt", 
        "seaweed", "water", "cucumber", "melon", "calone", "castoreum", "civet"
    ]
}

FAMOUS_BRANDS = [
    "Jo Malone", "Diptyque", "Byredo", "Aesop", "Chanel", "Dior", "Clean",
    "Forment", "Tamburins", "Nonfiction", "Le Labo", "Maison Francis Kurkdjian",
    "Tom Ford", "Hermes", "Creed", "Penhaligon", "Acqua di Parma"
]

client = None
if OPENAI_SDK_AVAILABLE:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = AsyncOpenAI(api_key=api_key)

df = pd.DataFrame()

def load_data():
    global df
    if not os.path.exists(DATA_PATH):
        print(f"Warning: Data file not found at {DATA_PATH}")
        return

    try:
        temp_df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    except Exception:
        temp_df = pd.read_csv(DATA_PATH)

    text_columns = ["Name", "Brand", "Notes", "Description", "matched_keywords", "Top", "Middle", "Base", "Gender"]
    for c in text_columns:
        if c not in temp_df.columns:
            temp_df[c] = ""
        temp_df[c] = temp_df[c].fillna("").astype(str)

    for c in ["Female_Score", "Male_Score"]:
        if c not in temp_df.columns:
            temp_df[c] = 0.5
        temp_df[c] = pd.to_numeric(temp_df[c], errors="coerce").fillna(0.5)

    for e in ELEMENTS:
        if e not in temp_df.columns:
            temp_df[e] = 0.0
        temp_df[e] = pd.to_numeric(temp_df[e], errors="coerce").fillna(0.0)

    temp_df["all_text"] = (
        temp_df["Name"] + " " + temp_df["Brand"] + " " +
        temp_df["Notes"] + " " + temp_df["matched_keywords"] + " " +
        temp_df["Top"] + " " + temp_df["Middle"] + " " + temp_df["Base"] + " " +
        temp_df["Gender"]
    ).str.lower().fillna("")

    temp_df["element_sum"] = temp_df[ELEMENTS].sum(axis=1)
    temp_df = temp_df[temp_df["element_sum"] > 0].copy()

    ban_words = ["sample", "discovery", "set", "gift", "miniature"]
    mask = ~temp_df["Name"].str.lower().apply(lambda x: any(w in x for w in ban_words))
    temp_df = temp_df[mask].copy()

    drop_keys = ["Brand", "Name"]
    for c in drop_keys:
        if c not in temp_df.columns:
            temp_df[c] = ""
    global df
    df = temp_df.drop_duplicates(subset=drop_keys).reset_index(drop=True)
    print(f"Loaded {len(df)} perfumes successfully.")

load_data()

# =========================================================
# UTILITIES AND LOGIC
# =========================================================

def safe_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def tags_to_keywords(tags):
    kws = []
    for t in tags:
        kws.extend(TAG_TO_KEYWORDS.get(t, []))
    return sorted(set([k.lower().strip() for k in kws if k]))

def keyword_hit_score(text, keywords):
    if not keywords:
        return 0.0
    text = safe_text(text).lower()
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)

def extract_matching_notes(row, target_element, top_n=3):
    text = f"{safe_text(row.get('matched_keywords', ''))} {safe_text(row.get('Notes', ''))} {safe_text(row.get('Description', ''))}".lower()
    candidates = ELEMENT_KEYWORDS.get(target_element, [])
    hits = [kw for kw in candidates if kw in text]
    return hits[:top_n]

def get_real_saju_elements(year, month, day, hour=None, minute=None):
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)
    gapja_str = cal.getGapJaString()
    gapja = gapja_str.split()
    if len(gapja) < 3:
        return None

    year_char, month_char, day_char = gapja[0], gapja[1], gapja[2]
    saju_chars = [year_char[0], year_char[1], month_char[0], month_char[1], day_char[0], day_char[1]]
    saju_name = f"{year_char} {month_char} {day_char}"
    
    pillars = {
        "year": {"stem": year_char[0], "branch": year_char[1]},
        "month": {"stem": month_char[0], "branch": month_char[1]},
        "day": {"stem": day_char[0], "branch": day_char[1]},
        "hour": {"stem": "?", "branch": "?"}
    }

    if hour is not None and minute is not None:
        stems, branches = "갑을병정무기경신임계", "자축인묘진사오미신유술해"
        total_mins = hour * 60 + minute
        time_branch_idx = 0 if total_mins >= 1410 or total_mins < 90 else ((total_mins - 90) // 120 + 1) % 12
        time_branch = branches[time_branch_idx]
        day_stem_idx = stems.find(day_char[0])
        time_stem = stems[((day_stem_idx % 5) * 2 + time_branch_idx) % 10] if day_stem_idx != -1 else "갑"
        saju_chars.extend([time_stem, time_branch])
        saju_name += f" {time_stem}{time_branch}시"
        
        pillars["hour"]["stem"] = time_stem
        pillars["hour"]["branch"] = time_branch
    else:
        saju_name += " (시간 모름·6글자 기준)"

    element_map = {
        '갑': 'Wood', '을': 'Wood', '병': 'Fire', '정': 'Fire', '무': 'Earth', '기': 'Earth',
        '경': 'Metal', '신': 'Metal', '임': 'Water', '계': 'Water',
        '인': 'Wood', '묘': 'Wood', '사': 'Fire', '오': 'Fire', '진': 'Earth', '술': 'Earth',
        '축': 'Earth', '미': 'Earth', '신': 'Metal', '유': 'Metal', '해': 'Water', '자': 'Water', '申': 'Metal'
    }
    
    for key, val in pillars.items():
        val["stem_element"] = element_map.get(val["stem"], "Unknown")
        val["branch_element"] = element_map.get(val["branch"], "Unknown")

    counts = {e: 0 for e in ELEMENTS}
    for c in saju_chars:
        if c in element_map:
            counts[element_map[c]] += 1

    sorted_e = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return {
        "saju_name": saju_name,
        "counts": counts, 
        "strongest": sorted_e[0][0],
        "weakest": sorted_e[-1][0],
        "gapja_str": gapja_str,
        "pillars": pillars 
    }

def find_perfume_in_db(brand_input: str, name_input: str):
    if df.empty:
        return None
    brand_q = brand_input.strip().lower()
    name_q = name_input.strip().lower()

    mask = (
        df["Brand"].str.lower().str.contains(brand_q, regex=False, na=False) &
        df["Name"].str.lower().str.contains(name_q, regex=False, na=False)
    )
    hits = df[mask]
    if len(hits) == 0:
        mask2 = df["Name"].str.lower().str.contains(name_q, regex=False, na=False)
        hits = df[mask2]
    if len(hits) == 0:
        return None
        
    hits = hits.copy()
    hits["_name_len"] = hits["Name"].str.len()
    return hits.sort_values("_name_len").iloc[0].to_dict()

async def get_perfume_notes_via_ai(brand: str, name: str) -> str:
    if not client:
        return ""
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 향수 전문가야. 향수의 주요 노트를 영어로 콤마 구분해서만 답해. 예: bergamot, rose, sandalwood, musk. 다른 말은 하지 마. 항상 가장 대표적이고 공식적인 노트만 답해."},
                {"role": "user", "content": f"향수: {brand} - {name}\n이 향수의 공식 주요 향 노트를 알려줘."}
            ],
            temperature=0,
            seed=42,
            max_tokens=50
        )
        return resp.choices[0].message.content.strip() if resp and resp.choices else ""
    except Exception:
        return ""

def compute_perfume_element_vector(notes_text: str) -> dict[str, float]:
    scores = {"Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0}
    
    if not isinstance(notes_text, str) or not notes_text.strip():
        return scores

    flattened_keywords = []
    for element, keywords in ELEMENT_KEYWORDS.items():
        for kw in keywords:
            flattened_keywords.append({"keyword": kw.lower(), "element": element})
            
    # Sort by descending length to prevent partial match overlaps (e.g. "white musk" vs "musk")
    flattened_keywords.sort(key=lambda x: len(x["keyword"]), reverse=True)

    notes_list = [n.strip().lower() for n in notes_text.split(",")]

    for note in notes_list:
        for item in flattened_keywords:
            if item["keyword"] in note:
                scores[item["element"]] += 1.0
                break

    total_score = sum(scores.values())
    if total_score > 0:
        for element in scores:
            scores[element] = round((scores[element] / total_score), 3)

    return scores

def compute_compatibility_score(user_counts: dict, perfume_vec: dict, weak: str, strong: str) -> int:
    total_perf = sum(perfume_vec.values()) or 1
    perf_norm = {e: perfume_vec.get(e, 0) / total_perf for e in ELEMENTS}

    # 사주의 균형(Balance)를 맞추는 것이 핵심!
    # 부족한 기운(weak)을 채워주면 가산점, 넘치는 기운(strong)을 더하면 감점
    complement = perf_norm.get(weak, 0.0)
    overload = perf_norm.get(strong, 0.0)

    # 기본 55점에서 시작. 부족한 기운이 많으면 최고점 향해 증가, 넘치는 기운이 많으면 크게 감점
    raw = 0.55 + (0.85 * complement) - (0.50 * overload)
    score = max(0.0, min(1.0, raw))
    return int(round(score * 100))

def get_gender_tone(gender):
    if gender == "여성":
        return {"suffix": "님", "style": "부드럽고 감성적인 톤"}
    elif gender == "남성":
        return {"suffix": "님", "style": "깔끔하고 직관적인 톤"}
    return {"suffix": "님", "style": "중립적이고 친근한 톤"}

def _strip_code_fences(text: str) -> str:
    if not text:
        return ""
    t = str(text)
    t = t.replace("```json", "").replace("```html", "").replace("```", "")
    return t.strip()

async def generate_compatibility_result(
    user_name: str, gender: str, saju_name: str, strong: str, weak: str,
    perf_brand: str, perf_name: str, notes_text: str, score: int, perf_vec: dict
) -> dict:
    strong_ko = ELEMENTS_KO.get(strong, strong)
    weak_ko = ELEMENTS_KO.get(weak, weak)
    top2_perf = sorted(perf_vec.items(), key=lambda x: x[1], reverse=True)[:2]
    top2_names = [ELEMENTS_KO[e] for e, v in top2_perf if v > 0]
    gender_tone = get_gender_tone(gender)["style"]

    # Score-dependent good/bad reason counts
    if score >= 75:
        good_count, bad_count = 4, 1
    elif score >= 50:
        good_count, bad_count = 2, 2
    else:
        good_count, bad_count = 1, 4

    # Per-element note breakdown
    element_notes_breakdown = []
    for elem in ELEMENTS:
        val = perf_vec.get(elem, 0)
        matched_kws = [kw for kw in ELEMENT_KEYWORDS.get(elem, []) if kw in notes_text.lower()]
        element_notes_breakdown.append(f"{ELEMENT_EMOJI[elem]} {ELEMENTS_KO[elem]}: {val:.0%} ({'노트: ' + ', '.join(matched_kws[:3]) if matched_kws else '해당 노트 없음'})")
    element_breakdown_str = "\n".join(element_notes_breakdown)

    fallback = {
        "one_liner": f"{'운명의 향✨' if score >= 75 else '🤔 애증의 향' if score >= 50 else '😅 기운 역주행 향'}",
        "score_comment": f"{'이 향수 뿌리면 인생 펼쳐짐 🌈' if score >= 75 else '뿌릴까 말까… 고민 각' if score >= 50 else '당장 화장대에서 퇴출시켜 🚨'}",
        "good_reasons": [f"{top2_names[0] if top2_names else '이 향'}의 기운이 개성을 살려줄 수 있어요"] * good_count,
        "bad_reasons": [f"부족한 {weak_ko} 기운 보완엔 아쉬울 수 있어요"] * bad_count,
        "perf_element_summary": f"이 향수는 {', '.join(top2_names[:2]) if top2_names else '다양한'} 기운이 주를 이루고 있어요.",
        "compatibility_detail": f"궁합 점수 {score}점은 {'좋은 편이에요.' if score >= 70 else '보통 수준이에요.' if score >= 50 else '조금 아쉬운 편이에요.'}"
    }

    if not client:
        return fallback

    top2_str = ", ".join([f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]}({v:.0%})" for e, v in top2_perf if v > 0])
    prompt = f"""
너는 명리학과 조향을 연결해 설명하는 전문가야.
결과는 **반드시 JSON만** 출력해. 다른 말 일절 금지. (AI 투는 최대한 지양하고, 유쾌한 친구같이 말해줘)

[핵심 규칙 - 절대 어기지 말 것]
유저의 사주에서 넘치는 기운({strong_ko})이 향수에 없는 것은 **매우 긍정적인 현상**입니다. (애초에 넘치는 기운은 더 이상 필요하지 않습니다).
반대로 유저에게 부족한 기운({weak_ko})이 향수에 있다면 그 향수는 유저의 밸런스를 채워주는 귀중한 향수입니다.
따라서 "유저의 강한 기운({strong_ko})이 이 향수에 없어서 아쉽다"는 식의 해설은 **절대로** 작성하지 마세요. 강한 기운이 향수에 없는 것은 '아쉬운 점'이 아니라 '잘 맞는 이유'이거나 당연한 것입니다.

[사용자 정보]
이름: {user_name}, 성별: {gender}(문체: {gender_tone})
사주: {saju_name}
강한 기운: {strong_ko}, 부족한 기운: {weak_ko}

[향수 정보]
브랜드: {perf_brand}, 향수명: {perf_name}
노트: {notes_text}
향수의 실제 주요 오행 데이터: {top2_str}
궁합 점수: {score}점

[향수의 오행별 노트 분석]
{element_breakdown_str}

[출력 JSON 형식]
{{
  "one_liner": "유저의 오행과 향수의 오행이 만나면 어떻게 되는지 유쾌하고 직관적으로 표현 (20자 이내. 예: '물과 불이 만나 소화됨💨', '나무에 물 줬더니 대나무 됨🎋', '쇠가 쇠를 만나 칼 됨🗡️')",
  "score_comment": "궁합 점수가 {score}점이라는 점을 **반드시** 명심하고, 다음 10개의 점수 구간에 맞춰 15자 이내의 리액션을 작성해:
- 91~100점: '운명 그 자체! 평생 안고 가세요 💯'
- 81~90점: '최상의 바이브! 매일 뿌려도 좋아요 🌟'
- 71~80점: '기분 좋은 예감! 자주 손이 갈 거예요 ✨'
- 61~70점: '나쁘지 않은 호환성! 무난하게 쓰기 좋음 🌿'
- 51~60점: '가끔 기분 전환용으로만 쓰세요 🤔'
- 41~50점: '글쎄요 코에는 안 맞을 확률이 높음 🤷'
- 31~40점: '차라리 안 뿌리는 게 나을지도 🙅'
- 21~30점: '이건 좀 아닌 듯! 방향제로 쓰세요 🚨'
- 11~20점: '불협화음 폭발! 옆 사람도 피할 향 🌪️'
- 0~10점: '당장 갖다 버리세요 🗑️'",
  "good_reasons": ["잘 맞는 이유(30자 이내)"] * {good_count},
  "bad_reasons": ["아쉬운 점(30자 이내)"] * {bad_count},
  "perf_element_summary": "이 향수의 5가지 오행에 대해 매칭된 향수 노트를 **모두 이해하기 쉬운 한국어로 번역**해서 설명하고, 이 향수가 유저 사주상 부족한 기운({weak_ko})을 어떻게 보완하거나 넘치는 기운({strong_ko})을 악화시키는지 명확하게 설명할 것 (반드시 3~4줄 분량 내외로 핵심만)",
  "compatibility_detail": "궁합 점수에 대한 종합 설명 (3~4문장. 왜 이 점수인지, 어떤 상황에 쓰면 좋을지)"
}}
""".strip()

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 명리학+조향 전문가야. 반드시 JSON만 출력해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        raw = resp.choices[0].message.content if resp and resp.choices else ""
        raw = _strip_code_fences(raw)
        data = json.loads(raw)
        required = ["one_liner", "good_reasons", "bad_reasons", "perf_element_summary", "compatibility_detail"]
        if all(k in data for k in required):
            return data
        return fallback
    except Exception:
        return fallback


def _apply_gender_filter(work: pd.DataFrame, user_gender: str) -> pd.DataFrame:
    MIN_AFTER_GENDER_FILTER = 30
    GENDER_THRESHOLDS = [0.45, 0.35, 0.25]
    if work.empty or user_gender not in ["남성향", "여성향"]:
        return work  
    score_col = "Male_Score" if user_gender == "남성향" else "Female_Score"
    
    for thr in GENDER_THRESHOLDS:
        filtered = work[work[score_col] >= thr]
        if len(filtered) >= MIN_AFTER_GENDER_FILTER:
            return filtered.copy()
    return work

def recommend_perfumes(df, weakest, strongest, pref_tags, dislike_tags, brand_filter_mode, gender_filter="전체"):
    MIN_AFTER_BRAND_FILTER = 20
    DROP_DUP_KEYS = ["Brand", "Name"]
    if df.empty:
        return pd.DataFrame()
    work = df.copy()

    # 향수가 아닌 제품(로션, 워시 등) 필터링
    non_perfume_keywords = ["로션", "워시", "솝", "바디", "크림", "핸드", "lotion", "wash", "body", "cream", "hand", "soap", "헤어", "hair", "오일", "oil"]
    work = work[~work["Name"].apply(lambda n: any(kw in str(n).lower() for kw in non_perfume_keywords))]

    work = _apply_gender_filter(work, gender_filter)

    if brand_filter_mode == "유명 브랜드 위주":
        filtered = work[work["Brand"].apply(lambda b: any(f.lower() in str(b).lower() for f in FAMOUS_BRANDS))]
        if len(filtered) >= MIN_AFTER_BRAND_FILTER:
            work = filtered.copy()

    pref_keywords = tags_to_keywords(pref_tags)
    dislike_keywords = tags_to_keywords(dislike_tags)
    target = [1.0 if e == weakest else (0.1 if e == strongest else 0.5) for e in ELEMENTS]

    rows = []
    for _, row in work.iterrows():
        text = row.get("all_text", "")
        dislike_score = keyword_hit_score(text, dislike_keywords)
        pref_score = keyword_hit_score(text, pref_keywords)
        vec = [float(row.get(e, 0.0)) for e in ELEMENTS]

        denom = math.sqrt(sum(t*t for t in target)) * math.sqrt(sum(v*v for v in vec))
        sim = sum(t * v for t, v in zip(target, vec)) / denom if denom > 0 else 0.0
        brand_bonus = 0.15 if any(b.lower() in str(row.get("Brand", "")).lower() for b in FAMOUS_BRANDS) else 0.0

        final_score = (0.55 * sim) + (0.20 * float(row.get(weakest, 0.0))) + (0.18 * pref_score) - (0.20 * dislike_score) + brand_bonus
        if dislike_score >= 0.4:
            final_score -= 0.5

        r = row.to_dict()
        r.update({"score": float(final_score), f"{weakest}_fill": float(row.get(weakest, 0.0))})
        rows.append(r)

    out = (
        pd.DataFrame(rows)
        .sort_values("score", ascending=False)
        .drop_duplicates(subset=DROP_DUP_KEYS)
        .reset_index(drop=True)
    )
    return out

async def generate_comprehensive_reading_json(
    user_name: str, gender: str, saju_name: str, strongest: str, weakest: str, 
    top3_df: pd.DataFrame, know_time: bool, interests: List[str]
) -> dict:
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    gender_tone = get_gender_tone(gender)["style"]
    p = top3_df.head(3).copy()
    p1 = p.iloc[0] if len(p) > 0 else {}
    p2 = p.iloc[1] if len(p) > 1 else p1
    p3 = p.iloc[2] if len(p) > 2 else p1
    time_notice = "정오 기준(오차 가능)" if not know_time else "입력된 생시 기준"
    interests_str = ", ".join(interests) if interests else "전반적인 운"

    def notes_with_top_mid_base(row):
        top = safe_text(row.get("Top", ""))
        mid = safe_text(row.get("Middle", ""))
        base = safe_text(row.get("Base", ""))
        notes = safe_text(row.get("Notes", ""))
        if top or mid or base:
            return f"Top: {top} / Middle: {mid} / Base: {base}"
        return notes

    fallback = {
        "hero_title": f"{strong_ko} — '당신의 흐름은 분명합니다.'",
        "summary": f"당신의 사주는 {strong_ko} 기운이 매우 강하고, {weak_ko} 기운이 부족한 편입니다. 이러한 사주 구조는 {strong_ko} 기운의 장점인 추진력과 항동심을 가지게 하지만, {weak_ko} 기운이 상대적으로 약하기 때문에 유연성이나 세부적인 관심이 부족해질 수 있어요. 지금 선택한 향수는 {weak_ko} 기운을 채워주는 노트 일부로 구성되어, 당신의 {strong_ko}와 시너지를 낼 수 있게 선발됩니다. {interests_str}에 특히 집중해보면, 지금이 기운을 코디나는 중요한 시기일 수 있어요. 향수를 뿌려주시는 과정이 당신의 {weak_ko} 기운을 채워주는 하나의 의식적 습관이 될 수 있습니다.",
        "saju_analysis": {
            "overview": f"사주에서 {strong_ko} 기운이 우세한 편이라, 에너지와 추진력은 치치나 자칫치 않아요.",
            "advantages": f"{strong_ko} 기운이 나에게 주는 가장 큰 강점은 분명한 과결력이에요. 한번 집중하면 흔들림 없이 밀어다니는 힘이 있고, 임기응변하여 상황을 장악하는 능력도 있어요.",
            "disadvantages": f"{strong_ko} 기운이 과하면 지나치게 직접적이 되거나, 혼자 임스임스 왜 안 되는지 액한을 느끼는 순간이 올 수 있어요.",
            "weakness_signals": f"'{weak_ko}' 기운이 부족할 때는 나도 모르게 느슨해지거나, 세부사항에 무뚝해지는 신호가 올 수 있어요.",
            "balance_effect": f"'{weak_ko}' 기운을 담은 향수를 뿌리면, 존재감과 딩크스가 부드럽게 가락앉아요.",
            "best_environment": f"{strong_ko} 기운을 펼칠 수 있는 환경, 즉 목표와 기준이 명확한 콘텍스트에서 특히 강하다는 것을 유념하세요.",
            "perfume_effect": "추천된 향수를 뿌릴 때마다 부족한 기운을 속으로 물들이는 의식적 한관이 될 수 있어요."
        },
        "luck_analysis": {
            "primary": f"'{interests_str}' 방면에서 {weak_ko} 기운을 잊으면 더 편안하고 안정적인 흐름을 만들어 나갈 수 있어요.",
            "secondary": f"전반적으로 {strong_ko} 기운의 흐름이 강하니, 지금은 에너지 소모를 주의하게 환경에 수 마르세요."
        }
    }

    if not client:
        return fallback

    p1_notes = notes_with_top_mid_base(p1)
    p2_notes = notes_with_top_mid_base(p2)
    p3_notes = notes_with_top_mid_base(p3)

    p1_elements = ", ".join([f"{ELEMENTS_KO[e]}" for e in ELEMENTS if float(p1.get(e, 0.0)) > 0.15][:2])
    p2_elements = ", ".join([f"{ELEMENTS_KO[e]}" for e in ELEMENTS if float(p2.get(e, 0.0)) > 0.15][:2])
    p3_elements = ", ".join([f"{ELEMENTS_KO[e]}" for e in ELEMENTS if float(p3.get(e, 0.0)) > 0.15][:2])

    prompt = f"""
너는 명리학과 조향을 연결해 설명하는 전문가야.
결과는 **반드시 JSON만** 출력해. AI 말투(로봇처럼 딱딱한 말투) 지양하고 공감하는 친구 같은 톤으로 작성해.

[사용자 정보]
이름: {user_name}, 성별: {gender} (문체: {gender_tone})
사주: {saju_name}, 강한 기운: {strong_ko}, 보완 기운: {weak_ko}
조건: {time_notice}
관심 있는 운: {interests_str} (이 운들에 대해서만 아주 깊게, 집중적으로 풀이해줘)

[추천 향수 Top3 실제 오행 데이터]
1) {safe_text(p1.get("Brand",""))} - {safe_text(p1.get("Name",""))} / {p1_notes} / 주 기운: {p1_elements}
2) {safe_text(p2.get("Brand",""))} - {safe_text(p2.get("Name",""))} / {p2_notes} / 주 기운: {p2_elements}
3) {safe_text(p3.get("Brand",""))} - {safe_text(p3.get("Name",""))} / {p3_notes} / 주 기운: {p3_elements}

[출력 JSON 형식]
{{
  "hero_title": "짧고 강렬한 한 줄 정의 (15자 이내, 임팩트 있고 펀치감 있게. 예: '🔥 폭풍 속 불꽃', '💧 고요한 심해의 용', '🌳 부러지지 않는 대나무')",
  "summary": "핵심 요약: 사주 특성 + {interests_str} 측면에서 오행 불균형이 어떻게 작용하는지 + 부족한 기운을 향수로 어떻게 채워야 하는지 (반드시 4~5줄 이내로 자연스럽게 작성)",
  "saju_analysis": {{
    "overview": "★중요★ 사주 종합 평가. 유저의 사주를 기반으로 한 명리학적 성격, 두뇌/기질, 인간관계 특징 등을 핵심 위주로 디테일하게 풀이한 성격/인생 명세서 (반드시 5~6줄 이내로 작성할 것)",
    "advantages": "{strong_ko} 기운의 장점 (1~2문장)",
    "disadvantages": "과할 때 주의점 (1~2문장)",
    "weakness_signals": "{weak_ko} 부족 신호 (1~2문장)",
    "balance_effect": "'오행 보완' 후 실제 변화 (2~3문장)",
    "perfume_effect": "향수를 쓸 때 감정·신체·운에 미치는 효과 (반드시 2~3문장 이내)"
  }},
  "luck_analysis": [
    {{
      "luck_name": "선택한 각각의 운 이름 (예: 연애운)",
      "detail": "해당 운에 대해서만 집중적으로 핵심만 풀이. 향수와 오행을 연관지어서 어떻게 이 운이 좋아질 수 있는지 어드바이스 (무조건 2~3문장 이내, 디테일하게)"
    }}
  ],
  "perfumes": [
    {{
      "top": "첫번째 향수의 탑 노트 원본 향료 이름(예: 레몬, 베르가못)만 한국어로 번역. (절대 나무, 흙 같은 오행 기운을 적지 말 것)",
      "middle": "미들 노트 원본 향료 이름만 한국어로 번역. (절대 명리학적 오행이나 기운을 적지 말 것)",
      "base": "베이스 노트 원본 향료 이름만 한국어로 번역. (절대 목,화,토,금,수 같은 오행 기운이나 에너지를 적지 말고 머스크, 바닐라 등 실제 향료 이름만 적을 것)",
      "element_match_reason": "위 [추천 향수 Top3 실제 오행 데이터]에서 제공된 '주 기운'을 반드시 그대로 인용해서 설명할 것. 임의로 오행을 과장하거나 지어내지 말 것. 부족한 기운({weak_ko}) 보완 및 사주 밸런스와 왜 일치하는지를 3~4줄 분량 내외로 핵심만 명확하게 설명"
    }},
    {{ "top": "두번째 향수의 탑 ...", "middle": "...", "base": "...", "element_match_reason": "..." }},
    {{ "top": "세번째 향수의 탑 ...", "middle": "...", "base": "...", "element_match_reason": "..." }}
  ]
}}
""".strip()

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 명리학+조향 전문가야. 반드시 JSON만 출력해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=1200

        )
        raw = resp.choices[0].message.content if resp and resp.choices else ""
        raw = _strip_code_fences(raw)
        data = json.loads(raw)
        required = ["hero_title", "saju_analysis", "luck_analysis"]
        if all(k in data for k in required):
            return data
        return fallback
    except Exception:
        return fallback






# =========================================================
# API MODELS & ENDPOINTS
# =========================================================

class CompatRequest(BaseModel):
    user_name: str
    gender: str 
    year: int
    month: int
    day: int
    hour: Optional[int] = None
    minute: Optional[int] = None
    know_time: bool
    perf_brand: str
    perf_name: str

class CompatResponse(BaseModel):
    saju_data: dict
    perfume_details: dict
    compatibility_score: int
    compatibility_result: dict

class RecommendDirectRequest(BaseModel):
    user_name: str
    gender: str
    year: int
    month: int
    day: int
    hour: Optional[int] = None
    minute: Optional[int] = None
    know_time: bool
    pref_tags: List[str]
    dislike_tags: List[str]
    gender_filter: str
    brand_filter_mode: str
    interests: List[str]


image_cache = {}
def _sync_fetch_image(brand: str, name: str) -> Optional[str]:
    """Synchronous DuckDuckGo image fetch (run in thread pool)."""
    cache_key = f"{brand}_{name}"
    if cache_key in image_cache:
        return image_cache[cache_key]
    
    query = f"{brand} {name} perfume bottle"
    try:
        with DDGS(timeout=3) as ddgs:
            results = list(ddgs.images(query, max_results=1))
            if results and len(results) > 0:
                img_url = results[0].get("image")
                image_cache[cache_key] = img_url
                return img_url
    except Exception as e:
        print(f"Image fetch error for {query}: {e}")
    
    image_cache[cache_key] = None
    return None

async def get_perfume_image_url(brand: str, name: str, db_img_url: Optional[str] = None) -> Optional[str]:
    # 1. Use DB image URL if it's a valid picture link (not a fragrantica html page)
    if db_img_url and isinstance(db_img_url, str) and db_img_url.startswith("http"):
        if "fragrantica.com" not in db_img_url:
            return db_img_url

    # External search disabled to improve latency per user request.
    # We only rely on direct database URLs or cache.
    return None

@app.post("/api/compatibility", response_model=CompatResponse)
async def get_compatibility(req: CompatRequest):
    # Calculate user saju
    saju_res = get_real_saju_elements(req.year, req.month, req.day, req.hour if not req.know_time else None, req.minute if not req.know_time else None)
    if not saju_res:
        raise HTTPException(status_code=400, detail="Invalid date for Saju calculation")
    
    # Get perfume info
    db_row = find_perfume_in_db(req.perf_brand, req.perf_name)
    db_img_url = None
    if db_row:
        notes_text = str(db_row.get("Notes", ""))
        db_img_url = str(db_row.get("Image URL", ""))
        notes_source = "db"
    else:
        notes_text = await get_perfume_notes_via_ai(req.perf_brand, req.perf_name)
        notes_source = "ai"

    # Compute perf vector
    perf_vec = compute_perfume_element_vector(notes_text)
    
    # Check score
    score = compute_compatibility_score(saju_res["counts"], perf_vec, saju_res["weakest"], saju_res["strongest"])

    # AI generation
    compat_result = await generate_compatibility_result(
        user_name=req.user_name,
        gender=req.gender,
        saju_name=saju_res["saju_name"],
        strong=saju_res["strongest"],
        weak=saju_res["weakest"],
        perf_brand=req.perf_brand,
        perf_name=req.perf_name,
        notes_text=notes_text,
        score=score,
        perf_vec=perf_vec
    )

    return CompatResponse(
        saju_data=saju_res,
        perfume_details={
            "brand": req.perf_brand,
            "name": req.perf_name,
            "notes": notes_text,
            "source": notes_source,
            "element_vector": perf_vec
        },
        compatibility_score=score,
        compatibility_result=compat_result
    )

class RecommendRequest(BaseModel):
    user_name: str
    gender: str
    saju_data: dict
    pref_tags: List[str]
    dislike_tags: List[str]
    gender_filter: str
    brand_filter_mode: str
    interests: List[str] # ["금전운", "연애운"] 등

class RecommendResponse(BaseModel):
    top3: List[dict]
    reading_result: dict

@app.post("/api/recommend", response_model=RecommendResponse)
async def get_recommendations(req: RecommendRequest):
    weak = req.saju_data["weakest"]
    strong = req.saju_data["strongest"]
    saju_name = req.saju_data["saju_name"]
    know_time = "(시간 모름" not in saju_name # 간단한 파악

    rec_df = recommend_perfumes(
        df, weak, strong, req.pref_tags, req.dislike_tags, 
        req.brand_filter_mode, req.gender_filter
    )
    
    if rec_df.empty or len(rec_df) < 3:
        raise HTTPException(status_code=400, detail="Not enough perfumes found. Please ease the filters.")
         
    top3 = rec_df.head(3).copy()
    
    # Map dataframe outputs to simple dicts for the response
    top3_list = []
    for _, row in top3.iterrows():
        perf_dict = row.to_dict()
        perf_dict["badges"] = [f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]}" for e in ELEMENTS if float(perf_dict.get(e, 0.0)) > 0.15][:3]
        perf_dict["notes_ko"] = safe_text(perf_dict.get("Notes", ""))
        perf_dict["top_ko"] = safe_text(perf_dict.get("Top", ""))
        perf_dict["middle_ko"] = safe_text(perf_dict.get("Middle", ""))
        perf_dict["base_ko"] = safe_text(perf_dict.get("Base", ""))
        
        def notes_to_element_hints(notes_str):
            if not notes_str:
                return []
            hints = []
            for elem, kws in ELEMENT_KEYWORDS.items():
                matched = [kw for kw in kws if kw in notes_str.lower()]
                if matched:
                    hints.append(f"{ELEMENT_EMOJI[elem]} {ELEMENTS_KO[elem]} ({', '.join(matched[:2])})")
            return hints
        
        perf_dict["notes_element_hints"] = notes_to_element_hints(perf_dict["notes_ko"])
        top3_list.append(perf_dict)

    # === PARALLEL EXECUTION: images + AI reading simultaneously ===
    image_tasks = [
        get_perfume_image_url(
            p_dict.get("Brand", ""), 
            p_dict.get("Name", ""), 
            str(p_dict.get("Image URL", ""))
        )
        for p_dict in top3_list
    ]
    reading_task = generate_comprehensive_reading_json(
        user_name=req.user_name,
        gender=req.gender,
        saju_name=saju_name,
        strongest=strong,
        weakest=weak,
        top3_df=top3,
        know_time=know_time,
        interests=req.interests
    )

    # Run all 4 tasks (3 images + 1 AI) concurrently
    results = await asyncio.gather(*image_tasks, reading_task)
    
    # Unpack results: first 3 are images, last is the AI reading
    for i, p_dict in enumerate(top3_list):
        p_dict["image_url"] = results[i]
    reading = results[-1]

    ai_perfumes = reading.get("perfumes", [])
    for i, p_dict in enumerate(top3_list):
        if i < len(ai_perfumes):
            ai_data = ai_perfumes[i]
            p_dict["top_ko"] = ai_data.get("top", p_dict.get("top_ko"))
            p_dict["middle_ko"] = ai_data.get("middle", p_dict.get("middle_ko"))
            p_dict["base_ko"] = ai_data.get("base", p_dict.get("base_ko"))
            p_dict["element_match_reason"] = ai_data.get("element_match_reason", "")

    return RecommendResponse(
        top3=top3_list,
        reading_result=reading
    )

@app.post("/api/recommend_direct", response_model=RecommendResponse)
async def get_direct_recommendations(req: RecommendDirectRequest):
    # Calculate user saju
    saju_res = get_real_saju_elements(req.year, req.month, req.day, req.hour if not req.know_time else None, req.minute if not req.know_time else None)
    if not saju_res:
        raise HTTPException(status_code=400, detail="Invalid date for Saju calculation")
    
    weak = saju_res["weakest"]
    strong = saju_res["strongest"]
    saju_name = saju_res["saju_name"]
    know_time = req.know_time

    rec_df = recommend_perfumes(
        df, weak, strong, req.pref_tags, req.dislike_tags, 
        req.brand_filter_mode, req.gender_filter
    )
    
    if rec_df.empty or len(rec_df) < 3:
        raise HTTPException(status_code=400, detail="Not enough perfumes found. Please ease the filters.")
         
    top3 = rec_df.head(3).copy()
    
    # Map dataframe outputs to simple dicts for the response
    top3_list = []
    for _, row in top3.iterrows():
        perf_dict = row.to_dict()
        perf_dict["badges"] = [f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]}" for e in ELEMENTS if float(perf_dict.get(e, 0.0)) > 0.15][:3]
        perf_dict["notes_ko"] = safe_text(perf_dict.get("Notes", ""))
        perf_dict["top_ko"] = safe_text(perf_dict.get("Top", ""))
        perf_dict["middle_ko"] = safe_text(perf_dict.get("Middle", ""))
        perf_dict["base_ko"] = safe_text(perf_dict.get("Base", ""))
        
        def notes_to_element_hints(notes_str):
            if not notes_str:
                return []
            hints = []
            for elem, kws in ELEMENT_KEYWORDS.items():
                matched = [kw for kw in kws if kw in notes_str.lower()]
                if matched:
                    hints.append(f"{ELEMENT_EMOJI[elem]} {ELEMENTS_KO[elem]} ({', '.join(matched[:2])})")
            return hints
        
        perf_dict["notes_element_hints"] = notes_to_element_hints(perf_dict["notes_ko"])
        top3_list.append(perf_dict)

    # === PARALLEL EXECUTION: images + AI reading simultaneously ===
    image_tasks = [
        get_perfume_image_url(
            p_dict.get("Brand", ""), 
            p_dict.get("Name", ""), 
            str(p_dict.get("Image URL", ""))
        )
        for p_dict in top3_list
    ]
    reading_task = generate_comprehensive_reading_json(
        user_name=req.user_name,
        gender=req.gender,
        saju_name=saju_name,
        strongest=strong,
        weakest=weak,
        top3_df=top3,
        know_time=know_time,
        interests=req.interests
    )

    # Run all 4 tasks (3 images + 1 AI) concurrently
    results = await asyncio.gather(*image_tasks, reading_task)
    
    # Unpack results: first 3 are images, last is the AI reading
    for i, p_dict in enumerate(top3_list):
        p_dict["image_url"] = results[i]
    reading = results[-1]

    ai_perfumes = reading.get("perfumes", [])
    for i, p_dict in enumerate(top3_list):
        if i < len(ai_perfumes):
            ai_data = ai_perfumes[i]
            p_dict["top_ko"] = ai_data.get("top", p_dict.get("top_ko"))
            p_dict["base_ko"] = ai_data.get("base", p_dict.get("base_ko"))
            p_dict["element_match_reason"] = ai_data.get("element_match_reason", "")

    reading["saju_data"] = {
        "strongest": strong,
        "weakest": weak
    }

    return RecommendResponse(
        top3=top3_list,
        reading_result=reading
    )

