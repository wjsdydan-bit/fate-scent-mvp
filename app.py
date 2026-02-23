import streamlit as st
import pandas as pd
import datetime
import os
import math
import time
import urllib.parse
import uuid
from korean_lunar_calendar import KoreanLunarCalendar

# OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except Exception:
    OPENAI_SDK_AVAILABLE = False

# =========================================================
# 0) 기본 설정 및 모바일 앱 스타일
# =========================================================
st.set_page_config(page_title="향수 사쥬", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f5f7; }
    .block-container {
        max-width: 520px !important;
        background-color: #ffffff;
        padding: 1.6rem 1.2rem 1.8rem 1.2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-radius: 20px;
        margin-top: 14px;
        margin-bottom: 20px;
    }
    .stButton>button, .stFormSubmitButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        height: 3.2em;
        font-weight: bold;
        font-size: 15px;
    }
    h1 {
        text-align: center;
        color: #1e3c72;
        font-size: 28px !important;
        margin-bottom: 4px !important;
    }
    .subtitle {
        text-align: center;
        font-size: 13px;
        color: #666;
        margin-bottom: 22px;
        line-height: 1.5;
    }
    .card {
        background: #fff;
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #ddd;
        background: #fafafa;
    }
    .small-muted {
        font-size: 12px;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 1) 경로 / 상수 / OpenAI 설정
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(base_dir, "processed_perfumes_fixed_0223.csv")
LOG_PATH = os.path.join(base_dir, "recommendation_logs.csv")
CLICK_LOG_PATH = os.path.join(base_dir, "recommendation_click_logs.csv")

# ✅ 여기에 네 구글폼 링크 넣기
SURVEY_BASE_URL = "https://forms.gle/여기에_구글폼_링크"

ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
ELEMENTS_KO = {
    "Wood": "목(木/나무)",
    "Fire": "화(火/불)",
    "Earth": "토(土/흙)",
    "Metal": "금(金/쇠)",
    "Water": "수(水/물)"
}
ELEMENT_EMOJI = {
    "Wood": "🌳", "Fire": "🔥", "Earth": "🪨", "Metal": "⚙️", "Water": "💧"
}

# 태그 -> 키워드 맵
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

# 오행별 대표 키워드 (추천 이유 설명용)
ELEMENT_KEYWORDS = {
    "Wood": ["green", "herbal", "leafy", "tea", "vetiver", "pine", "grass"],
    "Fire": ["citrus", "spicy", "warm spicy", "pepper", "ginger", "cinnamon", "rose"],
    "Earth": ["woody", "musk", "amber", "powdery", "patchouli", "vanilla", "oud"],
    "Metal": ["aldehyde", "mineral", "mint", "cool", "soapy", "white floral"],
    "Water": ["aquatic", "marine", "sea", "watery", "ozonic", "salty"]
}

# 유명 브랜드 리스트
FAMOUS_BRANDS = [
    "Jo Malone", "Diptyque", "Byredo", "Aesop", "Chanel", "Dior", "Clean",
    "Forment", "Tamburins", "Nonfiction", "Le Labo", "Maison Francis Kurkdjian",
    "Tom Ford", "Hermes", "Creed", "Penhaligon", "Acqua di Parma"
]

# OpenAI 클라이언트
HAS_AI = False
client = None
if OPENAI_SDK_AVAILABLE:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        HAS_AI = True
    except Exception:
        HAS_AI = False

# =========================================================
# 2) 유틸 함수
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

def get_element_vector_badges(row):
    vals = {e: float(row.get(e, 0.0)) for e in ELEMENTS}
    top2 = sorted(vals.items(), key=lambda x: x[1], reverse=True)[:2]
    badges = []
    for e, v in top2:
        if v > 0:
            badges.append(f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]} {v:.2f}")
    return badges

def get_gender_tone(gender):
    """문구 톤 조절용"""
    if gender == "여성":
        return {
            "suffix": "님",
            "style": "부드럽고 감성적인 톤"
        }
    elif gender == "남성":
        return {
            "suffix": "님",
            "style": "깔끔하고 직관적인 톤"
        }
    else:
        return {
            "suffix": "님",
            "style": "중립적이고 친근한 톤"
        }

