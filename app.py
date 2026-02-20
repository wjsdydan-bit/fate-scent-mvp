import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import os
import math
from datetime import datetime as dt

import streamlit as st
import os

import streamlit as st
import os

# =========================================================
# 0) 기본 설정
# =========================================================
st.set_page_config(page_title="Fate Scent", page_icon="✨", layout="wide")

# 현재 app.py 파일이 있는 폴더의 절대 경로를 가져옴
base_dir = os.path.dirname(os.path.abspath(__file__))

# base_dir과 파일 이름을 합쳐서 절대 경로로 만듦
DATA_PATH = os.path.join(base_dir, "processed_perfumes_fixed.csv")
LOG_PATH = os.path.join(base_dir, "recommendation_logs.csv")

FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScGygiiOM-tp9ujKPmwzgMRozD3gxOmLwukyPo4V1-tS1HGLg/viewform?usp=dialog"

ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

# matplotlib: 있으면 레이더, 없으면 폴백
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# =========================================================
# 1) 데이터 로딩
# =========================================================
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path, encoding="utf-8-sig")

    # 0) 컬럼명 공백 정리 (엑셀 저장 시 공백 방지)
    df.columns = [str(c).strip() for c in df.columns]

    # 1) 필수 컬럼 보정
    # 텍스트 컬럼
    text_cols = ["matched_keywords", "all_text", "Notes", "Description", "Brand", "Name", "Image URL"]
    for c in text_cols:
        if c not in df.columns:
            df[c] = ""

    # 오행 컬럼 (없으면 0으로 생성)
    for e in ELEMENTS:
        if e not in df.columns:
            df[e] = 0.0

    # 2) 오행 점수 숫자(float) 강제 변환
    # (문자 "0.2", 빈칸, NaN, 이상값 모두 안전 처리)
    for e in ELEMENTS:
        df[e] = pd.to_numeric(df[e], errors='coerce').fillna(0.0)

    # 3) 텍스트 컬럼 문자열 강제 변환
    for c in text_cols:
        df[c] = df[c].fillna("").astype(str)

    # 4) 오행 점수 합계 계산
    df["element_sum"] = df[ELEMENTS].sum(axis=1)
    df = df[df["element_sum"] > 0].copy()

    # 5) 검색용 텍스트 생성
    df["matched_keywords"] = df["matched_keywords"].str.lower()
    df["all_text"] = df["all_text"].str.lower()
    df["search_text"] = (df["matched_keywords"] + " " + df["all_text"]).str.lower()
    df["notes_text"] = (df["Notes"] + " " + df["Description"]).str.lower()

    # 6) 샘플/세트 제거
    exclude_words = ["sample", "discovery", "set", "pack", "travel spray", "gift"]
    mask = ~df["Name"].str.lower().apply(lambda x: any(w in x for w in exclude_words))
    df = df[mask].copy()

    return df

try:
    df = load_data(DATA_PATH)
except Exception as e:
    st.error(
        "데이터를 못 불러왔어요.\n\n"
        "✅ app.py와 processed_perfumes_fixed.csv가 같은 폴더인지 확인하세요.\n"
        f"오류: {e}"
    )
    st.stop()


# =========================================================
# 2) 시간 드롭다운: "01~02" 형태
# =========================================================
def make_hour_ranges():
    ranges = []
    for h in range(24):
        h2 = (h + 1) % 24
        ranges.append(f"{h:02d}~{h2:02d}")
    return ranges

HOUR_RANGES = make_hour_ranges()

def range_to_start_hour(label: str) -> int:
    return int(label.split("~")[0])

# =========================================================
# 3) 사주(오행) MVP 로직
# =========================================================
def get_season(month: int) -> str:
    if month in [3,4,5]: return "spring"
    if month in [6,7,8]: return "summer"
    if month in [9,10,11]: return "autumn"
    return "winter"

