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
    "Wood": "목(木/나무)", "Fire": "화(火/불)", "Earth": "토(土/흙)",
    "Metal": "금(金/쇠)", "Water": "수(水/물)"
}
ELEMENT_EMOJI = {"Wood": "🌳", "Fire": "🔥", "Earth": "🪨", "Metal": "⚙️", "Water": "💧"}

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
    "Wood": ["green", "herbal", "leafy", "tea", "vetiver", "pine", "grass"],
    "Fire": ["citrus", "spicy", "warm spicy", "pepper", "ginger", "cinnamon", "rose"],
    "Earth": ["woody", "musk", "amber", "powdery", "patchouli", "vanilla", "oud"],
    "Metal": ["aldehyde", "mineral", "mint", "cool", "soapy", "white floral"],
    "Water": ["aquatic", "marine", "sea", "watery", "ozonic", "salty"]
}

FAMOUS_BRANDS = [
    "Jo Malone", "Diptyque", "Byredo", "Aesop", "Chanel", "Dior", "Clean",
    "Forment", "Tamburins", "Nonfiction", "Le Labo", "Maison Francis Kurkdjian",
    "Tom Ford", "Hermes", "Creed", "Penhaligon", "Acqua di Parma"
]

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
    if pd.isna(x): return ""
    return str(x).strip()

def tags_to_keywords(tags):
    kws = []
    for t in tags: kws.extend(TAG_TO_KEYWORDS.get(t, []))
    return sorted(set([k.lower().strip() for k in kws if k]))

def keyword_hit_score(text, keywords):
    if not keywords: return 0.0
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
    return [f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]} {v:.2f}" for e, v in top2 if v > 0]

def get_gender_tone(gender):
    if gender == "여성": return {"suffix": "님", "style": "부드럽고 감성적인 톤"}
    elif gender == "남성": return {"suffix": "님", "style": "깔끔하고 직관적인 톤"}
    else: return {"suffix": "님", "style": "중립적이고 친근한 톤"}

