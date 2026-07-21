import streamlit as st
import pandas as pd
import datetime
import os
import math
import time
import urllib.parse
import uuid
import re
import html as _html
from korean_lunar_calendar import KoreanLunarCalendar
from io import BytesIO

# OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except Exception:
    OPENAI_SDK_AVAILABLE = False


# =========================================================
# 0) 기본 설정 및 모바일 앱 스타일
# =========================================================
st.set_page_config(page_title="이 향수 사쥬!!", page_icon="🥺", layout="centered")

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

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
.small-muted { font-size: 12px; color: #666; }

/* 히어로 카드 */
.hero {
  background: linear-gradient(135deg, #eef4ff 0%, #ffffff 55%, #f7f7ff 100%);
  border: 1px solid #e7ecff;
  border-radius: 18px;
  padding: 14px 14px;
  margin: 10px 0 14px 0;
}
.hero-title {
  font-size: 18px;
  font-weight: 850;
  color: #1e3c72;
  line-height: 1.35;
  text-align:center;
  margin: 4px 0 8px 0;
}
.hero-sub { text-align:center; color:#666; font-size: 12px; line-height:1.5; }
.kpi-row { display:flex; gap:10px; margin-top:12px; }
.kpi {
  flex:1;
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 10px;
  background:#fff;
}
.kpi b { color:#222; }
.kpi .val { margin-top:4px; font-weight:800; color:#1e3c72; }
.section-card {
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 12px;
  background:#fff;
  margin-bottom: 12px;
}
.small-note { font-size: 12px; color:#777; line-height:1.55; }
div[data-baseweb="tab-panel"] { padding-top: 10px; }

/* ===== 궁합 점수 UI ===== */
.compat-score-wrap {
  text-align: center;
  padding: 24px 0 16px 0;
}
.compat-score-num {
  font-size: 72px;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.compat-score-label {
  font-size: 15px;
  color: #666;
  margin-top: 6px;
}
.compat-oneliner {
  text-align: center;
  font-size: 18px;
  font-weight: 800;
  color: #191f28;
  margin: 12px 0 16px 0;
  line-height: 1.4;
}
.compat-tag {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  margin: 3px 4px;
}
.tag-good { background: #e8f3ff; color: #1e3c72; border: 1px solid #c2d9ff; }
.tag-bad  { background: #fff0f0; color: #c0392b; border: 1px solid #ffd0d0; }

/* ===== 필터 스텝 ===== */
.step-header {
  text-align: center;
  font-size: 20px;
  font-weight: 800;
  color: #1e3c72;
  margin-bottom: 6px;
}
.step-sub {
  text-align: center;
  font-size: 13px;
  color: #666;
  margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 1) 경로 / 상수 / OpenAI 설정
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
# 🚨 [수정 완료] 최신 DB 파일명으로 변경
DATA_PATH = os.path.join(base_dir, "fatescent_master_db_v2_fixed.csv")
LOG_PATH = os.path.join(base_dir, "recommendation_logs.csv")

SURVEY_BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfLuBSOMDSbph7vY3qfOeW-1yvFvKVnGIsWjkMBRZ8w-SdE5w/viewform?usp=pp_url&entry.1954804504="

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
    return [f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]} {v:.2f}" for e, v in top2 if v > 0]

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
    t = t.replace("```html", "").replace("```", "")
    return t.strip()

def _pick_lucky_color_place(weak_element: str):
    mapping = {
        "Wood": {"colors": ["올리브 그린", "세이지 그린"], "places": ["숲길 산책로", "식물 많은 카페(플랜테리어)"]},
        "Fire": {"colors": ["코랄 레드", "선셋 오렌지"], "places": ["노을 보이는 강변", "따뜻한 조명 바/라운지"]},
        "Earth": {"colors": ["샌드 베이지", "토프 브라운"], "places": ["도자기 공방/전시", "우드톤 북카페"]},
        "Metal": {"colors": ["실버 그레이", "오프화이트"], "places": ["미술관/갤러리", "정돈된 호텔 로비 라운지"]},
        "Water": {"colors": ["딥 네이비", "아쿠아 블루"], "places": ["바다/호수 산책", "비 오는 날 창가 자리 카페"]},
    }
    return mapping.get(weak_element, {"colors": ["오프화이트", "그레이"], "places": ["조용한 카페", "산책로"]})

def notes_to_korean_summary(notes_text: str) -> str:
    t = safe_text(notes_text).lower()
    if not t:
        return "노트 정보 없음"
    mapping = [
        (["citrus", "bergamot", "lemon", "orange", "grapefruit", "mandarin", "yuzu", "lime"], "상큼한 시트러스"),
        (["floral", "rose", "jasmine", "tuberose", "iris", "neroli", "ylang"], "화사한 플로럴"),
        (["woody", "cedar", "sandalwood", "vetiver", "patchouli", "moss", "oud"], "차분한 우디"),
        (["musk", "white musk", "clean musk", "soft musk"], "포근한 머스크"),
        (["vanilla", "tonka", "benzoin", "gourmand", "sweet", "amber"], "달콤한 앰버/바닐라"),
        (["aquatic", "marine", "sea", "ozonic", "watery", "salt"], "시원한 아쿠아/마린"),
        (["spicy", "pepper", "ginger", "cinnamon", "warm spicy"], "따뜻한 스파이시"),
        (["leather", "tobacco", "smoky", "incense", "animalic"], "스모키/가죽 무드"),
        (["powdery"], "보송한 파우더리"),
        (["soapy", "aldehyde"], "깔끔한 비누/클린"),
        (["mint"], "민트처럼 청량함"),
    ]
    hits = []
    for kws, ko in mapping:
        if any(k in t for k in kws):
            hits.append(ko)
    hits = list(dict.fromkeys(hits))
    if not hits:
        return "은은하고 부드러운 데일리 향"
    return " · ".join(hits[:3])

def build_east_asian_note_reason(weak_element: str, matched_notes: list) -> str:
    weak_ko = ELEMENTS_KO.get(weak_element, weak_element)
    lore = {
        "Wood": "예부터 목(木)은 '성장·확장·생기'로 보았어요. 초록/허브/우디 계열은 새싹이 돋는 느낌처럼 목의 흐름을 깨워주는 향으로 자주 비유됩니다.",
        "Fire": "화(火)는 '활력·온기·표현'과 연결돼요. 시트러스/스파이시처럼 밝고 톡 튀는 향은 기운을 위로 끌어올려 화의 생동감을 살리는 쪽으로 해석됩니다.",
        "Earth": "토(土)는 '안정·중심·포용'의 이미지예요. 머스크/앰버/바닐라처럼 포근하고 감싸는 향은 마음을 붙잡아 주는 토의 성질과 잘 맞는다고 봅니다.",
        "Metal": "금(金)은 '정리·기준·결단'의 이미지가 강해요. 클린/비누/미네랄/민트 계열은 군더더기를 덜어내는 느낌이라 금의 또렷함을 돋운다고 해석합니다.",
        "Water": "수(Water)는 '유연·깊이·흐름'이에요. 아쿠아/마린/오존 계열은 물의 결을 떠올리게 해서 수의 흐름을 자연스럽게 살린다고 봅니다.",
    }
    if matched_notes:
        notes_ko = ", ".join(matched_notes[:3])
        return f"당신의 부족한 <b>{weak_ko}</b> 기운을 <b>{notes_ko}</b> 계열 노트가 채워주는 방향이에요. {lore.get(weak_element, '')}"
    return f"당신의 부족한 <b>{weak_ko}</b> 기운을 채우는 데 도움이 되는 계열로 추천됐어요. {lore.get(weak_element, '')}"


# =========================================================
# 3) 사주 계산
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
        if c in element_map:
            counts[element_map[c]] += 1

    sorted_e = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return saju_name, counts, sorted_e[0][0], sorted_e[-1][0], gapja_str


# =========================================================
# 4) 궁합 분석 (NEW)
# =========================================================
def find_perfume_in_db(df, brand_input: str, name_input: str):
    """DB에서 향수 검색. 퍼지 매칭(소문자 포함 여부)."""
    if df.empty:
        return None
    brand_q = brand_input.strip().lower()
    name_q = name_input.strip().lower()

    # 🚨 [수정 완료] regex=False 추가로 특수문자 에러 방어
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
    return hits.sort_values("_name_len").iloc[0]


def get_perfume_notes_via_ai(brand: str, name: str) -> str:
    if not HAS_AI or client is None:
        return ""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 향수 전문가야. 향수의 주요 노트를 영어로 콤마 구분해서만 답해. 예: bergamot, rose, sandalwood, musk. 다른 말은 하지 마."},
                {"role": "user", "content": f"향수: {brand} - {name}\n이 향수의 주요 향 노트를 알려줘."}
            ],
            temperature=0.3,
            max_tokens=150
        )
        return resp.choices[0].message.content.strip() if resp and resp.choices else ""
    except Exception:
        return ""


def compute_perfume_element_vector(notes_text: str) -> dict:
    t = notes_text.lower()
    vec = {}
    for elem, kws in ELEMENT_KEYWORDS.items():
        hits = sum(1 for kw in kws if kw in t)
        vec[elem] = hits
    total = sum(vec.values())
    if total > 0:
        vec = {k: round(v / total, 3) for k, v in vec.items()}
    else:
        vec = {k: 0.0 for k in ELEMENTS}
    return vec


def compute_compatibility_score(user_counts: dict, perfume_vec: dict, weak: str, strong: str) -> int:
    total_user = sum(user_counts.values()) or 1
    user_norm = {e: user_counts[e] / total_user for e in ELEMENTS}

    total_perf = sum(perfume_vec.values()) or 1
    perf_norm = {e: perfume_vec.get(e, 0) / total_perf for e in ELEMENTS}

    dot = sum(user_norm[e] * perf_norm[e] for e in ELEMENTS)
    mag_u = math.sqrt(sum(v**2 for v in user_norm.values()))
    mag_p = math.sqrt(sum(v**2 for v in perf_norm.values()))
    cosine = dot / (mag_u * mag_p) if mag_u * mag_p > 0 else 0.0

    complement_score = perf_norm.get(weak, 0.0)
    overload_penalty = perf_norm.get(strong, 0.0) * user_norm.get(strong, 0.0)

    raw = (0.35 * cosine) + (0.50 * complement_score) - (0.25 * overload_penalty)
    score = max(0.0, min(1.0, raw + 0.3)) 
    return int(round(score * 100))


def build_compatibility_prompt(
    user_name, gender, saju_name, strong, weak,
    perf_brand, perf_name, notes_text, score, perf_vec
) -> str:
    strong_ko = ELEMENTS_KO.get(strong, strong)
    weak_ko = ELEMENTS_KO.get(weak, weak)
    gender_tone = get_gender_tone(gender)["style"]

    top2_perf = sorted(perf_vec.items(), key=lambda x: x[1], reverse=True)[:2]
    top2_str = ", ".join([f"{ELEMENT_EMOJI[e]} {ELEMENTS_KO[e]}({v:.0%})" for e, v in top2_perf if v > 0])

    return f"""
너는 명리학과 조향을 연결해 설명하는 전문가야.
결과는 **반드시 JSON만** 출력해. 다른 말 일절 금지.

[사용자 정보]
이름: {user_name}, 성별: {gender}(문체: {gender_tone})
사주: {saju_name}
강한 기운: {strong_ko}, 부족한 기운: {weak_ko}

[향수 정보]
브랜드: {perf_brand}, 향수명: {perf_name}
노트: {notes_text}
향수의 주요 오행: {top2_str}
궁합 점수: {score}점

[출력 JSON 형식]
{{
  "one_liner": "총평 한 줄(20자 이내, 재미있고 임팩트 있게. 예: '불꽃에 기름 붓는 향💥')",
  "good_reasons": ["잘 맞는 이유 1(30자 이내)", "잘 맞는 이유 2(30자 이내)"],
  "bad_reasons": ["안 맞는 이유 1(30자 이내)", "안 맞는 이유 2(30자 이내)"],
  "perf_element_summary": "이 향수의 오행 설명(2~3문장. 어떤 기운이 강하고 약한지)",
  "compatibility_detail": "궁합 점수에 대한 설명(3~4문장. 왜 이 점수인지, 어떤 상황에 쓰면 좋은지)"
}}
""".strip()


def generate_compatibility_result(
    user_name, gender, saju_name, strong, weak,
    perf_brand, perf_name, notes_text, score, perf_vec
) -> dict:
    strong_ko = ELEMENTS_KO.get(strong, strong)
    weak_ko = ELEMENTS_KO.get(weak, weak)
    top2_perf = sorted(perf_vec.items(), key=lambda x: x[1], reverse=True)[:2]
    top2_names = [ELEMENTS_KO[e] for e, v in top2_perf if v > 0]

    fallback = {
        "one_liner": f"{'운명의 향✨' if score >= 75 else '🤔 애증의 향' if score >= 50 else '😅 기운 역주행 향'}",
        "good_reasons": [
            f"{top2_names[0] if top2_names else '이 향'}의 기운이 개성을 살려줄 수 있어요",
            f"노트 구성이 현재 컨디션에 자극이 될 수 있어요"
        ],
        "bad_reasons": [
            f"{strong_ko} 기운이 이미 강한데 향도 비슷한 방향이에요",
            f"부족한 {weak_ko} 기운 보완엔 아쉬울 수 있어요"
        ],
        "perf_element_summary": f"이 향수는 {', '.join(top2_names[:2]) if top2_names else '다양한'} 기운이 주를 이루고 있어요. 노트 구성에서 그 기운이 잘 드러나요.",
        "compatibility_detail": f"궁합 점수 {score}점은 {'좋은 편이에요. 지금 컨디션에 잘 맞는 향이에요.' if score >= 70 else '보통 수준이에요. 기분에 따라 잘 맞을 수도 있어요.' if score >= 50 else '조금 아쉬운 편이에요. 부족한 기운을 더 잘 채우는 향이 있어요.'}"
    }

    if not HAS_AI or client is None:
        return fallback

    prompt = build_compatibility_prompt(
        user_name, gender, saju_name, strong, weak,
        perf_brand, perf_name, notes_text, score, perf_vec
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 명리학+조향 전문가야. 반드시 JSON만 출력해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        raw = resp.choices[0].message.content if resp and resp.choices else ""
        raw = _strip_code_fences(raw)
        import json
        data = json.loads(raw)
        required = ["one_liner", "good_reasons", "bad_reasons", "perf_element_summary", "compatibility_detail"]
        if all(k in data for k in required):
            return data
        return fallback
    except Exception:
        return fallback


# =========================================================
# 5) AI 사주 풀이
# =========================================================
def build_ai_reading_prompt_html(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    gender_tone = get_gender_tone(gender)["style"]
    p = top3_df.head(3).copy()
    p1 = p.iloc[0]
    p2 = p.iloc[1] if len(p) > 1 else p1
    p3 = p.iloc[2] if len(p) > 2 else p1
    time_notice = (
        "사용자는 태어난 시간을 모름으로 선택했음. 반드시 '정오 기준 + 오차 가능' 안내를 1줄로 넣어라."
        if know_time else "사용자는 태어난 시간을 입력했음."
    )
    prompt = f"""
너는 '명리학 + 조향'을 연결해 설명하는 전문가야.
결과는 **오직 HTML로만** 작성해. 마크다운(###, **, -) 절대 금지. 코드블록 ``` 절대 금지.

[고객] 이름: {user_name}, 성별: {gender}(문체: {gender_tone})
사주: {saju_name}, 강한 기운: {strong_ko}, 보완 기운: {weak_ko}
조건: {time_notice}

[추천 향수 Top3]
1) {safe_text(p1.get("Brand",""))} - {safe_text(p1.get("Name",""))} / Notes: {safe_text(p1.get("Notes","정보 없음"))}
2) {safe_text(p2.get("Brand",""))} - {safe_text(p2.get("Name",""))} / Notes: {safe_text(p2.get("Notes","정보 없음"))}
3) {safe_text(p3.get("Brand",""))} - {safe_text(p3.get("Name",""))} / Notes: {safe_text(p3.get("Notes","정보 없음"))}

[작성 규칙]
- 초등학생도 이해할 말로 쓰되, 전문가처럼 체계적으로.
- 사주 파트는 충분히 길게.
- 각 섹션에 현실 예시 1개 포함.
- 점술처럼 단정 금지: "~할 수 있어요 / 도움이 될 수 있어요".

[HTML 출력 템플릿]
<h2 style="color:#1e3c72; text-align:center; font-size:1.6rem; padding: 10px 0; margin: 6px 0 10px 0;">(한 단어) — "(한 줄 비유 1문장)"</h2>
<div style="text-align:center; font-size:0.95rem; color:#555; margin-bottom: 12px;">강한 기운: {strong_ko} / 보완 기운: {weak_ko}</div>
<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">(시간 안내 1줄)</div>
<h3 style="margin:14px 0 8px 0;">📜 사주 및 오행 분석</h3>
<div style="color:#333; line-height:1.75;">
  <div style="margin-bottom:12px;"><b>1) 강한 기운의 장점</b><br>(3~4문장)</div>
  <div style="margin-bottom:12px;"><b>2) 강한 기운이 과할 때 주의점</b><br>(3문장)</div>
  <div style="margin-bottom:12px;"><b>3) 부족 기운 신호</b><br>(3~4문장)</div>
  <div style="margin-bottom:12px;"><b>4) 부족 기운을 채우면 생기는 균형</b><br>(3~4문장)</div>
  <div style="margin-bottom:12px;"><b>5) 잘 풀리는 환경/관계 스타일</b><br>(3문장)</div>
</div>
<h3 style="margin:14px 0 8px 0;">💖 향기로 운을 틔웠을 때의 변화</h3>
<ul style="line-height:1.8; color:#333;">
  <li><b>💰 재물운:</b> ...</li>
  <li><b>💕 연애운:</b> ...</li>
  <li><b>🤝 인간관계:</b> ...</li>
</ul>
<hr style="border:none; border-top:1px solid #eee; margin: 12px 0;">
<h3 style="margin:14px 0 8px 0;">🧴 맞춤 향수 처방전 (Top 3)</h3>
(각 향수 카드 3개, 브랜드/향수명/한줄이미지/왜 {weak_ko} 기운 채우나/기대효과 포함)
<hr style="border:none; border-top:1px solid #eee; margin: 12px 0;">
<h3 style="margin:14px 0 8px 0;">🍀 당신의 네잎클로버</h3>
<ul style="line-height:1.8; color:#333;">
  <li><b>🎨 나와 잘 맞는 색깔:</b> (2개)</li>
  <li><b>📍 나와 잘 맞는 장소:</b> (2곳)</li>
</ul>
"""
    return prompt.strip()


def generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    p = top3_df.head(3).copy()
    if len(p) == 0:
        return "<div>추천 결과가 부족해요. 조건을 조금 완화해 주세요.</div>"
    lucky = _pick_lucky_color_place(weakest)
    colors, places = lucky["colors"], lucky["places"]
    time_notice_html = (
        '<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">⏰ 태어난 시간을 모른다고 선택하셔서, <b>정오 기준(오차 가능)</b>으로 연/월/일 6글자 중심 풀이예요.</div>'
        if know_time else
        '<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">⏰ 태어난 시간까지 반영해서 8글자 기준으로 풀이했어요.</div>'
    )
    one_word_map = {
        "Wood": ("숲", "당신은 바람에도 다시 자라는 숲의 사람입니다."),
        "Fire": ("등불", "당신은 주변을 밝히는 따뜻한 등불입니다."),
        "Earth": ("흙길", "당신은 흔들림 없이 중심을 잡아주는 흙길입니다."),
        "Metal": ("칼날", "당신은 군더더기 없이 선명한 칼날의 사람입니다."),
        "Water": ("물결", "당신은 바다로 향하는 깊은 물결입니다."),
    }
    one_word, one_line = one_word_map.get(strongest, ("기운", "당신은 고유한 흐름을 가진 사람입니다."))
    medals = ["🥇", "🥈", "🥉"]
    cards_html = ""
    for i, (_, r) in enumerate(p.iterrows()):
        b = safe_text(r.get("Brand", ""))
        n = safe_text(r.get("Name", ""))
        notes = safe_text(r.get("Notes", "정보 없음"))
        cards_html += f"""
<div style="border:1px solid #eee; border-radius:12px; padding:12px; margin-bottom:10px;">
  <div style="font-weight:800;">{medals[i]} {i+1}위. {b} - {n}</div>
  <div style="margin-top:6px;"><b>한줄 이미지:</b> {weak_ko} 기운을 부드럽게 채워주는 '무드 보정' 향이에요.</div>
  <div style="margin-top:6px;"><b>향기 노트:</b> {notes}</div>
  <div style="margin-top:6px;"><b>왜 {weak_ko} 기운을 채우나:</b> 이 향의 핵심 노트가 {weak_ko}의 이미지에 닿아 있어요.</div>
  <div style="margin-top:6px;"><b>기대 효과:</b> 기분이 정돈되고, 선택이 또렷해질 수 있어요.</div>
</div>"""
    return f"""
<h2 style="color:#1e3c72; text-align:center; font-size:1.6rem; padding: 10px 0; margin: 6px 0 10px 0;">{one_word} — "{one_line}"</h2>
<div style="text-align:center; font-size:0.95rem; color:#555; margin-bottom: 12px;">강한 기운: {strong_ko} / 보완 기운: {weak_ko}</div>
{time_notice_html}
<h3 style="margin:14px 0 8px 0;">📜 사주 및 오행 분석</h3>
<div style="color:#333; line-height:1.75;">
  <div style="margin-bottom:12px;"><b>1) 강한 기운의 장점</b><br>강한 기운이 뚜렷하면 분위기와 선택 기준이 분명해지는 편이에요.</div>
  <div style="margin-bottom:12px;"><b>2) 강한 기운이 과할 때 주의점</b><br>피곤할 때 생각이 많아져 결정을 미루고 기회를 놓칠 수 있어요.</div>
  <div style="margin-bottom:12px;"><b>3) 부족 기운이 부족할 때 나타나는 신호</b><br>{weak_ko}가 부족하면 정리/기준/결정이 늦어질 수 있어요.</div>
  <div style="margin-bottom:12px;"><b>4) 부족 기운을 채우면 생기는 균형</b><br>마음은 부드럽고, 행동은 또렷해지는 쪽으로 균형이 잡힐 수 있어요.</div>
  <div style="margin-bottom:12px;"><b>5) 잘 풀리는 환경/관계 스타일</b><br>역할과 기준이 명확한 환경에서 강점을 더 잘 발휘할 수 있어요.</div>
</div>
<h3 style="margin:14px 0 8px 0;">🧴 맞춤 향수 처방전 (Top 3)</h3>
{cards_html}
<h3 style="margin:14px 0 8px 0;">🍀 깨알 재미 요소</h3>
<ul style="line-height:1.8; color:#333;">
  <li><b>🎨 나와 잘 맞는 색깔:</b> {colors[0]}, {colors[1]}</li>
  <li><b>📍 나와 잘 맞는 장소:</b> {places[0]}, {places[1]}</li>
</ul>
""".strip()


def generate_comprehensive_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time):
    if not HAS_AI or client is None:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
    prompt = build_ai_reading_prompt_html(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 사용자가 이해하기 쉽게 풀어주는 '명리학+조향' 전문가야. 결과는 반드시 HTML만 출력해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75
        )
        out = response.choices[0].message.content if response and response.choices else ""
        out = _strip_code_fences(out)
        if "<h2" not in out or "<h3" not in out:
            return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
        return out
    except Exception:
        return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)


# =========================================================
# 6) 로그 저장
# =========================================================
def save_recommendation_log(session_id, user_name, gender, birth_date, know_time, saju_name, strongest, weakest, top3_df):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for rank_idx, (_, row) in enumerate(top3_df.iterrows(), start=1):
        rows.append({
            "timestamp": now_str, "session_id": session_id,
            "user_name": user_name, "gender": gender,
            "birth_date": str(birth_date), "know_time": 0 if know_time else 1,
            "saju_name": saju_name, "strongest_element": strongest, "weakest_element": weakest,
            "rank": rank_idx, "perfume_name": safe_text(row.get("Name", "")),
            "brand": safe_text(row.get("Brand", "")), "rec_score": float(row.get("score", 0.0))
        })
    df_log = pd.DataFrame(rows)
    df_log.to_csv(
        LOG_PATH, mode="a" if os.path.exists(LOG_PATH) else "w",
        header=not os.path.exists(LOG_PATH), index=False, encoding="utf-8-sig"
    )


# =========================================================
# 7) 데이터 로드 및 추천 엔진 (🚨 최종 진화형으로 완벽 교체)
# =========================================================
MIN_AFTER_GENDER_FILTER = 30
MIN_AFTER_BRAND_FILTER = 20
GENDER_THRESHOLDS = [0.45, 0.35, 0.25]
DROP_DUP_KEYS = ["Brand", "Name"]

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(DATA_PATH)

    text_columns = ["Name", "Brand", "Notes", "Description", "matched_keywords", "Top", "Middle", "Base", "Gender"]
    for c in text_columns:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    # 성별 스코어 (신규 DB 완벽 호환)
    for c in ["Female_Score", "Male_Score"]:
        if c not in df.columns:
            df[c] = 0.5
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.5)

    for e in ELEMENTS:
        if e not in df.columns:
            df[e] = 0.0
        df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)

    df["all_text"] = (
        df["Name"] + " " + df["Brand"] + " " +
        df["Notes"] + " " + df["matched_keywords"] + " " +
        df["Top"] + " " + df["Middle"] + " " + df["Base"] + " " +
        df["Gender"]
    ).str.lower().fillna("")

    df["element_sum"] = df[ELEMENTS].sum(axis=1)
    df = df[df["element_sum"] > 0].copy()

    ban_words = ["sample", "discovery", "set", "gift", "miniature"]
    mask = ~df["Name"].str.lower().apply(lambda x: any(w in x for w in ban_words))
    df = df[mask].copy()

    for c in DROP_DUP_KEYS:
        if c not in df.columns:
            df[c] = ""
    df = df.drop_duplicates(subset=DROP_DUP_KEYS).reset_index(drop=True)
    return df

df = load_data()

def _apply_gender_filter(work: pd.DataFrame, user_gender: str) -> pd.DataFrame:
    if work.empty or user_gender not in ["남성향", "여성향"]:
        return work  
    score_col = "Male_Score" if user_gender == "남성향" else "Female_Score"
    
    # 성별 필터 단계적 완화 로직 적용
    for thr in GENDER_THRESHOLDS:
        filtered = work[work[score_col] >= thr]
        if len(filtered) >= MIN_AFTER_GENDER_FILTER:
            return filtered.copy()
    return work

def recommend_perfumes(df, weakest, strongest, pref_tags, dislike_tags, brand_filter_mode, gender_filter="전체"):
    if df.empty:
        return pd.DataFrame()
    work = df.copy()

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


# =========================================================
# 8) 로딩 헬퍼
# =========================================================
loading_css = """
<style>
@keyframes pulse-text { 0%{opacity:1;} 50%{opacity:0.45;} 100%{opacity:1;} }
@keyframes spin-icon  { 0%{transform:rotate(0deg);} 100%{transform:rotate(360deg);} }
@keyframes move-bar   { 0%{transform:translateX(-60%);} 100%{transform:translateX(160%);} }
.loading-box{ border:1px solid #e7ecff; border-radius:18px; padding:16px 14px; background:linear-gradient(135deg,#eef4ff 0%,#ffffff 55%,#f7f7ff 100%); }
.loading-title{ text-align:center; color:#1e3c72; font-weight:850; margin:6px 0 10px 0; }
.loading-sub{ text-align:center; font-size:13px; color:#666; line-height:1.5; margin-top:8px; }
.loading-spin{ display:inline-block; animation:spin-icon 1.1s linear infinite; margin-right:6px; }
.loading-pulse{ animation:pulse-text 1.6s infinite ease-in-out; }
.progress-wrap{ height:10px; border-radius:999px; background:#eef2ff; overflow:hidden; border:1px solid #e7ecff; margin:10px 0 8px 0; }
.progress-fill{ height:100%; border-radius:999px; background:linear-gradient(90deg,#1e3c72 0%,#2a5298 100%); transition:width 0.35s ease; }
.indeterminate{ position:relative; height:10px; border-radius:999px; background:#eef2ff; overflow:hidden; border:1px solid #e7ecff; margin:10px 0 8px 0; }
.indeterminate:before{ content:""; position:absolute; top:0; left:0; height:100%; width:40%; background:linear-gradient(90deg,rgba(30,60,114,0) 0%,rgba(42,82,152,0.8) 50%,rgba(30,60,114,0) 100%); animation:move-bar 1.1s infinite linear; }
.step-list{ margin:10px 0 0 0; padding:0; list-style:none; }
.step-item{ font-size:13px; color:#555; padding:4px 0; }
.step-done{ color:#2a5298; font-weight:700; }
.step-now{ color:#1e3c72; font-weight:850; }
.step-wait{ color:#888; }
</style>
"""

def render_loading(placeholder, current_step: int, title: str, percent: int, step_texts: list, ai_mode: bool = False):
    li = []
    for idx, s in enumerate(step_texts, start=1):
        if idx < current_step:
            li.append(f"<li class='step-item step-done'>✅ {s}</li>")
        elif idx == current_step:
            li.append(f"<li class='step-item step-now'>👉 {s}</li>")
        else:
            li.append(f"<li class='step-item step-wait'>⬜ {s}</li>")
    steps_html = "\n".join(li)
    bar_html = (
        "<div class='indeterminate'></div>" if ai_mode else
        f"<div class='progress-wrap'><div class='progress-fill' style='width:{percent}%;'></div></div>"
    )
    placeholder.markdown(f"""
{loading_css}
<div class="loading-box">
  <div class="loading-title loading-pulse"><span class="loading-spin">⏳</span>{title}</div>
  {bar_html}
  <ul class="step-list">{steps_html}</ul>
  <div class="loading-sub">새로고침하지 말고 잠시만 기다려주세요 🙏</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 9) 스텝 초기화
# =========================================================
if "step" not in st.session_state:
    st.session_state["step"] = 1


# =========================================================
# 10) 공통 헤더
# =========================================================
st.markdown("<h1>🥺 이 향수 사쥬!!</h1>", unsafe_allow_html=True)

if df.empty:
    st.error("향수 데이터베이스를 불러오지 못했습니다.")
    st.stop()


# =========================================================
# ✅ STEP 1 — 기본 정보 + 현재 쓰는 향수 입력
# =========================================================
if st.session_state["step"] == 1:
    st.markdown('<div class="subtitle">내가 쓰는 향수, 나랑 잘 맞을까?<br>사주로 궁합 점수 확인해봐 👀</div>', unsafe_allow_html=True)

    with st.form("step1_form"):
        st.markdown("#### 👤 내 정보")
        user_name = st.text_input("이름 (또는 닉네임)", placeholder="예: 홍길동")
        gender = st.selectbox("성별", ["선택 안 함", "여성", "남성"], index=0)
        birth_date = st.date_input("생년월일 (양력)", min_value=datetime.date(1950, 1, 1), value=datetime.date(1995, 1, 1))

        st.markdown("<p style='font-size:14px; margin-bottom:5px; color:#333; font-weight:bold;'>태어난 시간</p>", unsafe_allow_html=True)
        know_time = st.checkbox("태어난 시간을 몰라요 (체크 시 시간 제외 분석)")
        if know_time:
            b_hour, b_min = None, None
        else:
            c1, c2 = st.columns(2)
            with c1:
                b_hour = st.selectbox("시", list(range(24)), index=12)
            with c2:
                b_min = st.selectbox("분", list(range(60)), index=0)

        st.markdown("<hr style='margin:1.2rem 0; border:none; border-top:1px dashed #ddd;'>", unsafe_allow_html=True)
        st.markdown("#### 🧴 지금 쓰는 향수")
        st.markdown('<p class="small-muted">현재 사용 중이거나 관심 있는 향수를 입력해주세요.</p>', unsafe_allow_html=True)
        perf_brand = st.text_input("브랜드명", placeholder="예: Jo Malone, Diptyque, Chanel")
        perf_name = st.text_input("향수명", placeholder="예: Wood Sage & Sea Salt, Lime Basil & Mandarin")

        submit1 = st.form_submit_button("✨ 궁합 점수 확인하기")

    if submit1:
        if not user_name.strip():
            st.warning("이름(또는 닉네임)을 입력해주세요.")
            st.stop()
        if not perf_brand.strip() or not perf_name.strip():
            st.warning("브랜드명과 향수명을 모두 입력해주세요.")
            st.stop()

        calc_hour = None if know_time else b_hour
        calc_min = None if know_time else b_min

        loading = st.empty()
        step_texts = ["🔮 만세력 스캐닝", "🌿 오행 분석", "🧴 향수 노트 분석", "💘 궁합 계산 중"]

        render_loading(loading, 1, "만세력을 확인하고 있어요…", 20, step_texts)
        time.sleep(0.2)

        result = get_real_saju_elements(birth_date.year, birth_date.month, birth_date.day, calc_hour, calc_min)
        if result[0] is None:
            loading.empty()
            st.error("사주 계산에 실패했습니다.")
            st.stop()
        saju_name, e_counts, strong, weak, gapja_str = result

        render_loading(loading, 2, "오행 에너지를 분석하고 있어요…", 45, step_texts)
        time.sleep(0.2)

        render_loading(loading, 3, "향수 노트를 찾고 있어요…", 65, step_texts)
        time.sleep(0.1)

        db_row = find_perfume_in_db(df, perf_brand.strip(), perf_name.strip())
        if db_row is not None:
            notes_text = safe_text(db_row.get("Notes", ""))
            notes_source = "db"
        else:
            notes_text = get_perfume_notes_via_ai(perf_brand.strip(), perf_name.strip())
            notes_source = "ai"

        perf_vec = compute_perfume_element_vector(notes_text)

        render_loading(loading, 4, "궁합을 계산하고 있어요…", 85, step_texts, ai_mode=True)
        time.sleep(0.1)

        score = compute_compatibility_score(e_counts, perf_vec, weak, strong)
        compat_result = generate_compatibility_result(
            user_name.strip(), gender, saju_name, strong, weak,
            perf_brand.strip(), perf_name.strip(), notes_text, score, perf_vec
        )

        loading.empty()

        st.session_state.update({
            "step": 2,
            "user_name": user_name.strip(),
            "gender": gender,
            "birth_date": birth_date,
            "know_time": know_time,
            "b_hour": None if know_time else b_hour,
            "b_min": None if know_time else b_min,
            "saju_name": saju_name,
            "e_counts": e_counts,
            "strong": strong,
            "weak": weak,
            "session_id": f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "perf_brand": perf_brand.strip(),
            "perf_name": perf_name.strip(),
            "notes_text": notes_text,
            "notes_source": notes_source,
            "perf_vec": perf_vec,
            "compat_score": score,
            "compat_result": compat_result,
        })
        st.rerun()


# =========================================================
# ✅ STEP 2 — 궁합 결과 화면
# =========================================================
elif st.session_state["step"] == 2:
    s = st.session_state
    score = s["compat_score"]
    cr = s["compat_result"]
    strong, weak = s["strong"], s["weak"]
    perf_vec = s["perf_vec"]

    if score >= 75:
        score_color = "#1e3c72"
        score_emoji = "💘"
    elif score >= 50:
        score_color = "#e67e22"
        score_emoji = "🤔"
    else:
        score_color = "#c0392b"
        score_emoji = "😅"

    st.markdown(f"""
    <div class="hero">
      <div class="hero-sub" style="margin-bottom:6px;">{_html.escape(s['user_name'])}님의 향수 궁합 결과</div>
      <div class="compat-score-wrap">
        <div class="compat-score-num" style="background:linear-gradient(135deg,{score_color},{score_color}CC); -webkit-background-clip:text;">{score_emoji} {score}점</div>
        <div class="compat-score-label">/ 100점</div>
      </div>
      <div class="compat-oneliner">{_html.escape(cr.get('one_liner',''))}</div>
      <div style="text-align:center;">
        <span style="font-size:12px; color:#888; margin-right:6px;">🧴 {_html.escape(s['perf_brand'])} — {_html.escape(s['perf_name'])}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi"><b>내 강한 기운</b><div class="val">{ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}</div></div>
      <div class="kpi"><b>내 부족한 기운</b><div class="val">{ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**💚 잘 맞는 이유**")
        for r in cr.get("good_reasons", []):
            st.markdown(f'<span class="compat-tag tag-good">✔ {_html.escape(r)}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown("**🔴 아쉬운 점**")
        for r in cr.get("bad_reasons", []):
            st.markdown(f'<span class="compat-tag tag-bad">✖ {_html.escape(r)}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🌿 이 향수의 오행 분석 보기"):
        st.markdown(cr.get("perf_element_summary", ""), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        total_v = sum(perf_vec.values()) or 1
        for elem in ELEMENTS:
            val = perf_vec.get(elem, 0.0)
            pct = int(val / total_v * 100) if total_v > 0 else 0
            bar_w = max(4, pct)
            st.markdown(f"""
            <div style="margin-bottom:8px;">
              <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px;">
                <span>{ELEMENT_EMOJI[elem]} {ELEMENTS_KO[elem]}</span>
                <span style="color:#888;">{pct}%</span>
              </div>
              <div style="background:#eef2ff; border-radius:999px; height:8px;">
                <div style="background:linear-gradient(90deg,#1e3c72,#2a5298); width:{bar_w}%; height:8px; border-radius:999px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("💬 궁합 점수 상세 설명"):
        st.markdown(cr.get("compatibility_detail", ""), unsafe_allow_html=True)

    if s.get("notes_source") == "ai":
        st.caption("💡 이 향수는 DB에 없어서 AI가 노트를 추론했어요. 실제와 약간 다를 수 있어요.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 더 잘 맞는 향수가 궁금해? 🤔")
    st.markdown('<p class="small-muted">사주 오행에 딱 맞는 향수 3개를 추천해드릴게요!</p>', unsafe_allow_html=True)

    if st.button("🧴 나에게 맞는 향수 추천받기", use_container_width=True):
        st.session_state["step"] = 3
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 처음으로 돌아가기", use_container_width=False):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# =========================================================
# ✅ STEP 3 — 추천 필터 선택
# =========================================================
elif st.session_state["step"] == 3:
    s = st.session_state
    weak_ko = ELEMENTS_KO.get(s["weak"], s["weak"])

    st.markdown(f'<div class="step-header">🌿 향수 취향 설정</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-sub"><b>{_html.escape(s["user_name"])}</b>님의 부족한 <b>{_html.escape(weak_ko)}</b> 기운을 채울<br>향수를 골라드릴게요!</div>', unsafe_allow_html=True)

    with st.form("step3_form"):
        tag_options = list(TAG_TO_KEYWORDS.keys())
        pref_tags = st.multiselect("💚 끌리는 향 (복수 선택)", tag_options)
        dislike_tags = st.multiselect("🚫 피하고 싶은 향", [t for t in tag_options if t not in pref_tags])

        st.markdown("<hr style='margin:1rem 0; border:none; border-top:1px dashed #ddd;'>", unsafe_allow_html=True)

        gender_filter = st.radio(
            "향수 성향",
            ["전체", "여성향", "남성향", "중성향"],
            horizontal=True,
            index=0
        )
        brand_filter_mode = st.radio(
            "브랜드 범위",
            ["전체 브랜드", "유명 브랜드 위주"],
            horizontal=True,
            index=1
        )

        submit3 = st.form_submit_button("🔮 향수 3개 추천받기")

    if submit3:
        loading = st.empty()
        step_texts = ["🌿 오행 필터 적용", "🧴 향수 매칭", "✍️ 처방전 작성"]

        render_loading(loading, 1, "조건에 맞는 향수를 찾고 있어요…", 30, step_texts)
        time.sleep(0.2)

        calc_hour = s.get("b_hour")
        calc_min = s.get("b_min")

        rec_df = recommend_perfumes(df.copy(), s["weak"], s["strong"], pref_tags, dislike_tags, brand_filter_mode, gender_filter)
        if rec_df.empty or len(rec_df) < 3:
            loading.empty()
            st.error("조건에 맞는 향수가 부족해요. 필터를 줄여주세요.")
            st.stop()
        top3 = rec_df.head(3).copy()

        render_loading(loading, 2, "향수를 고르고 있어요…", 60, step_texts)
        time.sleep(0.2)

        render_loading(loading, 3, "사쥬 마스터가 처방전을 쓰는 중이에요…", 85, step_texts, ai_mode=True)
        time.sleep(0.1)

        reading_result = generate_comprehensive_reading(
            s["user_name"], s["gender"], s["saju_name"], s["strong"], s["weak"], top3, s["know_time"]
        )

        render_loading(loading, 3, "마무리 정리 중이에요…", 100, step_texts)
        time.sleep(0.15)
        loading.empty()

        try:
            save_recommendation_log(
                s["session_id"], s["user_name"], s["gender"], s["birth_date"],
                s["know_time"], s["saju_name"], s["strong"], s["weak"], top3
            )
        except Exception:
            pass

        st.session_state.update({
            "step": 4,
            "top3": top3,
            "reading_result": reading_result,
        })
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 궁합 결과로 돌아가기", use_container_width=False):
        st.session_state["step"] = 2
        st.rerun()


# =========================================================
# ✅ STEP 4 — 추천 결과 (기존 탭 구조)
# =========================================================
elif st.session_state["step"] == 4:
    s = st.session_state
    top3 = s["top3"]
    saju_name = s["saju_name"]
    strong = s["strong"]
    weak = s["weak"]
    know_time = s["know_time"]
    user_name = s["user_name"]
    gender = s["gender"]
    session_id = s["session_id"]
    reading_result = s.get("reading_result", "") or ""

    survey_url = f"{SURVEY_BASE_URL}{urllib.parse.quote(session_id)}"
    app_link = "[https://fate-scent-mvp.streamlit.app/](https://fate-scent-mvp.streamlit.app/)"

    st.markdown(f"### {_html.escape(user_name)}님의 향수 추천 결과")

    hero_text = ""
    m = re.search(r"<h2[^>]*>(.*?)</h2>", reading_result, flags=re.S | re.I)
    if m:
        hero_text = re.sub(r"<[^>]+>", "", m.group(1))
        hero_text = _html.unescape(hero_text).strip()
    
    # 🚨 [수정 완료] 큰따옴표 안의 큰따옴표로 인한 Syntax Error 해결
    if not hero_text:
        hero_text = f"{ELEMENTS_KO.get(strong,strong)} — '당신의 흐름은 분명합니다.'"

    time_line = "⏰ 태어난 시간이 입력되었습니다." if not know_time else "⏰ 시간 미입력: 정오 기준(오차 가능)으로 분석했어요."

    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">{_html.escape(hero_text)}</div>
      <div class="hero-sub">{_html.escape(time_line)}</div>
      <div class="kpi-row">
        <div class="kpi"><b>가장 강한 기운</b><div class="val">{ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}</div></div>
        <div class="kpi"><b>보완할 기운</b><div class="val">{ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}</div></div>
      </div>
      <div class="small-note" style="margin-top:10px;">원하는 것만 빠르게 볼 수 있게 <b>탭</b>으로 나눴어요.</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["✨ 요약", "📜 사주풀이(자세히)", "🧴 향수 Top3", "🥺 사쥬!!!(공유)"])

    # --- 요약 탭 ---
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"**핵심 요약**: 지금은 **{ELEMENTS_KO[weak]}** 기운을 채우는 향이 가장 잘 맞아요.")
        st.markdown("부족한 기운을 향으로 보완하면, 컨디션/결정/관계 흐름이 더 안정적으로 잡히는 데 도움이 될 수 있어요.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 🧴 Top 3 추천 (빠르게 보기)")
        for i, (_, row) in enumerate(top3.iterrows()):
            b_name = safe_text(row.get("Brand"))
            p_name = safe_text(row.get("Name"))
            notes_raw = safe_text(row.get("Notes", ""))
            notes_ko = notes_to_korean_summary(notes_raw)
            matched = extract_matching_notes(row, weak, top_n=3)
            reason = build_east_asian_note_reason(weak, matched)
            badges = " ".join([f"<span class='badge'>{x}</span>" for x in get_element_vector_badges(row)])
            st.markdown(f"""
            <div class="section-card">
              <div style="font-weight:800;">{['🥇','🥈','🥉'][i]} {_html.escape(b_name)} - {_html.escape(p_name)}</div>
              <div style="margin-top:6px;">{badges}</div>
              <div class="small-muted" style="margin-top:8px;"><b>향 느낌:</b> {_html.escape(notes_ko)}</div>
              <div class="small-muted" style="margin-top:6px;"><b>이유:</b> {reason}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🚀 다음 액션")
        row0 = top3.iloc[0]
        b0, n0 = safe_text(row0.get("Brand")), safe_text(row0.get("Name"))
        naver0 = f"[https://search.shopping.naver.com/search/all?query=](https://search.shopping.naver.com/search/all?query=){urllib.parse.quote(f'{b0} {n0} 향수')}"
        st.link_button("🥇 1위 향수 시향 검색하기", naver0, use_container_width=True)

    # --- 사주풀이 탭 ---
    with tab2:
        magazine_css = """
        <style>
        .saju-magazine { font-size:15px; line-height:1.8; color:#444444; letter-spacing:-0.5px; padding:10px 5px; word-break:keep-all; }
        .saju-magazine h3 { color:#1e3c72; font-weight:800; font-size:18px; margin-top:35px; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid #eef2ff; }
        .saju-magazine strong { color:#1e3c72; font-weight:700; background:linear-gradient(to top, #e8f0fe 35%, transparent 35%); padding:0 2px; }
        .saju-magazine ul { list-style:none; padding-left:10px; }
        .saju-magazine ul li { position:relative; padding-left:18px; margin-bottom:8px; }
        .saju-magazine ul li::before { content:"✨"; position:absolute; left:0; top:2px; font-size:12px; }
        </style>
        """
        st.markdown(magazine_css, unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        reading_body = re.sub(r"<h2[^>]*>.*?</h2>", "", reading_result, flags=re.S | re.I)
        st.markdown(f'<div class="saju-magazine">\n{reading_body}\n</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 향수 Top3 탭 ---
    with tab3:
        st.markdown("### 🛍️ 추천 향수 시향해보기")
        for i, (_, row) in enumerate(top3.iterrows()):
            b_name = safe_text(row.get("Brand"))
            p_name = safe_text(row.get("Name"))
            naver_url = f"[https://search.shopping.naver.com/search/all?query=](https://search.shopping.naver.com/search/all?query=){urllib.parse.quote(f'{b_name} {p_name} 향수')}"
            st.link_button(f"{['🥇','🥈','🥉'][i]} {b_name} - {p_name} 검색하기", naver_url, use_container_width=True)
        st.info("Tip) 가장 끌리는 1개만 먼저 시향해도 충분해요. '첫인상'이 맞는지 체크해보세요!")

    # --- 공유 탭 ---
    with tab4:
        st.markdown("### 📸 인스타에 박제")
        st.info("아래 **'송금 요청서'**를 캡처해서 스토리에 올리고 친구/애인을 태그해보세요! 💸")

        row0 = top3.iloc[0]
        best_brand = safe_text(row0.get("Brand"))
        best_name = safe_text(row0.get("Name"))

        qr_img_b64 = ""
        try:
            import qrcode
            import base64
            qr = qrcode.QRCode(box_size=4, border=0)
            qr.add_data(app_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#3182f6", back_color="transparent")
            buf = BytesIO()
            img.save(buf, format="PNG")
            qr_img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            qr_img_b64 = ""

        qr_block = ""
        if qr_img_b64:
            qr_block = f'<div style="display:flex; justify-content:space-between; align-items:center; background:#f2f4f6; border-radius:16px; padding:16px; margin-top:24px;"><div style="text-align:left; line-height:1.4;"><div style="font-size:13px; font-weight:800; color:#3182f6;">나도 운명 향수 찾기</div><div style="font-size:12px; font-weight:600; color:#4e5968;">QR 스캔하고 테스트하기</div></div><img src="data:image/png;base64,{qr_img_b64}" style="width:44px; height:44px; border-radius:8px;" /></div>'

        toss_ui_html = f"""
<div style="background-color:#f9fafb; padding:20px; border-radius:24px; display:flex; justify-content:center;">
<div style="background:#ffffff; border-radius:24px; padding:32px 24px; text-align:center; width:100%; max-width:340px; box-shadow:0 4px 20px rgba(0,0,0,0.04); position:relative;">
<div style="width:56px; height:56px; background:#e8f3ff; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:28px; margin:0 auto 16px auto;">💸</div>
<div style="font-size:18px; font-weight:800; color:#191f28; line-height:1.4; margin-bottom:8px;"><span style="color:#3182f6;">{_html.escape(user_name)}</span>님이<br>결제를 요청했어요</div>
<div style="font-size:22px; font-weight:900; color:#191f28; margin:24px 0 6px 0;">{_html.escape(best_brand)}</div>
<div style="font-size:15px; font-weight:600; color:#4e5968; margin-bottom:24px;">{_html.escape(best_name)}</div>
<div style="background:#f2f4f6; border-radius:16px; padding:16px; text-align:left; margin-bottom:24px;">
<div style="font-size:12px; font-weight:700; color:#8b95a1; margin-bottom:6px;">요청 사유</div>
<div style="font-size:14px; font-weight:700; color:#333d4b; line-height:1.5;">내 사주에 <b>{ELEMENTS_KO[weak]}</b> 기운이 부족하대요.<br>나 이거 안 뿌리면 진짜 큰일남 🥺 사쥬!!!</div>
</div>
<div style="display:flex; flex-direction:column; gap:8px;">
<div style="background:#3182f6; color:#ffffff; font-size:15px; font-weight:800; padding:16px; border-radius:16px;">쿨하게 결제해주기</div>
<div style="background:#f2f4f6; color:#4e5968; font-size:15px; font-weight:700; padding:16px; border-radius:16px;">쌩까기 (위험)</div>
</div>
{qr_block}
</div>
</div>"""
        st.markdown(toss_ui_html, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📝 서비스 개선에 참여하기")
        st.info("결과가 맘에 드셨다면 1분 설문 부탁드려요! 여러분의 피드백이 다음 업데이트에 바로 반영됩니다.")
        st.link_button("📝 1분 설문 참여하기 (세션ID 자동입력)", survey_url, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 처음부터 다시 하기", use_container_width=False):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# =========================================================
# 11) 관리자용 로그
# =========================================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
with st.expander("🔐 [관리자용] 추천 로그 데이터 확인"):
    admin_pw = st.text_input("관리자 암호를 입력하세요", type="password")
    if admin_pw == "saju1234":
        st.success("인증 완료!")
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "rb") as f:
                st.download_button(
                    label="📥 누적 추천 로그 CSV 다운로드",
                    data=f, file_name="recommendation_logs.csv", mime="text/csv"
                )
        else:
            st.write("아직 저장된 로그가 없습니다.")
    elif admin_pw != "":
        st.error("비밀번호가 틀렸습니다.")