def season_ko(season: str) -> str:
    return {"spring":"봄", "summer":"여름", "autumn":"가을", "winter":"겨울"}.get(season, season)

def normalize_vec(vec: dict) -> dict:
    s = sum(vec.values())
    if s <= 0:
        return {k: 0 for k in vec}
    return {k: v/s for k, v in vec.items()}

def build_element_vector(birth_date: datetime.date, birth_hour_start: int):
    season = get_season(birth_date.month)
    vec = {e: 0.2 for e in ELEMENTS}

    # 계절 보정
    if season == "spring":
        vec["Wood"] += 0.40; vec["Fire"] += 0.20
    elif season == "summer":
        vec["Fire"] += 0.40; vec["Earth"] += 0.20
    elif season == "autumn":
        vec["Metal"] += 0.40; vec["Earth"] += 0.20
    else:
        vec["Water"] += 0.40; vec["Metal"] += 0.20

    # 시간대 보정
    h = birth_hour_start
    if h in [23,0,1,2]:
        vec["Water"] += 0.25
    elif h in [3,4,5,6]:
        vec["Wood"] += 0.25
    elif h in [7,8,9,10]:
        vec["Fire"] += 0.25
    elif h in [11,12,13,14]:
        vec["Earth"] += 0.25
    elif h in [15,16,17,18]:
        vec["Metal"] += 0.25
    else:
        vec["Water"] += 0.15
        vec["Metal"] += 0.10

    vec = normalize_vec(vec)
    return season, vec

def need_avoid_from_vector(vec: dict):
    strongest = max(vec, key=vec.get)
    weakest = min(vec, key=vec.get)
    need = {k: 0.0 for k in vec}
    avoid = {k: 0.0 for k in vec}
    need[weakest] = 1.0
    avoid[strongest] = 1.0
    return strongest, weakest, need, avoid

def dynamic_story_kr(name: str, season: str, strongest: str, weakest: str):
    se = season_ko(season)
    return f"""
### 📜 {name}님을 위한 명리(命理) 향기 처방전

**{name}**님은 만물이 생동하고 변화하는 **{se}의 기운**을 바탕으로 태어나셨습니다. 
현재 {name}님의 오행(五行) 차트를 분석해 본 결과, 내면을 지배하는 **가장 강한 기운은 '{strongest}'**이며, **상대적으로 보완이 필요한 기운은 '{weakest}'**로 나타납니다.

✨ **나의 강점: {strongest} 기운의 발현**
명리학에서 특정 기운이 강하다는 것은 곧 본인만의 확실한 무기이자 매력 포인트가 있다는 뜻입니다. {strongest}의 에너지는 {name}님이 세상을 살아가는 뚜렷한 주관과 원동력이 되어주고 있을 것입니다. 하지만 이 기운이 너무 한쪽으로 쏠리게 되면, 때로는 스스로를 지치게 만들거나 일상의 불균형을 초래하기도 합니다.

⚖️ **운명의 빈칸: 왜 '{weakest}' 기운이 필요할까요?**
동양 철학에서는 '비워진 곳을 채워 균형을 맞추는 것(중화, 中和)'을 가장 이상적인 상태로 봅니다. 현재 {name}님의 차트에서 아쉬운 **{weakest} 기운이 부족해지면**, 일상에서 알 수 없는 갈증을 느끼거나 감정의 환기가 필요한 순간들을 남들보다 더 자주 경험할 수 있습니다. 이 빈칸을 채워주었을 때 비로소 {name}님이 원래 가진 강점이 더욱 빛을 발하게 됩니다.

🌿 **운명을 보완하는 향기 큐레이션**
과거에는 부족한 오행을 채우기 위해 특정 색깔의 옷을 입거나 머리를 두는 방향을 바꾸었지만, 현대에는 **'공간과 감정을 즉각적으로 바꾸는 향기'**가 그 역할을 대신할 수 있습니다. 

👉 따라서 AI는 {name}님의 평소 취향을 섬세하게 반영하면서도, **운명의 빈칸인 `{weakest}` 기운을 채워 밸런스를 맞춰줄 '맞춤형 향수'**를 아래와 같이 처방합니다.
"""