# =========================================================
# 3) 실제 만세력 기반 사주 계산
# =========================================================
def get_real_saju_elements(year, month, day, hour=None, minute=None):
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)

    gapja_str = cal.getGapJaString()
    gapja = gapja_str.split()
    if len(gapja) < 3: return None, None, None, None, None

    year_char, month_char, day_char = gapja[0], gapja[1], gapja[2]
    saju_chars = [year_char[0], year_char[1], month_char[0], month_char[1], day_char[0], day_char[1]]
    saju_name = f"{year_char} {month_char} {day_char}"

    if hour is not None and minute is not None:
        stems, branches = "갑을병정무기경신임계", "자축인묘진사오미신유술해"
        total_mins = hour * 60 + minute
        time_branch_idx = 0 if total_mins >= 1410 or total_mins < 90 else ((total_mins - 90) // 120 + 1) % 12
        time_branch = branches[time_branch_idx]
        day_stem_idx = stems.find(day_char[0])
        time_stem = stems[((day_stem_idx % 5) * 2 + time_branch_idx) % 10] if day_stem_idx != -1 else "갑"
        saju_chars.extend([time_stem, time_branch])
        saju_name += f" {time_stem}{time_branch}시"
    else:
        saju_name += " (시간 모름·6글자 기준)"

    element_map = {
        '갑':'Wood','을':'Wood','병':'Fire','정':'Fire','무':'Earth','기':'Earth',
        '경':'Metal','신':'Metal','임':'Water','계':'Water',
        '인':'Wood','묘':'Wood','사':'Fire','오':'Fire','진':'Earth','술':'Earth',
        '축':'Earth','미':'Earth','신':'Metal','유':'Metal','해':'Water','자':'Water','申':'Metal'
    }

    counts = {e: 0 for e in ELEMENTS}
    for c in saju_chars:
        if c in element_map: counts[element_map[c]] += 1

    sorted_e = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return saju_name, counts, sorted_e[0][0], sorted_e[-1][0], gapja_str

# =========================================================
# 4) AI 풀이 생성 (Fallback 포함)
# =========================================================
def generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    p1 = top3_df.iloc[0]
    
    time_notice = "\n\n> ⏰ **태어난 시간을 모른다고 선택하셔서, 연월일 6글자 기준으로 풀이했어요.**" if know_time else ""

    return f"""
### ✨ {user_name}님의 고유한 기운
**{saju_name}** 기준으로 보면, 현재 가장 강한 기운은 **{strong_ko}**, 보완이 필요한 기운은 **{weak_ko}**입니다.

### 📜 사주 및 오행 분석
강한 기운이 분명한 타입이라 개성과 분위기가 뚜렷하게 드러나는 편이에요. 반대로 부족한 기운이 채워지면 일상 컨디션, 감정 균형, 대인관계에서 더 부드러운 흐름을 만들 수 있습니다.

### 🔑 당신에게 꼭 필요한 기운
지금은 **{weak_ko}** 기운을 향으로 보완하는 것이 핵심이에요.
> 이 부족한 **{weak_ko}** 기운은, 아래 향수들의 노트를 통해 일상에서 자연스럽게 보완할 수 있습니다.{time_notice}

---
### 🧴 맞춤 향수 처방전 (Top 3)
#### 🥇 1위. {p1['Brand']} - {p1['Name']}
- **추천 포인트:** 부족한 **{weak_ko}** 기운과 연결되는 노트가 잘 살아 있어요.
- **향기 노트:** {safe_text(p1.get('Notes', '정보 없음'))}
"""

def generate_comprehensive_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    if not HAS_AI or client is None:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)

    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    p1, p2, p3 = top3_df.iloc[0], top3_df.iloc[1], top3_df.iloc[2]
    gender_tone = get_gender_tone(gender)["style"]
    time_notice = "사용자는 태어난 시간을 모름으로 선택해 6글자(삼주)로 분석함. 반드시 안내 문구를 짧게 넣어라." if know_time else "사용자는 태어난 시간을 정확히 입력함."

    prompt = f"""
당신은 트렌디한 명리학자이자 조향사입니다.
고객 이름: {user_name} (성별: {gender}, 문체: {gender_tone})
고객 사주: [{saju_name}]
가장 강한 기운: [{strong_ko}] / 보완이 필요한 기운: [{weak_ko}]
추가 조건: {time_notice}

추천 향수 Top 3:
1위: {p1['Brand']} - {p1['Name']} (노트: {safe_text(p1.get('Notes',''))})
2위: {p2['Brand']} - {p2['Name']} (노트: {safe_text(p2.get('Notes',''))})
3위: {p3['Brand']} - {p3['Name']} (노트: {safe_text(p3.get('Notes',''))})

규칙:
- 한국어로 자연스럽고 다정하게 작성
- 각 향수마다 "이 향수의 노트가 동양학적으로 어떻게 {weak_ko} 기운과 상통하는지", "어떤 기대효과가 있는지" 상세히 작성.

형식 (마크다운 완벽 준수):
### ✨ [당신의 고유한 기운]
(사주를 비유한 감성적인 한 줄)

### 📜 사주 및 오행 분석
(사주 풀이 3~4문장)

### 🔑 당신에게 꼭 필요한 기운
(왜 {weak_ko} 기운이 필요한지, 보완되면 어떤 점이 좋아지는지)
> "이 부족한 {weak_ko} 기운은, 아래 향수들을 통해 일상에서 완벽하게 보완할 수 있습니다."

---
### 🧴 맞춤 향수 처방전

#### 🥇 1위. {p1['Brand']} - {p1['Name']}
- **한줄 설명:** (향수 한줄 요약)
- **향기 노트:** {safe_text(p1.get('Notes',''))}
- **오행의 기운:** (향과 오행의 연결)
- **기대 효과:** (운세 상승 효과)

#### 🥈 2위. {p2['Brand']} - {p2['Name']}
- **한줄 설명:** ...
- **향기 노트:** {safe_text(p2.get('Notes',''))}
- **오행의 기운:** ...
- **기대 효과:** ...

#### 🥉 3위. {p3['Brand']} - {p3['Name']}
- **한줄 설명:** ...
- **향기 노트:** {safe_text(p3.get('Notes',''))}
- **오행의 기운:** ...
- **기대 효과:** ...
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
        return response.choices[0].message.content or generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
    except Exception:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)

# =========================================================
# 5) 로그 저장
# =========================================================
def save_recommendation_log(session_id, user_name, gender, birth_date, know_time, saju_name, strongest, weakest, top3_df):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for rank_idx, (_, row) in enumerate(top3_df.iterrows(), start=1):
        rows.append({
            "timestamp": now_str, "session_id": session_id, "user_name": user_name, "gender": gender,
            "birth_date": str(birth_date), "know_time": 0 if know_time else 1, "saju_name": saju_name,
            "strongest_element": strongest, "weakest_element": weakest, "rank": rank_idx,
            "perfume_name": safe_text(row.get("Name", "")), "brand": safe_text(row.get("Brand", "")),
            "rec_score": float(row.get("score", 0.0))
        })
    df_log = pd.DataFrame(rows)
    df_log.to_csv(LOG_PATH, mode="a" if os.path.exists(LOG_PATH) else "w", header=not os.path.exists(LOG_PATH), index=False, encoding="utf-8-sig")

# =========================================================
# 6) 데이터 로드 및 추천 엔진
# =========================================================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH): return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)
    for c in ["Name", "Brand", "Notes", "Description", "matched_keywords"]:
        if c not in df.columns: df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    for e in ELEMENTS:
        if e not in df.columns: df[e] = 0.0
        df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)
    df["all_text"] = (df["Name"] + " " + df["Brand"] + " " + df["Notes"] + " " + df["matched_keywords"]).str.lower()
    df["element_sum"] = df[ELEMENTS].sum(axis=1)
    df = df[df["element_sum"] > 0].copy()
    mask = ~df["Name"].str.lower().apply(lambda x: any(w in x for w in ["sample", "discovery", "set", "gift", "miniature"]))
    return df[mask].reset_index(drop=True)

df = load_data()

def recommend_perfumes(df, weakest, strongest, pref_tags, dislike_tags, brand_filter_mode):
    if df.empty: return pd.DataFrame()
    work = df.copy()
    if brand_filter_mode == "유명 브랜드 위주":
        work = work[work["Brand"].apply(lambda b: any(f.lower() in str(b).lower() for f in FAMOUS_BRANDS))].copy()
        if len(work) < 20: work = df.copy()

    pref_keywords = tags_to_keywords(pref_tags)
    dislike_keywords = tags_to_keywords(dislike_tags)
    target = [1.0 if e == weakest else (0.1 if e == strongest else 0.5) for e in ELEMENTS]

    rows = []
    for _, row in work.iterrows():
        text = row["all_text"]
        dislike_score = keyword_hit_score(text, dislike_keywords)
        pref_score = keyword_hit_score(text, pref_keywords)
        vec = [float(row[e]) for e in ELEMENTS]
        
        denom = math.sqrt(sum(t*t for t in target)) * math.sqrt(sum(v*v for v in vec))
        sim = sum(t * v for t, v in zip(target, vec)) / denom if denom > 0 else 0.0
        
        brand_bonus = 0.15 if any(b.lower() in str(row.get("Brand", "")).lower() for b in FAMOUS_BRANDS) else 0.0
        final_score = (0.55 * sim) + (0.20 * float(row.get(weakest, 0.0))) + (0.18 * pref_score) - (0.20 * dislike_score) + brand_bonus
        if dislike_score >= 0.4: final_score -= 0.5
        
        r = row.to_dict(); r.update({"score": final_score, f"{weakest}_fill": float(row.get(weakest, 0.0))})
        rows.append(r)

    out = pd.DataFrame(rows).sort_values("score", ascending=False).drop_duplicates(subset=["Name"]).reset_index(drop=True)
    return out

# =========================================================
# 7) 메인 화면 UI
# =========================================================
st.markdown("<h1>🔮 향수 사쥬</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">실제 만세력 기반으로 사주 오행을 분석하고<br>부족한 기운을 보완해줄 맞춤 향수를 처방해드려요.</div>', unsafe_allow_html=True)

if df.empty:
    st.error("향수 데이터베이스를 불러오지 못했습니다.")
    st.stop()

with st.form("saju_form"):
    user_name = st.text_input("이름 (또는 닉네임)", placeholder="예: 홍길동")
    gender = st.selectbox("성별", ["선택 안 함", "여성", "남성"], index=0)
    birth_date = st.date_input("생년월일 (양력)", min_value=datetime.date(1950, 1, 1), value=datetime.date(1995, 1, 1))

    st.markdown("<p style='font-size:14px; margin-bottom:5px; color:#333; font-weight:bold;'>태어난 시간</p>", unsafe_allow_html=True)
    know_time = st.checkbox("태어난 시간을 모릅니다 (체크 시 시간 제외 분석)")

    if know_time:
        b_hour, b_min = None, None
    else:
        c1, c2 = st.columns(2)
        with c1: b_hour = st.selectbox("시", list(range(24)), index=12)
        with c2: b_min = st.selectbox("분", list(range(60)), index=0)

    st.markdown("<hr style='margin:1.2rem 0; border:none; border-top:1px dashed #ddd;'>", unsafe_allow_html=True)
    
    tag_options = list(TAG_TO_KEYWORDS.keys())
    pref_tags = st.multiselect("끌리는 향 (복수 선택)", tag_options)
    dislike_tags = st.multiselect("피하고 싶은 향", [t for t in tag_options if t not in pref_tags])
    brand_filter_mode = st.radio("브랜드 범위", ["전체 브랜드", "유명 브랜드 위주"], horizontal=True, index=1)

    submit = st.form_submit_button("향수 처방 받기")

# =========================================================
# 8) 분석 및 결과
# =========================================================
if submit:
    if not user_name.strip():
        st.warning("이름(또는 닉네임)을 입력해주세요.")
        st.stop()

    session_id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 💡 수정포인트: 모를 경우 완전 None을 넘겨서 6글자만 분석하도록 버그 픽스!
    calc_hour = None if know_time else b_hour
    calc_min = None if know_time else b_min

    loading = st.empty()
    for msg in ["🔮 만세력 스캐닝 중...", "🌿 오행 에너지 분석 중...", "✨ 맞춤 향수 배합 중..."]:
        loading.markdown(f"<h3 style='text-align:center; color:#2a5298; margin: 28px 0;'>{msg}</h3>", unsafe_allow_html=True)
        time.sleep(0.8)
    loading.empty()

    result = get_real_saju_elements(birth_date.year, birth_date.month, birth_date.day, calc_hour, calc_min)
    if result[0] is None:
        st.error("사주 계산에 실패했습니다.")
        st.stop()

    saju_name, e_counts, strong, weak, gapja_str = result
    rec_df = recommend_perfumes(df.copy(), weak, strong, pref_tags, dislike_tags, brand_filter_mode)
    
    if rec_df.empty or len(rec_df) < 3:
        st.error("조건에 맞는 향수가 부족해요. 필터를 줄여주세요.")
        st.stop()

    top3 = rec_df.head(3).copy()
    try: save_recommendation_log(session_id, user_name.strip(), gender, birth_date, know_time, saju_name, strong, weak, top3)
    except: pass

    # 상태 저장
    st.session_state.update({"top3": top3, "saju_name": saju_name, "e_counts": e_counts, "strong": strong, "weak": weak, "gender": gender, "know_time": know_time, "session_id": session_id, "user_name": user_name})

# 결과 렌더링
if "top3" in st.session_state:
    top3, saju_name, e_counts = st.session_state["top3"], st.session_state["saju_name"], st.session_state["e_counts"]
    strong, weak, know_time = st.session_state["strong"], st.session_state["weak"], st.session_state["know_time"]
    
    st.markdown(f"### {st.session_state['user_name']}님의 향수 사쥬 결과")
    
    col_a, col_b = st.columns(2)
    col_a.markdown(f"<div class='card'><b>가장 강한 기운</b><br>{ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}</div>", unsafe_allow_html=True)
    col_b.markdown(f"<div class='card'><b>보완할 기운</b><br>{ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}</div>", unsafe_allow_html=True)

    with st.spinner("AI가 처방전을 작성 중입니다..."):
        reading_result = generate_comprehensive_reading(
            st.session_state["user_name"], st.session_state["gender"], saju_name, strong, weak, top3, know_time
        )
    st.markdown(f"<div class='card'>{reading_result}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛍️ 추천 향수 시향해보기")
    
    # 💡 수정포인트: UX를 위해 클릭 로깅용 이중버튼 제거하고 직관적인 링크 버튼으로 교체
    for i, (_, row) in enumerate(top3.iterrows()):
        b_name, p_name = safe_text(row.get("Brand")), safe_text(row.get("Name"))
        naver_url = f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(f'{b_name} {p_name} 향수')}"
        st.link_button(f"{['🥇','🥈','🥉'][i]} {b_name} - {p_name} 검색하기", naver_url, use_container_width=True)

    st.markdown("---")
    survey_url = f"{SURVEY_BASE_URL}?session_id={urllib.parse.quote(st.session_state['session_id'])}"
    st.info("🙋 추천 결과가 어떠셨나요? 1분 설문에 참여해주시면 더 좋은 서비스를 만들 수 있어요!")
    st.link_button("📝 1분 설문 참여하기", survey_url, use_container_width=True)

# =========================================================
# 9) 관리자용 로그 (하단 숨김)
# =========================================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
with st.expander("🔐 [관리자용] 추천 로그 데이터 확인"):
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "rb") as f:
            st.download_button("📥 누적 추천 로그 CSV 다운로드", f, file_name="recommendation_logs.csv", mime="text/csv")
    else:
        st.write("아직 저장된 로그가 없습니다.")