# =========================================================
# 3) 실제 만세력 기반 사주 계산 (시간 모름 지원)
# =========================================================
def get_real_saju_elements(year, month, day, hour=None, minute=None):
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)

    gapja_str = cal.getGapJaString()
    gapja = gapja_str.split()
    if len(gapja) < 3:
        return None, None, None, None, None

    year_char, month_char, day_char = gapja[0], gapja[1], gapja[2]

    saju_chars = [year_char[0], year_char[1], month_char[0], month_char[1], day_char[0], day_char[1]]
    saju_name = f"{year_char} {month_char} {day_char}"

    if hour is not None and minute is not None:
        stems = "갑을병정무기경신임계"
        branches = "자축인묘진사오미신유술해"
        total_mins = hour * 60 + minute

        # 23:30~01:29 = 자시 기준
        time_branch_idx = 0 if total_mins >= 1410 or total_mins < 90 else ((total_mins - 90) // 120 + 1) % 12
        time_branch = branches[time_branch_idx]

        day_stem_idx = stems.find(day_char[0])
        time_stem = stems[((day_stem_idx % 5) * 2 + time_branch_idx) % 10] if day_stem_idx != -1 else "갑"

        saju_chars.extend([time_stem, time_branch])
        saju_name += f" {time_stem}{time_branch}시"
    else:
        saju_name += " (시간 모름·정오 기준)"

    element_map = {
        '갑':'Wood','을':'Wood','병':'Fire','정':'Fire','무':'Earth','기':'Earth',
        '경':'Metal','신':'Metal','임':'Water','계':'Water',
        '인':'Wood','묘':'Wood','사':'Fire','오':'Fire',
        '진':'Earth','술':'Earth','축':'Earth','미':'Earth',
        '신':'Metal','유':'Metal','해':'Water','자':'Water',
        '申':'Metal'
    }

    counts = {e: 0 for e in ELEMENTS}
    for c in saju_chars:
        if c in element_map:
            counts[element_map[c]] += 1

    sorted_e = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_e[0][0]
    weakest = sorted_e[-1][0]

    return saju_name, counts, strongest, weakest, gapja_str

# =========================================================
# 4) AI 풀이 생성 (실패 시 fallback)
# =========================================================
def generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)

    p1 = top3_df.iloc[0]
    support_kws = extract_matching_notes(p1, weakest)
    support_kws_ko = ", ".join(support_kws) if support_kws else "핵심 노트"

    gender_line = ""
    if gender == "여성":
        gender_line = "감성적인 표현과 무드 연출에 특히 잘 반응하는 타입일 가능성이 있어요."
    elif gender == "남성":
        gender_line = "첫인상과 분위기를 만드는 향의 역할이 더 또렷하게 체감될 수 있어요."
    else:
        gender_line = "향을 통한 이미지 메이킹과 컨디션 조절에 잘 맞는 방식이에요."

    time_notice = ""
    if know_time:
        time_notice = "\n\n> ⏰ **태어난 시간을 모른다고 선택하셔서, 정오(12:30) 기준으로 풀이했어요.** 실제 시간에 따라 일부 해석이 달라질 수 있습니다."

    txt = f"""
### ✨ {user_name}님의 고유한 기운

**{saju_name}** 기준으로 보면, 현재 가장 강한 기운은 **{strong_ko}**, 보완이 필요한 기운은 **{weak_ko}**입니다.

### 📜 사주 및 오행 분석
강한 기운이 분명한 타입이라 개성과 분위기가 뚜렷하게 드러나는 편이에요.  
반대로 부족한 기운이 채워지면 일상 컨디션, 감정 균형, 대인관계에서 더 부드러운 흐름을 만들 수 있습니다.  
{gender_line}

### 🔑 당신에게 꼭 필요한 기운
지금은 **{weak_ko}** 기운을 향으로 보완하는 것이 핵심이에요.  
향수는 운세를 바꾼다기보다, **내가 가진 분위기를 더 잘 끌어내고 부족한 인상을 보완하는 도구**로 보면 가장 잘 맞습니다.

> 이 부족한 **{weak_ko}** 기운은, 아래 향수들의 노트를 통해 일상에서 자연스럽게 보완할 수 있습니다.
{time_notice}

---

### 🧴 맞춤 향수 처방전 (Top 3)

#### 🥇 1위. {p1['Brand']} - {p1['Name']}
- **추천 포인트:** 부족한 **{weak_ko}** 기운과 연결되는 노트가 잘 살아 있어요.
- **보완 노트 힌트:** {support_kws_ko}
- **향기 노트:** {safe_text(p1.get('Notes', '정보 없음'))}

#### 🥈 2위. {top3_df.iloc[1]['Brand']} - {top3_df.iloc[1]['Name']}
- **추천 포인트:** 밸런스 보완 + 데일리 사용감이 좋은 타입이에요.
- **향기 노트:** {safe_text(top3_df.iloc[1].get('Notes', '정보 없음'))}

#### 🥉 3위. {top3_df.iloc[2]['Brand']} - {top3_df.iloc[2]['Name']}
- **추천 포인트:** 개성을 살리면서도 분위기 연출에 좋은 선택이에요.
- **향기 노트:** {safe_text(top3_df.iloc[2].get('Notes', '정보 없음'))}
"""
    return txt