# =========================================================
# 4) 레이더 차트 (오른쪽 상단 1개만)
#    - 라벨은 한글 깨짐 방지 위해 영어 고정
# =========================================================
def radar_fig_small(vec: dict, title: str = "Elements Radar"):
    labels = ELEMENTS[:]
    values = [vec[k] for k in labels]
    vals = values + values[:1]
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    angles += angles[:1]

    # ⚠️ 최대한 줄임: figsize + dpi + 폰트
    fig = plt.figure(figsize=(2.2, 2.2), dpi=160)
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], labels, fontsize=6)
    ax.set_ylim(0, 0.75)

    ax.plot(angles, vals, linewidth=2)
    ax.fill(angles, vals, alpha=0.12)

    ax.set_yticks([0.2, 0.4, 0.6])
    ax.set_yticklabels(["0.2","0.4","0.6"], fontsize=5)
    plt.title(title, y=1.10, fontsize=8)
    return fig

def show_radar(vec: dict):
    if HAS_MPL:
        fig = radar_fig_small(vec, title="Elements Radar")
        # 컨테이너 폭으로 꽉 늘어나는 것 방지: Streamlit이 내부적으로 늘릴 수 있어 완전 제어는 어렵지만,
        # 오른쪽 컬럼 자체 폭을 제한하고, figure를 작게 만들어 최대한 작게 보이게 한다.
        st.pyplot(fig, clear_figure=True)
    else:
        st.warning("📌 레이더 차트는 matplotlib 설치 시 표시됩니다. (현재는 대체 차트)")
        chart_df = pd.DataFrame({"Element": ELEMENTS, "Score": [vec[e] for e in ELEMENTS]})
        st.bar_chart(chart_df.set_index("Element"))

# =========================================================
# 5) 취향 태그 -> 키워드
# =========================================================
TAG_TO_KW = {
    "상큼한(시트러스)": ["citrus", "bergamot", "lemon", "orange", "grapefruit", "yuzu", "mandarin"],
    "꽃향기(플로럴)": ["floral", "rose", "jasmine", "white floral", "neroli", "ylang ylang", "tuberose"],
    "나무향(우디)": ["woody", "cedar", "sandalwood", "vetiver", "patchouli", "moss"],
    "포근한(머스크)": ["musk", "white musk", "clean musk"],
    "달콤한(앰버/바닐라)": ["amber", "vanilla", "sweet", "tonka", "gourmand", "benzoin"],
    "시원한(아쿠아/마린)": ["aquatic", "marine", "sea salt", "watery", "ozonic", "salty"],
    "스모키/가죽": ["smoky", "incense", "leather", "tobacco", "animalic"]
}

def tags_to_keywords(tags):
    kws = []
    for t in tags:
        kws.extend(TAG_TO_KW.get(t, []))
    return sorted(set([k for k in kws if k]))

def kw_score(text, keywords):
    if not keywords:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text)
    return hits / len(keywords)

# 가중치
W_NEED = 0.60
W_AVOID = 0.25
W_PREF = 0.25
W_DISLIKE = 0.20

# =========================================================
# 6) 부족 오행을 채우는 키워드 + 한글 요약 태그
# =========================================================
ELEMENT_KEYWORDS = {
    "Wood":  ["green", "herbal", "fougere", "leafy", "pine", "grass", "vetiver", "tea", "bamboo", "matcha"],
    "Fire":  ["citrus", "bergamot", "lemon", "orange", "grapefruit", "yuzu", "spicy", "warm spicy", "ginger", "cinnamon", "pepper", "pink pepper"],
    "Earth": ["woody", "musk", "amber", "powdery", "earthy", "patchouli", "vanilla", "oud", "benzoin", "tonka"],
    "Metal": ["aldehyde", "metallic", "mineral", "cool", "mint", "soapy", "clean", "white floral", "cotton", "white tea"],
    "Water": ["aquatic", "marine", "salty", "ozonic", "sea", "sea salt", "watery", "blue"]
}

