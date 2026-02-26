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
from PIL import Image, ImageDraw, ImageFont
import textwrap

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
/* 트렌디한 폰트 '프리텐다드' 적용 */
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
.small-muted {
    font-size: 12px;
    color: #666;
}

/* ===== 결과 화면 UI 업그레이드(탭 + 히어로) ===== */
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
.hero-sub {
  text-align:center;
  color:#666;
  font-size: 12px;
  line-height:1.5;
}
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

.section-card{
  border: 1px solid #eee;
  border-radius: 14px;
  padding: 12px;
  background:#fff;
  margin-bottom: 12px;
}
.small-note { font-size: 12px; color:#777; line-height:1.55; }
div[data-baseweb="tab-panel"] { padding-top: 10px; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 1) 경로 / 상수 / OpenAI 설정
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(base_dir, "processed_perfumes_fixed_0223.csv")
LOG_PATH = os.path.join(base_dir, "recommendation_logs.csv")
CLICK_LOG_PATH = os.path.join(base_dir, "recommendation_click_logs.csv")

# ✅ 구글폼 프리필 링크 (entry.xxxxx= 까지 포함)
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

WEAK_MEME = {
    "Wood": {
        "title": "생기 0% 🌱",
        "lines": ["의욕이 갑자기 로그아웃됨", "새로운 시작 버튼이 안 눌림", "계획만 세우고 누워버림"],
    },
    "Fire": {
        "title": "텐션 0% 🔥",
        "lines": ["웃음 버튼이 고장남", "말수가 줄고 조용해짐", "추진력 배터리 방전"],
    },
    "Earth": {
        "title": "안정 0% 🪨",
        "lines": ["마음이 붕 떠있는 느낌", "컨디션이 널뛰기함", "꾸준함이 증발함"],
    },
    "Metal": {
        "title": "정리/결단 0% ⚙️",
        "lines": ["결정이 자꾸 미뤄짐", "기준이 흔들려 후회함", "정리정돈이 안 됨(현기증)"],
    },
    "Water": {
        "title": "여유/감성 0% 💧",
        "lines": ["마음이 바짝 마름", "여유가 없고 예민해짐", "감정 정리가 어려움"],
    },
}
def _safe_font(size=36, bold=False):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(name, size)
    except Exception:
        return ImageFont.load_default()

def _draw_wrapped(draw, text, xy, font, fill, max_width, line_spacing=8):
    x, y = xy
    wrapped = textwrap.fill(text, width=max(10, int(max_width / (font.size * 0.55))))
    for line in wrapped.split("\n"):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing
    return y

def make_meme_card_png(
    user_name: str,
    strong: str,
    weak: str,
    best_brand: str,
    best_name: str,
    app_link: str,
    hero_text: str = "",
    size=(1080, 1920),
):
    W, H = size
    img = Image.new("RGB", size, (244, 245, 247))
    draw = ImageDraw.Draw(img)

    f_title = _safe_font(62, bold=True)
    f_sub = _safe_font(34, bold=False)
    f_badge = _safe_font(30, bold=True)
    f_body = _safe_font(34, bold=False)
    f_small = _safe_font(26, bold=False)

    draw.text((W//2, 90), "향수 사쥬!!!", font=f_title, fill=(30, 60, 114), anchor="mm")
    if hero_text:
        draw.text((W//2, 160), hero_text, font=f_sub, fill=(90, 90, 90), anchor="mm")
    else:
        draw.text((W//2, 160), "부족한 기운을 채워주는 향수 처방", font=f_sub, fill=(90, 90, 90), anchor="mm")

    pad = 70
    card_x1, card_y1 = pad, 240
    card_x2, card_y2 = W - pad, 1520
    draw.rounded_rectangle((card_x1, card_y1, card_x2, card_y2), radius=40, fill=(255, 255, 255), outline=(235, 238, 245), width=4)

    def badge(x, y, text):
        tw = draw.textlength(text, font=f_badge)
        bw = int(tw) + 44
        bh = 58
        draw.rounded_rectangle((x, y, x + bw, y + bh), radius=999, fill=(250, 250, 252), outline=(225, 228, 235), width=3)
        draw.text((x + bw/2, y + bh/2), text, font=f_badge, fill=(40, 40, 40), anchor="mm")

    badge(card_x1 + 40, card_y1 + 40, f"강한 기운: {ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}")
    badge(card_x1 + 40, card_y1 + 120, f"부족 기운: {ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}")

    meme = WEAK_MEME.get(weak, {"title": "충전 필요", "lines": ["오늘은 충전이 필요해요", "기운을 채워볼게요", ""]})
    y = card_y1 + 220
    draw.text((card_x1 + 40, y), f"📌 오늘의 상태: {meme['title']}", font=_safe_font(40, bold=True), fill=(30, 60, 114))
    y += 70
    for line in meme["lines"][:3]:
        draw.text((card_x1 + 60, y), f"• {line}", font=f_body, fill=(60, 60, 60))
        y += 52

    y += 35
    draw.line((card_x1 + 40, y, card_x2 - 40, y), fill=(235, 238, 245), width=4)
    y += 35

    draw.text((card_x1 + 40, y), "🥇 오늘의 처방 TOP 1", font=_safe_font(38, bold=True), fill=(231, 76, 60))
    y += 70

    draw.text((card_x1 + 40, y), best_brand, font=_safe_font(52, bold=True), fill=(30, 60, 114))
    y += 72
    y = _draw_wrapped(draw, best_name, (card_x1 + 40, y), font=_safe_font(44, bold=True), fill=(50, 50, 50),
                      max_width=(card_x2 - card_x1 - 80), line_spacing=10)
    y += 30

    why_line = f"👉 {ELEMENTS_KO[weak]} 기운 긴급 충전템"
    y = _draw_wrapped(draw, why_line, (card_x1 + 40, y), font=f_body, fill=(80, 80, 80),
                      max_width=(card_x2 - card_x1 - 80), line_spacing=8)

    y_qr_top = card_y2 - 290
    draw.line((card_x1 + 40, y_qr_top - 25, card_x2 - 40, y_qr_top - 25), fill=(235, 238, 245), width=4)

    qr_ok = False
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=8, border=1)
        qr.add_data(app_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((220, 220))
        img.paste(qr_img, (card_x1 + 40, y_qr_top))
        qr_ok = True
    except Exception:
        qr_ok = False

    cta_x = card_x1 + (300 if qr_ok else 40)
    draw.text((cta_x, y_qr_top + 10), "📲 나도 해보기", font=_safe_font(38, bold=True), fill=(30, 60, 114))
    draw.text((cta_x, y_qr_top + 70), "QR 찍거나 아래 링크로!", font=f_small, fill=(100, 100, 100))

    show_link = app_link
    if len(show_link) > 42:
        show_link = show_link[:39] + "..."
    draw.text((cta_x, y_qr_top + 115), show_link, font=_safe_font(28, bold=False), fill=(60, 60, 60))

    draw.text((W//2, H - 70), "Fate Scent / 향수 사쥬!!!", font=_safe_font(24, bold=False), fill=(140, 140, 140), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ✅ 요약 탭용: 영어 Notes → 한글 요약(룰 기반)
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
    hits = list(dict.fromkeys(hits))  # 중복 제거

    if not hits:
        return "은은하고 부드러운 데일리 향"
    return " · ".join(hits[:3])

# ✅ 요약 탭용: 부족 기운을 채우는 이유(짧은 동양학 톤)
def build_east_asian_note_reason(weak_element: str, matched_notes: list[str]) -> str:
    weak_ko = ELEMENTS_KO.get(weak_element, weak_element)
    lore = {
        "Wood": "예부터 목(木)은 ‘성장·확장·생기’로 보았어요. 초록/허브/우디 계열은 새싹이 돋는 느낌처럼 목의 흐름을 깨워주는 향으로 자주 비유됩니다.",
        "Fire": "화(火)는 ‘활력·온기·표현’과 연결돼요. 시트러스/스파이시처럼 밝고 톡 튀는 향은 기운을 위로 끌어올려 화의 생동감을 살리는 쪽으로 해석됩니다.",
        "Earth": "토(土)는 ‘안정·중심·포용’의 이미지예요. 머스크/앰버/바닐라처럼 포근하고 감싸는 향은 마음을 붙잡아 주는 토의 성질과 잘 맞는다고 봅니다.",
        "Metal": "금(金)은 ‘정리·기준·결단’의 이미지가 강해요. 클린/비누/미네랄/민트 계열은 군더더기를 덜어내는 느낌이라 금의 또렷함을 돋운다고 해석합니다.",
        "Water": "수(水)는 ‘유연·깊이·흐름’이에요. 아쿠아/마린/오존 계열은 물의 결을 떠올리게 해서 수의 흐름을 자연스럽게 살린다고 봅니다.",
    }

    if matched_notes:
        notes_ko = ", ".join(matched_notes[:3])
        return f"당신의 부족한 <b>{weak_ko}</b> 기운을 <b>{notes_ko}</b> 계열 노트가 채워주는 방향이에요. {lore.get(weak_element, '')}"
    return f"당신의 부족한 <b>{weak_ko}</b> 기운을 채우는 데 도움이 되는 계열로 추천됐어요. {lore.get(weak_element, '')}"


# =========================================================
# 3) 실제 만세력 기반 사주 계산
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
# 4) AI 풀이 생성 (Fallback 포함) - ✅사주 파트 강화
# =========================================================
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
        if know_time else
        "사용자는 태어난 시간을 입력했음."
    )

    prompt = f"""
너는 '명리학 + 조향'을 연결해 설명하는 전문가야.
결과는 **오직 HTML로만** 작성해. 마크다운(###, **, -) 절대 금지. 코드블록 ``` 절대 금지.

[고객]
- 이름: {user_name}
- 성별: {gender} (문체: {gender_tone})
- 사주 표기: {saju_name}
- 가장 강한 기운: {strong_ko}
- 보완이 필요한 기운: {weak_ko}
- 조건: {time_notice}

[추천 향수 Top3]
1) {safe_text(p1.get("Brand",""))} - {safe_text(p1.get("Name",""))} / Notes: {safe_text(p1.get("Notes","정보 없음"))}
2) {safe_text(p2.get("Brand",""))} - {safe_text(p2.get("Name",""))} / Notes: {safe_text(p2.get("Notes","정보 없음"))}
3) {safe_text(p3.get("Brand",""))} - {safe_text(p3.get("Name",""))} / Notes: {safe_text(p3.get("Notes","정보 없음"))}

[작성 규칙]
- 초등학생도 이해할 말로 쓰되, 구조는 “전문가처럼 체계적으로”.
- 사주 파트는 충분히 길게(사용자가 ‘제대로 분석 받았다’ 느낌).
- 각 큰 섹션에는 최소 1개 “현실 예시(상황)” 포함.
- 점술처럼 단정 금지: “~할 수 있어요 / 도움이 될 수 있어요”.
- 반드시 아래 HTML 템플릿 구조를 지켜라.

[HTML 출력 템플릿]
<h2 style="color:#1e3c72; text-align:center; font-size:1.6rem; padding: 10px 0; margin: 6px 0 10px 0;">(한 단어) — “(한 줄 비유 1문장)”</h2>
<div style="text-align:center; font-size:0.95rem; color:#555; margin-bottom: 12px;">강한 기운: {strong_ko} / 보완 기운: {weak_ko}</div>
<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">(시간 안내 1줄)</div>

<h3 style="margin:14px 0 8px 0;">📜 사주 및 오행 분석</h3>
<div style="color:#333; line-height:1.75;">
  <div style="margin-bottom:12px;"><b>1) 강한 기운의 장점</b><br>(3~4문장 + 현실 예시 1개)</div>
  <div style="margin-bottom:12px;"><b>2) 강한 기운이 과할 때 주의점</b><br>(3문장 + 트리거→반응→결과 예시 1개)</div>
  <div style="margin-bottom:12px;"><b>3) 부족 기운이 부족할 때 나타나는 신호</b><br>(3~4문장 + 생활 신호 예시 1개)</div>
  <div style="margin-bottom:12px;"><b>4) 부족 기운을 채우면 생기는 균형</b><br>(3~4문장 + 바뀌는 장면 예시 1개)</div>
  <div style="margin-bottom:12px;"><b>5) 잘 풀리는 환경/관계 스타일</b><br>(3문장 + 잘 맞는 일/관계 방식 1개)</div>
</div>

<h3 style="margin:14px 0 8px 0;">✅ 지금 상태 체크(해당되면 {weak_ko} 보완이 특히 도움될 수 있어요)</h3>
<ul style="line-height:1.75; color:#333;">
  <li>(체크 1)</li><li>(체크 2)</li><li>(체크 3)</li>
</ul>

<h3 style="margin:14px 0 8px 0;">🔑 당신에게 꼭 필요한 기운: {weak_ko}</h3>
<div style="color:#333; line-height:1.75;">(3~4문장 + 쉬운 정의 + 현실 예시 1개)</div>

<h3 style="margin:14px 0 8px 0;">🧩 {weak_ko} 보완 루틴(향 말고 ‘행동’으로도 바로 효과 보기)</h3>
<ol style="line-height:1.75; color:#333;"><li>...</li><li>...</li><li>...</li></ol>

<h3 style="margin:14px 0 8px 0;">💖 향기로 운을 틔웠을 때의 변화</h3>
<ul style="line-height:1.8; color:#333;">
  <li><b>💰 재물운:</b> (3~4문장: {weak_ko}→행동 변화→돈 흐름)</li>
  <li><b>💕 연애운:</b> (3~4문장: {weak_ko}→무드/대화→관계)</li>
  <li><b>🤝 인간관계:</b> (3~4문장: {weak_ko}→소통/거리감→협업)</li>
</ul>
<div style="font-size:0.92rem; color:#2a5298; margin: 6px 0 12px 0;"><b>이 부족한 {weak_ko} 기운은, 아래 향수들을 통해 일상에서 자연스럽게 보완할 수 있어요.</b></div>

<hr style="border:none; border-top:1px solid #eee; margin: 12px 0;">

<h3 style="margin:14px 0 8px 0;">🧴 맞춤 향수 처방전 (Top 3)</h3>
<div style="border:1px solid #eee; border-radius:12px; padding:12px; margin-bottom:10px;">
  <div style="font-weight:800;">🥇 1위. (브랜드 - 향수명)</div>
  <div style="margin-top:6px;"><b>한줄 이미지:</b> ...</div>
  <div style="margin-top:6px;"><b>향기 노트:</b> ...</div>
  <div style="margin-top:6px;"><b>왜 {weak_ko} 기운을 채우나:</b> ...</div>
  <div style="margin-top:6px;"><b>기대 효과:</b> ...</div>
</div>
(🥈 2위 카드도 동일)
(🥉 3위 카드도 동일)

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
        '<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">'
        '⏰ 태어난 시간을 모른다고 선택하셔서, <b>정오 기준(오차 가능)</b>으로 연/월/일 6글자 중심 풀이예요.'
        '</div>'
        if know_time else
        '<div style="font-size:0.85rem; color:#666; margin-bottom: 12px;">'
        '⏰ 태어난 시간까지 반영해서 8글자 기준으로 풀이했어요.'
        '</div>'
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
          <div style="margin-top:6px;"><b>한줄 이미지:</b> {weak_ko} 기운을 부드럽게 채워주는 ‘무드 보정’ 향이에요.</div>
          <div style="margin-top:6px;"><b>향기 노트:</b> {notes}</div>
          <div style="margin-top:6px;"><b>왜 {weak_ko} 기운을 채우나:</b> 이 향의 핵심 노트가 {weak_ko}의 이미지(정리/안정/균형)에 닿아 있어요.</div>
          <div style="margin-top:6px;"><b>기대 효과:</b> 기분이 정돈되고, 선택이 또렷해질 수 있어요.</div>
        </div>
        """

    html = f"""
<h2 style="color:#1e3c72; text-align:center; font-size:1.6rem; padding: 10px 0; margin: 6px 0 10px 0;">{one_word} — “{one_line}”</h2>
<div style="text-align:center; font-size:0.95rem; color:#555; margin-bottom: 12px;">강한 기운: {strong_ko} / 보완 기운: {weak_ko}</div>
{time_notice_html}

<h3 style="margin:14px 0 8px 0;">📜 사주 및 오행 분석</h3>
<div style="color:#333; line-height:1.75;">
  <div style="margin-bottom:12px;"><b>1) 강한 기운의 장점</b><br>
  강한 기운이 뚜렷하면 분위기와 선택 기준이 분명해지는 편이에요. 예: 대화에서 핵심을 빨리 잡는 타입일 수 있어요.
  </div>
  <div style="margin-bottom:12px;"><b>2) 강한 기운이 과할 때 주의점</b><br>
  피곤할 때 생각이 많아져 결정을 미루고 기회를 놓칠 수 있어요.
  </div>
  <div style="margin-bottom:12px;"><b>3) 부족 기운이 부족할 때 나타나는 신호</b><br>
  {weak_ko}가 부족하면 정리/기준/결정이 늦어지고 관계의 선 긋기가 어려울 수 있어요.
  </div>
  <div style="margin-bottom:12px;"><b>4) 부족 기운을 채우면 생기는 균형</b><br>
  마음은 부드럽고, 행동은 또렷해지는 쪽으로 균형이 잡힐 수 있어요.
  </div>
  <div style="margin-bottom:12px;"><b>5) 잘 풀리는 환경/관계 스타일</b><br>
  역할과 기준이 명확한 환경에서 강점을 더 잘 발휘할 수 있어요.
  </div>
</div>

<h3 style="margin:14px 0 8px 0;">🧴 맞춤 향수 처방전 (Top 3)</h3>
{cards_html}

<hr style="border:none; border-top:1px solid #eee; margin: 12px 0;">

<h3 style="margin:14px 0 8px 0;">🍀 깨알 재미 요소</h3>
<ul style="line-height:1.8; color:#333;">
  <li><b>🎨 나와 잘 맞는 색깔:</b> {colors[0]}, {colors[1]}</li>
  <li><b>📍 나와 잘 맞는 장소:</b> {places[0]}, {places[1]}</li>
</ul>
"""
    return html.strip()

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

        # 형식 깨짐 방지
        if "<h2" not in out or "<h3" not in out:
            return generate_local_fallback_reading(user_name, gender, saju_name, strongest, weakest, top3_df, know_time)
        return out
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
            "timestamp": now_str,
            "session_id": session_id,
            "user_name": user_name,
            "gender": gender,
            "birth_date": str(birth_date),
            "know_time": 0 if know_time else 1,  # (기존 코드 유지)
            "saju_name": saju_name,
            "strongest_element": strongest,
            "weakest_element": weakest,
            "rank": rank_idx,
            "perfume_name": safe_text(row.get("Name", "")),
            "brand": safe_text(row.get("Brand", "")),
            "rec_score": float(row.get("score", 0.0))
        })
    df_log = pd.DataFrame(rows)
    df_log.to_csv(
        LOG_PATH,
        mode="a" if os.path.exists(LOG_PATH) else "w",
        header=not os.path.exists(LOG_PATH),
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# 6) 데이터 로드 및 추천 엔진
# =========================================================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)

    for c in ["Name", "Brand", "Notes", "Description", "matched_keywords"]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    for e in ELEMENTS:
        if e not in df.columns:
            df[e] = 0.0
        df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)

    df["all_text"] = (df["Name"] + " " + df["Brand"] + " " + df["Notes"] + " " + df["matched_keywords"]).str.lower()
    df["element_sum"] = df[ELEMENTS].sum(axis=1)
    df = df[df["element_sum"] > 0].copy()

    mask = ~df["Name"].str.lower().apply(lambda x: any(w in x for w in ["sample", "discovery", "set", "gift", "miniature"]))
    return df[mask].reset_index(drop=True)

df = load_data()

def recommend_perfumes(df, weakest, strongest, pref_tags, dislike_tags, brand_filter_mode):
    if df.empty:
        return pd.DataFrame()

    work = df.copy()

    if brand_filter_mode == "유명 브랜드 위주":
        work = work[work["Brand"].apply(lambda b: any(f.lower() in str(b).lower() for f in FAMOUS_BRANDS))].copy()
        if len(work) < 20:
            work = df.copy()

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
        if dislike_score >= 0.4:
            final_score -= 0.5

        r = row.to_dict()
        r.update({"score": final_score, f"{weakest}_fill": float(row.get(weakest, 0.0))})
        rows.append(r)

    out = pd.DataFrame(rows).sort_values("score", ascending=False).drop_duplicates(subset=["Name"]).reset_index(drop=True)
    return out


# =========================================================
# 7) 메인 화면 UI
# =========================================================
st.markdown("<h1>🥺 이 향수 사쥬!!</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">내 사주 오행에 딱 맞는 운명적인 향수,<br>나 이거 사주면 안돼? (당당)</div>', unsafe_allow_html=True)

if df.empty:
    st.error("향수 데이터베이스를 불러오지 못했습니다.")
    st.stop()

with st.form("saju_form"):
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

    tag_options = list(TAG_TO_KEYWORDS.keys())
    pref_tags = st.multiselect("끌리는 향 (복수 선택)", tag_options)
    dislike_tags = st.multiselect("피하고 싶은 향", [t for t in tag_options if t not in pref_tags])
    brand_filter_mode = st.radio("브랜드 범위", ["전체 브랜드", "유명 브랜드 위주"], horizontal=True, index=1)

    submit = st.form_submit_button("향수 처방 받기")


# =========================================================
# 8) 분석 및 결과 (✅ 진행률 느낌 + 깔끔한 로딩 + AI까지 한 흐름)
# =========================================================
if submit:
    if not user_name.strip():
        st.warning("이름(또는 닉네임)을 입력해주세요.")
        st.stop()

    session_id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    calc_hour = None if know_time else b_hour
    calc_min = None if know_time else b_min

    loading = st.empty()

    # ✅ 로딩용 CSS (들여쓰기 무시하고 왼쪽 끝에 배치해야 코드블록으로 인식 안 됨)
    loading_css = """
<style>
@keyframes pulse-text { 0% {opacity:1;} 50% {opacity:0.45;} 100% {opacity:1;} }
@keyframes spin-icon  { 0% {transform:rotate(0deg);} 100% {transform:rotate(360deg);} }
@keyframes move-bar   { 0% {transform:translateX(-60%);} 100% {transform:translateX(160%);} }

.loading-box{
  border:1px solid #e7ecff; border-radius:18px;
  padding:16px 14px; background:linear-gradient(135deg,#eef4ff 0%,#ffffff 55%,#f7f7ff 100%);
}
.loading-title{ text-align:center; color:#1e3c72; font-weight:850; margin:6px 0 10px 0; }
.loading-sub{ text-align:center; font-size:13px; color:#666; line-height:1.5; margin-top:8px; }
.loading-spin{ display:inline-block; animation:spin-icon 1.1s linear infinite; margin-right:6px; }
.loading-pulse{ animation:pulse-text 1.6s infinite ease-in-out; }

.progress-wrap{
  height:10px; border-radius:999px; background:#eef2ff; overflow:hidden;
  border:1px solid #e7ecff; margin:10px 0 8px 0;
}
.progress-fill{
  height:100%; border-radius:999px; width:100%; /* 파이썬에서 width를 주입할 것임 */
  background:linear-gradient(90deg,#1e3c72 0%,#2a5298 100%);
  transition:width 0.35s ease;
}
/* AI 단계에서 '진짜로 움직이는 느낌' 주는 바(불확정 진행률) */
.indeterminate{
  position:relative; height:10px; border-radius:999px; background:#eef2ff; overflow:hidden;
  border:1px solid #e7ecff; margin:10px 0 8px 0;
}
.indeterminate:before{
  content:""; position:absolute; top:0; left:0; height:100%; width:40%;
  background:linear-gradient(90deg, rgba(30,60,114,0) 0%, rgba(42,82,152,0.8) 50%, rgba(30,60,114,0) 100%);
  animation:move-bar 1.1s infinite linear;
}

.step-list{ margin:10px 0 0 0; padding:0; list-style:none; }
.step-item{ font-size:13px; color:#555; padding:4px 0; }
.step-done{ color:#2a5298; font-weight:700; }
.step-now{ color:#1e3c72; font-weight:850; }
.step-wait{ color:#888; }
</style>
"""

    def render_loading(current_step: int, title: str, percent: int, ai_mode: bool = False):
        step_texts = [
            "🔮 만세력 스캐닝",
            "🌿 오행 분석",
            "🧴 향수 매칭",
            "✍️ 사쥬 처방전 작성",
        ]

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
            "<div class='indeterminate'></div>"
            if ai_mode else
            f"<div class='progress-wrap'><div class='progress-fill' style='width:{percent}%;'></div></div>"
        )

        # 🚨 HTML 주입 부분. 들여쓰기 없이 왼쪽 벽에 딱 붙여야 렌더링이 깨지지 않음
        loading.markdown(f"""
{loading_css}
<div class="loading-box">
  <div class="loading-title loading-pulse">
    <span class="loading-spin">⏳</span>{title}
  </div>
  {bar_html}
  <ul class="step-list">
{steps_html}
  </ul>
  <div class="loading-sub">
    새로고침하지 말고 잠시만 기다려주세요 🙏
  </div>
</div>
""", unsafe_allow_html=True)

    # 1) 만세력 스캐닝
    render_loading(current_step=1, title="만세력을 확인하고 있어요…", percent=20, ai_mode=False)
    time.sleep(0.25)

    result = get_real_saju_elements(birth_date.year, birth_date.month, birth_date.day, calc_hour, calc_min)
    if result[0] is None:
        loading.empty()
        st.error("사주 계산에 실패했습니다.")
        st.stop()
    saju_name, e_counts, strong, weak, gapja_str = result

    # 2) 오행 분석
    render_loading(current_step=2, title="오행 에너지를 분석하고 있어요…", percent=45, ai_mode=False)
    time.sleep(0.25)

    # 3) 향수 매칭
    render_loading(current_step=3, title="부족한 기운을 채울 향을 고르는 중이에요…", percent=70, ai_mode=False)
    time.sleep(0.25)

    rec_df = recommend_perfumes(df.copy(), weak, strong, pref_tags, dislike_tags, brand_filter_mode)
    if rec_df.empty or len(rec_df) < 3:
        loading.empty()
        st.error("조건에 맞는 향수가 부족해요. 필터를 줄여주세요.")
        st.stop()
    top3 = rec_df.head(3).copy()

    # 4) AI 처방전 작성 (불확정 진행 바 + '진행 중' 느낌)
    render_loading(current_step=4, title="사쥬 마스터가 처방전을 쓰는 중이에요…", percent=90, ai_mode=True)
    time.sleep(0.1)  # 화면 먼저 그려지게 하는 작은 트릭

    reading_result = generate_comprehensive_reading(user_name.strip(), gender, saju_name, strong, weak, top3, know_time)

    # 완료 느낌(잠깐 95% 찍고 종료)
    render_loading(current_step=4, title="마무리 정리 중이에요…", percent=100, ai_mode=False)
    time.sleep(0.15)

    # 로딩 종료
    loading.empty()

    # 로그 저장
    try:
        save_recommendation_log(session_id, user_name.strip(), gender, birth_date, know_time, saju_name, strong, weak, top3)
    except Exception:
        pass

    # 세션 저장
    st.session_state.update({
        "top3": top3,
        "saju_name": saju_name,
        "e_counts": e_counts,
        "strong": strong,
        "weak": weak,
        "gender": gender,
        "know_time": know_time,
        "session_id": session_id,
        "user_name": user_name.strip(),
        "reading_result": reading_result
    })

# =========================================================
# ✅ 결과 렌더링 (탭 + 히어로 카드 + 바이럴 공유)
# =========================================================
if "top3" in st.session_state:
    top3 = st.session_state["top3"]
    saju_name = st.session_state["saju_name"]
    strong = st.session_state["strong"]
    weak = st.session_state["weak"]
    know_time = st.session_state["know_time"]
    user_name = st.session_state["user_name"]
    gender = st.session_state["gender"]
    session_id = st.session_state["session_id"]
    reading_result = st.session_state.get("reading_result", "") or ""

    st.markdown(f"### {user_name}님의 향수 사쥬 결과")

    # Hero 문장: AI 결과의 <h2> 내용 추출
    hero_text = ""
    m = re.search(r"<h2[^>]*>(.*?)</h2>", reading_result, flags=re.S | re.I)
    if m:
        hero_text = re.sub(r"<[^>]+>", "", m.group(1))
        hero_text = _html.unescape(hero_text).strip()
    if not hero_text:
        hero_text = f"{ELEMENTS_KO.get(strong,strong)} — “당신의 흐름은 분명합니다.”"

    time_line = "⏰ 태어난 시간이 입력되었습니다." if not know_time else "⏰ 시간 미입력: 정오 기준(오차 가능)으로 분석했어요."
    survey_url = f"{SURVEY_BASE_URL}{urllib.parse.quote(session_id)}"
    app_link = "https://your-perfume-saju-link.streamlit.app" # 🚨 네 실제 앱 링크로 나중에 바꿔줘!

    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">{_html.escape(hero_text)}</div>
      <div class="hero-sub">{_html.escape(time_line)}</div>

      <div class="kpi-row">
        <div class="kpi">
          <b>가장 강한 기운</b>
          <div class="val">{ELEMENT_EMOJI[strong]} {ELEMENTS_KO[strong]}</div>
        </div>
        <div class="kpi">
          <b>보완할 기운</b>
          <div class="val">{ELEMENT_EMOJI[weak]} {ELEMENTS_KO[weak]}</div>
        </div>
      </div>
      <div class="small-note" style="margin-top:10px;">
        원하는 것만 빠르게 볼 수 있게 <b>탭</b>으로 나눴어요.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 🚨 여기서 탭을 4개로 정확하게 선언!
    tab1, tab2, tab3, tab4 = st.tabs(["✨ 요약", "📜 사주풀이(자세히)", "🧴 향수 Top3", "🥺 사쥬!!!(공유)"])

    # --- 1) 요약 탭 ---
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"**핵심 요약**: 지금은 **{ELEMENTS_KO[weak]}** 기운을 채우는 향이 가장 잘 맞아요.")
        st.markdown("부족한 기운을 향으로 보완하면, 컨디션/결정/관계 흐름이 더 안정적으로 잡히는 데 도움이 될 수 있어요.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 🧴 Top 3 추천 (빠르게 보기)")
        for i, (_, row) in enumerate(top3.iterrows()):
            b_name, p_name = safe_text(row.get("Brand")), safe_text(row.get("Name"))
            notes_raw = safe_text(row.get("Notes", ""))
            notes_ko = notes_to_korean_summary(notes_raw)
            matched = extract_matching_notes(row, weak, top_n=3)
            reason = build_east_asian_note_reason(weak, matched)
            badges = " ".join([f"<span class='badge'>{x}</span>" for x in get_element_vector_badges(row)])

            st.markdown(f"""
            <div class="section-card">
              <div style="font-weight:800;">{['🥇','🥈','🥉'][i]} {b_name} - {p_name}</div>
              <div style="margin-top:6px;">{badges}</div>
              <div class="small-muted" style="margin-top:8px;"><b>향 느낌:</b> {_html.escape(notes_ko)}</div>
              <div class="small-muted" style="margin-top:6px;"><b>이유:</b> {reason}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🚀 다음 액션")
        row0 = top3.iloc[0]
        b0, n0 = safe_text(row0.get("Brand")), safe_text(row0.get("Name"))
        naver0 = f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(f'{b0} {n0} 향수')}"
        st.link_button("🥇 1위 향수 시향 검색하기", naver0, use_container_width=True)

    # --- 2) 상세 사주풀이 탭 ---
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        reading_body = re.sub(r"<h2[^>]*>.*?</h2>", "", reading_result, flags=re.S | re.I)
        st.markdown(reading_body, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 3) 향수 Top 3 탭 ---
    with tab3:
        st.markdown("### 🛍️ 추천 향수 시향해보기")
        for i, (_, row) in enumerate(top3.iterrows()):
            b_name, p_name = safe_text(row.get("Brand")), safe_text(row.get("Name"))
            naver_url = f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(f'{b_name} {p_name} 향수')}"
            st.link_button(f"{['🥇','🥈','🥉'][i]} {b_name} - {p_name} 검색하기", naver_url, use_container_width=True)
        st.info("Tip) 가장 끌리는 1개만 먼저 시향해도 충분해요. ‘첫인상’이 맞는지 체크해보세요!")

   # --- 4) 🥺 사달라고 조르기 (바이럴 공유 & 설문) 탭 ---
   with tab4:
    st.markdown("### 📸 밈카드로 공유하기")
    st.info("인스타 스토리/커뮤니티에 바로 올릴 수 있게 ‘한 장’으로 만들어드려요. (다운로드 가능)")

    row0 = top3.iloc[0]
    best_brand = safe_text(row0.get("Brand"))
    best_name = safe_text(row0.get("Name"))

    hero_text = ""
    try:
        m = re.search(r"<h2[^>]*>(.*?)</h2>", st.session_state.get("reading_result",""), flags=re.S | re.I)
        if m:
            hero_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    except Exception:
        pass

    # ✅ 너 배포 링크로 바꾸기
    app_link = "https://your-perfume-saju-link.streamlit.app"

    png_buf = make_meme_card_png(
        user_name=user_name,
        strong=strong,
        weak=weak,
        best_brand=best_brand,
        best_name=best_name,
        app_link=app_link,
        hero_text=hero_text,
    )

    st.image(png_buf, use_container_width=True)

    st.download_button(
        "⬇️ 밈카드 이미지 다운로드(PNG)",
        data=png_buf.getvalue(),
        file_name=f"fate_scent_{st.session_state.get('session_id','result')}.png",
        mime="image/png",
        use_container_width=True
    )

    st.caption("Tip) 이 이미지 1장만 올려도 사람들이 ‘나도 해볼래’ 하고 들어와요.")
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