def generate_comprehensive_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    if (not HAS_AI) or client is None:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)

    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)

    p1, p2, p3 = top3_df.iloc[0], top3_df.iloc[1], top3_df.iloc[2]
    p1_hint = ", ".join(extract_matching_notes(p1, weakest)) or "관련 노트"
    p2_hint = ", ".join(extract_matching_notes(p2, weakest)) or "관련 노트"
    p3_hint = ", ".join(extract_matching_notes(p3, weakest)) or "관련 노트"

    time_notice_prompt = (
        "사용자는 태어난 시간을 모름으로 선택했고, 정오 기준 추정 풀이임. 반드시 안내 문구를 넣어라."
        if know_time else
        "사용자는 태어난 시간을 입력함."
    )

    gender_tone = get_gender_tone(gender)["style"]

    prompt = f"""
당신은 트렌디한 명리학자이자 조향사입니다.
고객 이름: {user_name}
성별: {gender}
고객 사주: [{saju_name}]
가장 강한 기운: [{strong_ko}]
보완이 필요한 기운: [{weak_ko}]
문체 가이드: {gender_tone}
추가 조건: {time_notice_prompt}

추천 향수 Top 3:
1위: {p1['Brand']} - {p1['Name']} (노트: {safe_text(p1.get('Notes',''))}, 보완 힌트: {p1_hint})
2위: {p2['Brand']} - {p2['Name']} (노트: {safe_text(p2.get('Notes',''))}, 보완 힌트: {p2_hint})
3위: {p3['Brand']} - {p3['Name']} (노트: {safe_text(p3.get('Notes',''))}, 보완 힌트: {p3_hint})

규칙:
- 과장/단정 금지 (예: 운명 바뀜, 100%)
- 향을 통한 분위기/밸런스 보완 관점 유지
- 각 향수마다 "부족한 오행을 어떤 노트가 채우는지" 반드시 설명
- 한국어로 자연스럽고 읽기 좋게 작성

형식:
### ✨ [당신의 고유한 기운]
(한 줄 비유)

### 📜 사주 및 오행 분석
(3~4문장)

### 🔑 당신에게 꼭 필요한 기운
(왜 {weak_ko} 기운이 필요한지 + 보완되면 어떤 점이 좋아지는지)
> "이 부족한 {weak_ko} 기운은, 아래 향수들의 노트를 통해 일상에서 자연스럽게 보완할 수 있습니다."
(시간 모름이면 정오 기준 안내 문구 추가)

---

### 🧴 맞춤 향수 처방전

#### 🥇 1위. {p1['Brand']} - {p1['Name']}
- **한줄 설명:** ...
- **향기 노트:** ...
- **오행 보완 포인트:** ...
- **추천 이유:** ...

#### 🥈 2위. {p2['Brand']} - {p2['Name']}
- **한줄 설명:** ...
- **향기 노트:** ...
- **오행 보완 포인트:** ...
- **추천 이유:** ...

#### 🥉 3위. {p3['Brand']} - {p3['Name']}
- **한줄 설명:** ...
- **향기 노트:** ...
- **오행 보완 포인트:** ...
- **추천 이유:** ...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 향수와 명리학을 연결해 설명하는 친절한 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        if not content:
            return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
        return content
    except Exception:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)

# =========================================================
# 5) 로그 저장 (추천 로그 / 클릭 로그)
# =========================================================
def save_recommendation_log_rows(session_id, user_name, gender, birth_date, know_time, saju_name, strongest, weakest, brand_filter, top3_df):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for rank_idx, (_, row) in enumerate(top3_df.iterrows(), start=1):
        rows.append({
            "timestamp": now_str,
            "session_id": session_id,
            "user_name": user_name,
            "gender": gender,
            "birth_date": str(birth_date),
            "know_time": 0 if know_time else 1,  # check box가 "시간 모름"이므로 반대로 저장
            "saju_name": saju_name,
            "strongest_element": strongest,
            "weakest_element": weakest,
            "brand_filter": brand_filter,
            "rank": rank_idx,
            "perfume_name": safe_text(row.get("Name", "")),
            "brand": safe_text(row.get("Brand", "")),
            "notes": safe_text(row.get("Notes", "")),
            "rec_score": float(row.get("score", 0.0)),
            "sim_score": float(row.get("sim_score", 0.0)),
            "pref_score": float(row.get("pref_score", 0.0)),
            "dislike_score": float(row.get("dislike_score", 0.0)),
            "weak_fill_score": float(row.get(f"{weakest}_fill", row.get(weakest, 0.0))),
        })

    df_log = pd.DataFrame(rows)
    if not os.path.exists(LOG_PATH):
        df_log.to_csv(LOG_PATH, index=False, encoding="utf-8-sig")
    else:
        df_log.to_csv(LOG_PATH, mode="a", header=False, index=False, encoding="utf-8-sig")

def save_click_log(session_id, user_name, rank, brand, perfume_name, click_type, url):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = pd.DataFrame([{
        "timestamp": now_str,
        "session_id": session_id,
        "user_name": user_name,
        "rank": rank,
        "brand": brand,
        "perfume_name": perfume_name,
        "click_type": click_type,  # naver_search / survey
        "url": url
    }])

    if not os.path.exists(CLICK_LOG_PATH):
        row.to_csv(CLICK_LOG_PATH, index=False, encoding="utf-8-sig")
    else:
        row.to_csv(CLICK_LOG_PATH, mode="a", header=False, index=False, encoding="utf-8-sig")

# =========================================================
# 6) 데이터 로드
# =========================================================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    df = None
    for enc in ["utf-8-sig", "utf-8", "cp949"]:
        try:
            df = pd.read_csv(DATA_PATH, encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        return pd.DataFrame()

    for c in ["Name", "Brand", "Notes", "Description", "matched_keywords"]:
        if c not in df.columns:
            df[c] = ""

    for c in ["Name", "Brand", "Notes", "Description", "matched_keywords"]:
        df[c] = df[c].fillna("").astype(str)

    for e in ELEMENTS:
        if e not in df.columns:
            df[e] = 0.0
        df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)

    df["all_text"] = (
        df["Name"].astype(str) + " " +
        df["Brand"].astype(str) + " " +
        df["Notes"].astype(str) + " " +
        df["Description"].astype(str) + " " +
        df["matched_keywords"].astype(str)
    ).str.lower()

    df["element_sum"] = df[ELEMENTS].sum(axis=1)
    df = df[df["element_sum"] > 0].copy()

    # 샘플/세트 제외
    exclude_words = ["sample", "discovery", "set", "pack", "travel spray", "gift", "miniature"]
    mask = ~df["Name"].str.lower().apply(lambda x: any(w in x for w in exclude_words))
    df = df[mask].copy()

    return df.reset_index(drop=True)

df = load_data()

# =========================================================
# 7) 추천 엔진
# =========================================================
def recommend_perfumes(df, weakest, strongest, pref_tags, dislike_tags, brand_filter_mode):
    if df.empty:
        return pd.DataFrame()

    work = df.copy()

    # 브랜드 필터
    if brand_filter_mode == "유명 브랜드 위주":
        work = work[work["Brand"].astype(str).apply(
            lambda b: any(f.lower() in b.lower() for f in FAMOUS_BRANDS)
        )].copy()

        # 필터 결과가 너무 적으면 전체로 fallback
        if len(work) < 20:
            work = df.copy()

    pref_keywords = tags_to_keywords(pref_tags)
    dislike_keywords = tags_to_keywords(dislike_tags)

    target = []
    for e in ELEMENTS:
        if e == weakest:
            target.append(1.0)
        elif e == strongest:
            target.append(0.1)
        else:
            target.append(0.5)

    rows = []
    for _, row in work.iterrows():
        text = row["all_text"]
        dislike_score = keyword_hit_score(text, dislike_keywords)
        pref_score = keyword_hit_score(text, pref_keywords)

        vec = [float(row[e]) for e in ELEMENTS]
        dot = sum(t * v for t, v in zip(target, vec))
        denom = math.sqrt(sum(t*t for t in target)) * math.sqrt(sum(v*v for v in vec))
        sim = dot / denom if denom > 0 else 0.0

        brand = safe_text(row.get("Brand", ""))
        brand_bonus = 0.15 if any(b.lower() in brand.lower() for b in FAMOUS_BRANDS) else 0.0

        weak_fill = float(row.get(weakest, 0.0))

        final_score = (
            (0.55 * sim) +
            (0.20 * weak_fill) +
            (0.18 * pref_score) -
            (0.20 * dislike_score) +
            brand_bonus
        )

        if dislike_score >= 0.4:
            final_score -= 0.5

        row_dict = row.to_dict()
        row_dict.update({
            "score": final_score,
            "sim_score": sim,
            "pref_score": pref_score,
            "dislike_score": dislike_score,
            f"{weakest}_fill": weak_fill
        })
        rows.append(row_dict)

    out = pd.DataFrame(rows)
    out = out.sort_values("score", ascending=False).drop_duplicates(subset=["Name"]).reset_index(drop=True)
    return out

# =========================================================
# 8) UI
# =========================================================
st.markdown("<h1>🔮 향수 사쥬</h1>", unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">실제 만세력 기반으로 사주 오행을 분석하고<br>부족한 기운을 보완해줄 향수를 추천해드려요.</div>',
    unsafe_allow_html=True
)

if df.empty:
    st.error("향수 데이터 파일을 불러오지 못했어요. `processed_perfumes_fixed_0223.csv` 파일을 앱 폴더에 넣어주세요.")
    st.stop()

with st.form("saju_form"):
    user_name = st.text_input("이름 (또는 닉네임)", placeholder="예: 홍길동")

    gender = st.selectbox("성별", ["선택 안 함", "여성", "남성"], index=0)

    birth_date = st.date_input(
        "생년월일 (양력)",
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(1995, 1, 1)
    )

    st.markdown("<p style='font-size:14px; margin-bottom:5px; color:#333;'>태어난 시간</p>", unsafe_allow_html=True)
    know_time = st.checkbox("태어난 시간을 모릅니다")

    if know_time:
        b_hour, b_min = None, None
        st.caption("시간을 모르면 정오(12:30) 기준으로 계산하며, 실제 시간에 따라 일부 해석이 달라질 수 있어요.")
    else:
        time_slots = [f"{h:02d}~{(h+1)%24:02d}" for h in range(24)]
        selected_slot = st.selectbox("시간대 선택", time_slots, index=12)
        b_hour = int(selected_slot.split("~")[0])
        b_min = 30

    st.markdown("<hr style='margin:1.2rem 0; border:none; border-top:1px dashed #ddd;'>", unsafe_allow_html=True)

    tag_options = list(TAG_TO_KEYWORDS.keys())
    pref_tags = st.multiselect("끌리는 향 (복수 선택)", tag_options)

    dislike_candidates = [t for t in tag_options if t not in pref_tags]
    dislike_tags = st.multiselect("피하고 싶은 향", dislike_candidates)

    brand_filter_mode = st.radio(
        "브랜드 범위",
        ["전체 브랜드", "유명 브랜드 위주"],
        horizontal=True
    )

    submit = st.form_submit_button("향수 처방 받기")

# =========================================================
# 9) 추천 실행
# =========================================================
if submit:
    if not user_name.strip():
        st.warning("이름(또는 닉네임)을 입력해주세요.")
        st.stop()

    # session_id 생성/유지
    session_id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    st.session_state["session_id"] = session_id
    st.session_state["user_name"] = user_name.strip()

    # 로딩
    loading_placeholder = st.empty()
    messages = ["🔮 만세력 스캐닝 중...", "🌿 오행 에너지 분석 중...", "✨ 맞춤 향수 배합 중..."]
    for msg in messages:
        loading_placeholder.markdown(
            f"<h3 style='text-align:center; color:#2a5298; margin: 28px 0;'>{msg}</h3>",
            unsafe_allow_html=True
        )
        time.sleep(0.8)
    loading_placeholder.empty()

    # 시간 모름이면 정오 기준
    calc_hour = 12 if know_time else b_hour
    calc_min = 30 if know_time else b_min

    result = get_real_saju_elements(
        birth_date.year, birth_date.month, birth_date.day, calc_hour, calc_min
    )
    if result[0] is None:
        st.error("사주 계산에 실패했어요. 날짜를 다시 확인해주세요.")
        st.stop()

    saju_name, e_counts, strong, weak, gapja_str = result

    rec_df = recommend_perfumes(df.copy(), weak, strong, pref_tags, dislike_tags, brand_filter_mode)
    if rec_df.empty or len(rec_df) < 3:
        st.error("추천 가능한 향수가 부족해요. 데이터 파일 또는 필터 설정을 확인해주세요.")
        st.stop()

    top3 = rec_df.head(3).copy()

    # 세션 결과 저장 (화면 재렌더링 대응)
    st.session_state["top3"] = top3
    st.session_state["saju_name"] = saju_name
    st.session_state["e_counts"] = e_counts
    st.session_state["strong"] = strong
    st.session_state["weak"] = weak
    st.session_state["gender"] = gender
    st.session_state["know_time"] = know_time
    st.session_state["brand_filter_mode"] = brand_filter_mode
    st.session_state["birth_date"] = birth_date

    # 추천 로그 저장
    try:
        save_recommendation_log_rows(
            session_id=session_id,
            user_name=user_name.strip(),
            gender=gender,
            birth_date=birth_date,
            know_time=know_time,
            saju_name=saju_name,
            strongest=strong,
            weakest=weak,
            brand_filter=brand_filter_mode,
            top3_df=top3
        )
    except Exception:
        pass

# =========================================================
# 10) 결과 렌더링 (버튼 클릭 후 rerun 대비)
# =========================================================
if "top3" in st.session_state:
    top3 = st.session_state["top3"]
    saju_name = st.session_state["saju_name"]
    e_counts = st.session_state["e_counts"]
    strong = st.session_state["strong"]
    weak = st.session_state["weak"]
    gender = st.session_state["gender"]
    know_time = st.session_state["know_time"]
    session_id = st.session_state["session_id"]
    user_name = st.session_state["user_name"]

    st.markdown(f"### {user_name}님의 맞춤 향수 처방 결과")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"<div class='card'><b>가장 강한 기운</b><br>{ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}</div>",
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            f"<div class='card'><b>보완이 필요한 기운</b><br>{ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}</div>",
            unsafe_allow_html=True
        )

    if know_time:
        st.info("⏰ 태어난 시간을 모른다고 선택하셔서 **정오(12:30) 기준**으로 풀이했어요. 실제 태어난 시간에 따라 일부 해석은 달라질 수 있어요.")

    st.markdown("#### 오행 분포")
    e_df = pd.DataFrame({
        "오행": [f"{ELEMENT_EMOJI[e]} {e}" for e in ELEMENTS],
        "개수": [e_counts[e] for e in ELEMENTS]
    })
    st.bar_chart(e_df.set_index("오행"))

    with st.spinner("AI가 사주 풀이와 향수 처방전을 작성 중입니다..."):
        reading_result = generate_comprehensive_reading(
            user_name=user_name,
            gender=gender,
            saju_name=saju_name,
            strongest=strong,
            weakest=weak,
            top3_df=top3,
            know_time=know_time
        )
    st.markdown(reading_result)

    st.markdown("---")
    st.markdown("### 🧴 추천 향수 Top 3 (카드형 요약)")

    medal_map = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, (_, row) in enumerate(top3.iterrows()):
        name = safe_text(row.get("Name", ""))
        brand = safe_text(row.get("Brand", ""))
        notes = safe_text(row.get("Notes", ""))
        desc = safe_text(row.get("Description", ""))

        support_notes = extract_matching_notes(row, weak)
        support_notes_text = ", ".join(support_notes) if support_notes else "관련 노트 분석됨"

        badges = get_element_vector_badges(row)
        naver_query = urllib.parse.quote(f"{brand} {name} 향수")
        naver_url = f"https://search.shopping.naver.com/search/all?query={naver_query}"

        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.markdown(f"**{medal_map.get(i,'🔹')} {brand} - {name}**")
            st.caption(f"추천 점수: {float(row.get('score', 0.0)):.3f}")

            badge_html = "".join([f"<span class='badge'>{b}</span>" for b in badges])
            st.markdown(badge_html, unsafe_allow_html=True)

            weak_fill_value = float(row.get(f"{weak}_fill", row.get(weak, 0.0)))
            st.write(f"**부족 오행 보완력 ({ELEMENTS_KO[weak]})**: `{weak_fill_value:.2f}`")
            st.write(f"**보완 노트 포인트**: {support_notes_text}")

            if notes:
                st.write(f"**주요 노트**: {notes[:160]}{'...' if len(notes) > 160 else ''}")
            if desc:
                st.write(f"**설명**: {desc[:160]}{'...' if len(desc) > 160 else ''}")

            # 클릭 로그 버튼 + 링크 열기
            btn_key = f"naver_btn_{session_id}_{i}"
            if st.button("네이버 쇼핑에서 검색하기", key=btn_key, use_container_width=True):
                try:
                    save_click_log(
                        session_id=session_id,
                        user_name=user_name,
                        rank=i+1,
                        brand=brand,
                        perfume_name=name,
                        click_type="naver_search",
                        url=naver_url
                    )
                except Exception:
                    pass
                st.link_button("네이버 쇼핑 열기", naver_url, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # 설문 링크 (session_id 포함)
    st.markdown("---")
    st.markdown("### 🙋 추천 결과가 어떠셨나요?")
    st.write("1분 설문에 참여해주시면 추천 정확도를 더 좋게 개선할 수 있어요.")

    # session_id 파라미터 붙이기
    # (구글폼이 직접 받지 못해도, 최소한 URL에 남겨두면 추적에 도움)
    survey_url_with_session = SURVEY_BASE_URL
    if SURVEY_BASE_URL.startswith("http"):
        sep = "&" if "?" in SURVEY_BASE_URL else "?"
        survey_url_with_session = f"{SURVEY_BASE_URL}{sep}session_id={urllib.parse.quote(session_id)}"

    st.caption(f"분석용 세션 ID: {session_id}")

    if st.button("1분 설문 참여하기", key=f"survey_btn_{session_id}", use_container_width=True):
        try:
            save_click_log(
                session_id=session_id,
                user_name=user_name,
                rank=0,
                brand="",
                perfume_name="",
                click_type="survey",
                url=survey_url_with_session
            )
        except Exception:
            pass
        st.link_button("설문 열기", survey_url_with_session, use_container_width=True)

# =========================================================
# 11) 관리자용 로그 확인
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🔐 [관리자용] 로그 데이터 확인"):
    st.write("추천 로그와 클릭 로그가 서버에 누적 저장됩니다.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**추천 로그 (recommendation_logs.csv)**")
        if os.path.exists(LOG_PATH):
            try:
                log_preview = pd.read_csv(LOG_PATH, encoding="utf-8-sig").tail(20)
                st.dataframe(log_preview, use_container_width=True)
            except Exception:
                st.info("미리보기 로딩 실패 (다운로드는 가능)")
            with open(LOG_PATH, "rb") as f:
                st.download_button(
                    "📥 추천 로그 다운로드",
                    f,
                    file_name="recommendation_logs.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("아직 추천 로그가 없습니다.")

    with col2:
        st.markdown("**클릭 로그 (recommendation_click_logs.csv)**")
        if os.path.exists(CLICK_LOG_PATH):
            try:
                click_preview = pd.read_csv(CLICK_LOG_PATH, encoding="utf-8-sig").tail(20)
                st.dataframe(click_preview, use_container_width=True)
            except Exception:
                st.info("미리보기 로딩 실패 (다운로드는 가능)")
            with open(CLICK_LOG_PATH, "rb") as f:
                st.download_button(
                    "📥 클릭 로그 다운로드",
                    f,
                    file_name="recommendation_click_logs.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("아직 클릭 로그가 없습니다.")