KW_KO = {
    "citrus":"시트러스","bergamot":"베르가못","lemon":"레몬","orange":"오렌지","grapefruit":"자몽","yuzu":"유자","mandarin":"만다린",
    "floral":"플로럴","rose":"로즈","jasmine":"자스민","white floral":"화이트 플로럴","neroli":"네롤리","ylang ylang":"일랑일랑","tuberose":"튜베로즈",
    "woody":"우디","cedar":"시더우드","sandalwood":"샌달우드","vetiver":"베티버","patchouli":"파출리","moss":"모스",
    "musk":"머스크","white musk":"화이트 머스크","clean":"클린","soapy":"비누향",
    "amber":"앰버","vanilla":"바닐라","sweet":"달콤","tonka":"통카","gourmand":"구르망","benzoin":"벤조인","powdery":"파우더리",
    "aquatic":"아쿠아틱","marine":"마린","sea salt":"씨솔트","watery":"워터리","ozonic":"오존","salty":"솔티","sea":"바다",
    "spicy":"스파이시","warm spicy":"웜 스파이시","ginger":"진저","cinnamon":"시나몬","pepper":"페퍼","pink pepper":"핑크페퍼",
    "smoky":"스모키","incense":"인센스","leather":"가죽","tobacco":"타바코","animalic":"애니멀릭",
    "mint":"민트","mineral":"미네랄","metallic":"메탈릭","cool":"쿨","cotton":"코튼","white tea":"화이트티"
}

def find_fill_keywords(row, weakest_element: str, max_n=3):
    text = f"{row.get('matched_keywords','')} {row.get('notes_text','')}".lower()
    candidates = ELEMENT_KEYWORDS.get(weakest_element, [])
    found = []
    for kw in candidates:
        if kw and kw in text:
            found.append(kw)
        if len(found) >= max_n:
            break
    uniq = []
    for x in found:
        if x not in uniq:
            uniq.append(x)
    return uniq

def keywords_to_korean_tags(keywords):
    tags = []
    for kw in keywords:
        k = KW_KO.get(kw)
        if k and k not in tags:
            tags.append(k)
    return tags[:6]

def highlight_keywords_md(keywords):
    if not keywords:
        return ""
    return " ".join([f"`{k}`" for k in keywords[:3]])

def make_reason_kr(season, need_score, pref_score, weakest_element, fill_keywords):
    w_need, w_pref = need_score * W_NEED, pref_score * W_PREF
    if w_pref > w_need:
        base = "취향 반영이 강한 추천 🎯"
    else:
        if season == "winter": base = "추운 기운을 데워주는 추천 🔥"
        elif season == "summer": base = "뜨거운 기운을 식혀주는 추천 💧"
        elif season == "spring": base = "생기를 끌어올리는 추천 🌱"
        else: base = "정돈/차분 밸런스 추천 🍂"

    kw_md = highlight_keywords_md(fill_keywords)
    if kw_md:
        return f"{base} · **부족 오행: {weakest_element}** → {kw_md}"
    return f"{base} · **부족 오행: {weakest_element}**"

def make_naver_link(brand, name):
    q = urllib.parse.quote(f"{brand} {name} 향수")
    return f"https://search.shopping.naver.com/search/all?query={q}"

# =========================================================
# 7) 로그 저장
# =========================================================
def append_log_rows(rows, log_path=LOG_PATH):
    log_df = pd.DataFrame(rows)
    if not os.path.exists(log_path):
        log_df.to_csv(log_path, index=False, encoding="utf-8-sig")
    else:
        log_df.to_csv(log_path, mode="a", header=False, index=False, encoding="utf-8-sig")

# =========================================================
# 8) UI
# =========================================================
st.title("✨ Fate Scent : 운명의 향기")
st.markdown("생년월일과 태어난 시간(대략)을 입력하면 **오행 균형을 분석**해 지금 당신에게 필요한 분위기를 채워줄 향수를 추천합니다.")
st.divider()

with st.expander("💡 추천 원리 / 사용 방법"):
    st.markdown(
        """
- 이 서비스는 **구매/클릭 이력**이 없는 신규 사용자도 추천을 받을 수 있게 만든 **MVP**입니다.
- **생년월일(계절)** + **태어난 시간대(대략)**로 **오행 분포(5요소)**를 만들고,
- **가장 부족한 오행(Weakest)**을 “지금 보완할 기운(Need)”으로 설정합니다.
- 향수는 데이터의 **노트/키워드(Notes, Accords, 설명)**에 해당 오행과 연결된 단어가 많을수록 점수가 올라갑니다.
- 추가로 **좋아하는 향(가산)** / **피하고 싶은 향(감점)**을 반영합니다.
        """
    )

# 세션상태(중복 선택 방지용)
if "pref_tags" not in st.session_state:
    st.session_state.pref_tags = []
if "dislike_tags" not in st.session_state:
    st.session_state.dislike_tags = []

col_input, col_chart = st.columns([1.25, 1.0], gap="large")

with col_input:
    st.subheader("🧾 개인정보 입력")

    user_name = st.text_input("이름 또는 닉네임", placeholder="예: 김데이터")

    user_birth = st.date_input(
        "생년월일",
        min_value=datetime.date(1940, 1, 1),
        max_value=datetime.date.today(),
        value=datetime.date(1992, 5, 20)
    )

    time_range = st.selectbox("태어난 시간(대략)", HOUR_RANGES, index=16)
    birth_hour_start = range_to_start_hour(time_range)

    st.markdown("### 🎛️ 취향(선택)")
    st.caption("좋아하는 향과 피하고 싶은 향은 동시에 고르면 모순이라, 서로 자동 제외됩니다.")

    all_tags = list(TAG_TO_KW.keys())
    pref_options = [t for t in all_tags if t not in st.session_state.dislike_tags]
    dislike_options = [t for t in all_tags if t not in st.session_state.pref_tags]

    pref = st.multiselect(
        "좋아하는 향",
        options=pref_options,
        default=[t for t in st.session_state.pref_tags if t in pref_options],
        key="pref_multiselect"
    )
    dislike = st.multiselect(
        "피하고 싶은 향",
        options=dislike_options,
        default=[t for t in st.session_state.dislike_tags if t in dislike_options],
        key="dislike_multiselect"
    )

    st.session_state.pref_tags = pref
    st.session_state.dislike_tags = dislike

    top_k = st.slider("추천 개수", 3, 10, 3)
    run_btn = st.button("🔍 내 사주 풀이 & 향수 추천 받기", type="primary", use_container_width=True)

with col_chart:
    st.subheader("📊 오행 차트")
    st.caption("※ 차트 라벨은 한글 깨짐 방지를 위해 영어로 표시됩니다.")

    if run_btn and user_name:
        season, user_vec = build_element_vector(user_birth, birth_hour_start)
        strongest, weakest, need_vec, avoid_vec = need_avoid_from_vector(user_vec)

        b1, b2 = st.columns(2)
        with b1:
            st.metric("강한 기운", strongest)
        with b2:
            st.metric("부족한 기운", weakest)

        # 작게 만들려고 노력했지만, 환경에 따라 크게 보일 수 있음
        show_radar(user_vec)
    else:
        st.info("왼쪽 입력 후 추천 버튼을 누르면 표시됩니다.")

st.divider()

# =========================================================
# 9) 실행 + 추천 + 수치 배지(부족 오행 보완량)
# =========================================================
if run_btn:
    if not user_name:
        st.warning("이름(또는 닉네임)을 입력해주세요.")
        st.stop()

    with st.spinner("사주(오행) 분석하고 향수를 매칭 중입니다..."):
        season, user_vec = build_element_vector(user_birth, birth_hour_start)
        strongest, weakest, need_vec, avoid_vec = need_avoid_from_vector(user_vec)

        st.subheader("🔮 사주 풀이(요약)")
        st.markdown(dynamic_story_kr(user_name, season, strongest, weakest))

        pref_keywords = tags_to_keywords(st.session_state.pref_tags)
        dislike_keywords = tags_to_keywords(st.session_state.dislike_tags)

        work = df.copy()
        work["need_score"] = work.apply(lambda r: sum(r[e] * need_vec[e] for e in ELEMENTS), axis=1)
        work["avoid_score"] = work.apply(lambda r: sum(r[e] * avoid_vec[e] for e in ELEMENTS), axis=1)
        work["pref_score"] = work["search_text"].apply(lambda x: kw_score(x, pref_keywords))
        work["dislike_score"] = work["search_text"].apply(lambda x: kw_score(x, dislike_keywords))

        work["rec_score"] = (
            (W_NEED * work["need_score"])
            - (W_AVOID * work["avoid_score"])
            + (W_PREF * work["pref_score"])
            - (W_DISLIKE * work["dislike_score"])
        )

        result = (
            work.sort_values("rec_score", ascending=False)
                .drop_duplicates(subset=["Name"])
                .head(top_k)
                .copy()
        )

        result["naver_link"] = result.apply(lambda r: make_naver_link(r["Brand"], r["Name"]), axis=1)

        # 부족 오행 채우는 키워드 + 한글 태그
        fill_kw = []
        fill_ko = []
        reason = []
        fill_amount = []  # ✅ 수치 배지용: 부족 오행을 얼마나 채우는지

        for _, row in result.iterrows():
            kws = find_fill_keywords(row, weakest, max_n=3)
            fill_kw.append(", ".join(kws) if kws else "")
            fill_ko.append(", ".join(keywords_to_korean_tags(kws)))
            reason.append(make_reason_kr(season, row["need_score"], row["pref_score"], weakest, kws))

            # ✅ 수치화(0~100%)
            # 부족 오행만 보면 됨: 향수의 해당 오행 점수(0~1)에 비례
            # 100% = 그 향수가 weakest 오행 성분이 매우 강한 편
            # (단순/직관적인 MVP)
            amt = float(row.get(weakest, 0.0))
            fill_amount.append(int(round(amt * 100)))

        result["fill_keywords"] = fill_kw
        result["fill_keywords_ko"] = fill_ko
        result["reason"] = reason
        result["fill_percent"] = fill_amount

        # =========================================================
        # TOP 3 강조 카드
        # =========================================================
        st.subheader("🏆 추천 TOP 3 (강조)")
        st.caption("※ 카드의 배지에서 **부족한 오행을 얼마나 채우는지(%)**를 확인할 수 있어요.")

        top3 = result.head(3).copy()

        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 2.3, 1.2], gap="large")

                with c1:
                    img = str(row.get("Image URL",""))
                    if img.startswith("http"):
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("이미지 없음")

                with c2:
                    st.markdown(f"### #{rank}  {row.get('Name','-')}")
                    st.write(f"**브랜드:** {row.get('Brand','-')}")

                    # ✅ 배지: 부족 오행 보완량(수치)
                    st.markdown(
                        f"🟦 **부족 오행({weakest}) 보완:**  **{row.get('fill_percent',0)}%**"
                    )

                    st.markdown(f"**추천 이유:** {row.get('reason','-')}")

                    if str(row.get("fill_keywords_ko","")).strip():
                        st.info(f"**부족 오행을 채우는 핵심 키워드(한글 요약):** {row['fill_keywords_ko']}")

                    # Notes/Description은 한글 “요약(태그)”만 보여주고, 원문은 expander로
                    with st.expander("원문 Notes/Description 보기(영어)"):
                        notes = str(row.get("Notes",""))
                        desc = str(row.get("Description",""))
                        if notes.strip():
                            st.write(f"**Notes(EN):** {notes}")
                        if desc.strip():
                            st.write(f"**Description(EN):** {desc}")

                with c3:
                    st.markdown("**점수**")
                    st.metric("최종 점수", f"{row.get('rec_score',0):.4f}")
                    st.metric("Need", f"{row.get('need_score',0):.3f}")
                    st.metric("취향", f"{row.get('pref_score',0):.3f}")
                    st.link_button("🛒 네이버 쇼핑에서 보기", row["naver_link"], use_container_width=True)

        # =========================================================
        # 추가 추천
        # =========================================================
        if top_k > 3:
            st.subheader(f"✨ 추가 추천 (4 ~ {top_k})")
            rest = result.iloc[3:].copy()
            for rank, (_, row) in enumerate(rest.iterrows(), start=4):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2.3, 1.2], gap="large")

                    with c1:
                        img = str(row.get("Image URL",""))
                        if img.startswith("http"):
                            st.image(img, use_container_width=True)
                        else:
                            st.caption("이미지 없음")

                    with c2:
                        st.markdown(f"### #{rank}  {row.get('Name','-')}")
                        st.write(f"**브랜드:** {row.get('Brand','-')}")
                        st.markdown(f"🟦 **부족 오행({weakest}) 보완:**  **{row.get('fill_percent',0)}%**")
                        st.markdown(f"**추천 이유:** {row.get('reason','-')}")

                        if str(row.get("fill_keywords_ko","")).strip():
                            st.info(f"**부족 오행을 채우는 핵심 키워드(한글 요약):** {row['fill_keywords_ko']}")

                        with st.expander("원문 Notes/Description 보기(영어)"):
                            notes = str(row.get("Notes",""))
                            desc = str(row.get("Description",""))
                            if notes.strip():
                                st.write(f"**Notes(EN):** {notes}")
                            if desc.strip():
                                st.write(f"**Description(EN):** {desc}")

                    with c3:
                        st.metric("최종 점수", f"{row.get('rec_score',0):.4f}")
                        st.link_button("🛒 네이버 쇼핑에서 보기", row["naver_link"], use_container_width=True)

        # =========================================================
        # 로그 저장 (Top3만 저장)
        # =========================================================
        ts = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        log_rows = []
        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            log_rows.append({
                "timestamp": ts,
                "user_name": user_name,
                "birth_date": str(user_birth),
                "birth_time_range": time_range,
                "season": season,
                "strongest_element": strongest,
                "weakest_element": weakest,
                "pref_tags": ",".join(st.session_state.pref_tags),
                "dislike_tags": ",".join(st.session_state.dislike_tags),
                "rank": rank,
                "perfume_name": row.get("Name",""),
                "brand": row.get("Brand",""),
                "rec_score": float(row.get("rec_score", 0.0)),
                "fill_percent": int(row.get("fill_percent",0)),
                "fill_keywords": row.get("fill_keywords",""),
                "fill_keywords_ko": row.get("fill_keywords_ko",""),
                "naver_link": row.get("naver_link","")
            })

        try:
            append_log_rows(log_rows, LOG_PATH)
            st.success(f"✅ 추천 결과가 CSV로 저장됐어요: {LOG_PATH}")
        except Exception as e:
            st.error(f"❌ CSV 저장 실패: {e}")

        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "rb") as f:
                st.download_button(
                    "📥 추천 로그 CSV 다운로드",
                    data=f,
                    file_name="recommendation_logs.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.divider()

        st.subheader("📝 1분 피드백(설문)")
        st.write("추천이 어땠는지 알려주면, 다음 버전에서 추천 품질을 더 올릴 수 있어요.")
        st.link_button("👉 설문 참여하기", FEEDBACK_FORM_URL, type="primary")
