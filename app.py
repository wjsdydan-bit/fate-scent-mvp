import streamlit as st
import pandas as pd
import datetime
import os
import math
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI

# =========================================================
# 0) 기본 설정 및 API 세팅
# =========================================================
st.set_page_config(page_title="향수 사쥬 (V3)", page_icon="🔮", layout="wide")

# OpenAI API 클라이언트 (Streamlit Secrets에서 불러오기)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    HAS_AI = True
except Exception:
    HAS_AI = False

base_dir = os.path.dirname(os.path.abspath(__file__))
# 💡 방금 업데이트한 V3 파일 이름으로 연결!
DATA_PATH = os.path.join(base_dir, "processed_perfumes_fixed_0223.csv")
LOG_PATH = os.path.join(base_dir, "recommendation_logs.csv")

ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
ELEMENTS_KO = {"Wood": "목(木/나무)", "Fire": "화(火/불)", "Earth": "토(土/흙)", "Metal": "금(金/쇠)", "Water": "수(水/물)"}

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# =========================================================
# 1) 만세력 기반 '진짜 사주팔자' 계산 함수
# =========================================================
def get_real_saju_elements(year, month, day, hour, minute):
    """실제 만세력 기반으로 사주팔자(8글자)를 뽑고 오행을 분석"""
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)
    gapja = cal.getGapJaString() # 출력 예: '임신년 을사월 병술일'
    parts = gapja.split()
    
    if len(parts) < 3:
        return None, None, None, None

    year_stem, year_branch = parts[0][0], parts[0][1]
    month_stem, month_branch = parts[1][0], parts[1][1]
    day_stem, day_branch = parts[2][0], parts[2][1]
    
    # 시주(태어난 시간) 계산 (명리학 자시~해시 기준)
    stems = "갑을병정무기경신임계"
    branches = "자축인묘진사오미신유술해"
    
    total_mins = hour * 60 + minute
    if total_mins >= 23 * 60 + 30 or total_mins < 1 * 60 + 30:
        time_branch_idx = 0 # 자시
    else:
        time_branch_idx = ((total_mins - 90) // 120 + 1) % 12
        
    time_branch = branches[time_branch_idx]
    
    day_stem_idx = stems.find(day_stem)
    time_stem_start_idx = (day_stem_idx % 5) * 2
    time_stem_idx = (time_stem_start_idx + time_branch_idx) % 10
    time_stem = stems[time_stem_idx]
    
    saju_chars = [year_stem, year_branch, month_stem, month_branch, day_stem, day_branch, time_stem, time_branch]
    
    # 명리학 오행 매핑 (목화토금수)
    element_map = {
        '갑':'Wood', '을':'Wood', '인':'Wood', '묘':'Wood',
        '병':'Fire', '정':'Fire', '사':'Fire', '오':'Fire',
        '무':'Earth', '기':'Earth', '진':'Earth', '술':'Earth', '축':'Earth', '미':'Earth',
        '경':'Metal', '신':'Metal', '유':'Metal', '申':'Metal',
        '임':'Water', '계':'Water', '해':'Water', '자':'Water'
    }
    
    elements_count = {'Wood':0, 'Fire':0, 'Earth':0, 'Metal':0, 'Water':0}
    for char in saju_chars:
        if char in element_map:
            elements_count[element_map[char]] += 1
            
    sorted_elements = sorted(elements_count.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_elements[0][0]
    weakest = sorted_elements[-1][0] 
    
    saju_name = f"{year_stem}{year_branch}년 {month_stem}{month_branch}월 {day_stem}{day_branch}일 {time_stem}{time_branch}시"
    
    return saju_name, elements_count, strongest, weakest

# =========================================================
# 2) OpenAI 맞춤형 풀이 생성 함수
# =========================================================
def generate_saju_ai_reading(saju_name, strongest, weakest, perfume_name, brand, notes):
    if not HAS_AI:
        return "⚠️ OpenAI API 키가 설정되지 않아 상세 풀이를 제공할 수 없습니다."
        
    strong_ko = ELEMENTS_KO.get(strongest, strongest)
    weak_ko = ELEMENTS_KO.get(weakest, weakest)
    
    system_prompt = """
    당신은 트렌디하고 통찰력 있는 '향수 사쥬' 마스터이자 수석 조향사입니다.
    고객의 사주팔자(천간지지)를 분석하고, 부족한 기운을 채워주는 향수를 추천합니다.
    단순한 분석을 넘어, 이 향수를 뿌렸을 때 고객의 삶에 어떤 '긍정적인 마법(운세 상승)'이 일어나는지 확신에 찬 다정한 말투(해요체)로 설명해 주세요.
    결과에는 '1. 사주 형국 분석', '2. 향수 처방의 이유', '3. 운세 발복(상승) 효과'를 소제목으로 나누어 가독성 있게 작성해주세요.
    """
    
    user_prompt = f"""
    고객의 사주팔자(태어난 연월일시)는 '{saju_name}'입니다. 
    이 사주에서 가장 과하게 집중된 기운은 '{strong_ko}'이고, 운의 흐름을 뚫어주기 위해 절대적으로 필요한(부족한) 기운은 '{weak_ko}'입니다.
    이 고객의 '{weak_ko}' 기운을 완벽하게 채워줄 액운 방지용 부적으로 '{notes}' 향을 지닌 '{brand}'의 '{perfume_name}' 향수를 처방했습니다.
    이 향수를 매일 뿌렸을 때 고객의 연애운, 재물운, 직장운 등이 어떻게 폭발적으로 상승하게 될지 600자 내외로 풀이해 주세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.75,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"사쥬 풀이를 생성하는 중 오류가 발생했습니다: {e}"

# =========================================================
# 3) 데이터 로드 및 UI 구성
# =========================================================
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
        df["all_text"] = df["all_text"].fillna("").astype(str).str.lower()
        df["matched_keywords"] = df["matched_keywords"].fillna("").astype(str)
        for e in ELEMENTS:
            if e in df.columns:
                df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)
            else:
                df[e] = 0.0
        return df
    return pd.DataFrame()

df = load_data()

st.title("🔮 향수 사쥬 (Saju & Scent)")
st.markdown("당신의 **진짜 사주팔자 8글자**를 분석해, 꽉 막힌 운을 틔워줄 **인생 향수**를 처방해 드립니다.")

with st.form("saju_form"):
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("이름(또는 닉네임)", placeholder="홍길동")
        birth_date = st.date_input("생년월일 (양력 기준)", min_value=datetime.date(1940, 1, 1), max_value=datetime.date.today())
    with col2:
        birth_hour = st.number_input("태어난 시 (0~23)", min_value=0, max_value=23, value=12)
        birth_min = st.number_input("태어난 분 (0~59)", min_value=0, max_value=59, value=0)

    st.markdown("---")
    st.markdown("### 🌸 향기 취향 선택")
    pref_tags = st.multiselect("끌리는 향 (여러 개 선택 가능)", ["꽃향기(플로럴)", "과일향(프루티)", "나무향(우디)", "상큼한(시트러스)", "포근한(머스크)", "달콤한(앰버/바닐라)", "시원한(아쿠아/마린)", "스모키/가죽"])
    dislike_tags = st.multiselect("피하고 싶은 향", ["꽃향기(플로럴)", "과일향(프루티)", "나무향(우디)", "상큼한(시트러스)", "포근한(머스크)", "달콤한(앰버/바닐라)", "시원한(아쿠아/마린)", "스모키/가죽"])

    submitted = st.form_submit_button("내 사쥬에 맞는 향수 처방받기 ✨")

# =========================================================
# 4) 추천 알고리즘 및 결과 화면
# =========================================================
if submitted:
    if df.empty:
        st.error("데이터베이스 파일이 없습니다.")
    elif not user_name:
        st.warning("이름을 입력해주세요!")
    else:
        with st.spinner("만세력을 바탕으로 사주팔자를 분석하고, AI 조향사가 당신만의 향수를 처방 중입니다... ⏳"):
            
            # 1. 사주 8글자 및 오행 계산
            saju_name, element_counts, strongest, weakest = get_real_saju_elements(
                birth_date.year, birth_date.month, birth_date.day, birth_hour, birth_min
            )
            
            # 2. 추천 로직 (코사인 유사도 + 💡 대중성 가중치)
            target_vec = [1.0 if e == weakest else (0.0 if e == strongest else 0.5) for e in ELEMENTS]
            target_norm = math.sqrt(sum(v**2 for v in target_vec))
            if target_norm == 0: target_norm = 1.0

            famous_brands = ['Jo Malone', 'Diptyque', 'Byredo', 'Aesop', 'Chanel', 'Dior', 'Clean', 'W.Dressroom', 'Forment', 'Tamburins', 'Nonfiction', 'Le Labo', 'Creed', 'John Varvatos', 'Ferrari', 'Acqua di Parma']

            rec_scores = []
            for idx, row in df.iterrows():
                # 싫어하는 향 필터링
                if any(dt in row["all_text"] for dt in dislike_tags):
                    rec_scores.append(-1)
                    continue
                
                perfume_vec = [float(row[e]) for e in ELEMENTS]
                p_norm = math.sqrt(sum(v**2 for v in perfume_vec))
                if p_norm == 0: p_norm = 1.0
                
                sim = sum(t * p for t, p in zip(target_vec, perfume_vec)) / (target_norm * p_norm)
                
                # 좋아하는 향 가산점
                if any(pt in row["all_text"] for pt in pref_tags):
                    sim += 0.15
                
                # 💡 [핵심] 대중적인 브랜드 가산점 폭격! (+0.2점)
                brand_name = str(row["Brand"])
                if any(fb.lower() in brand_name.lower() for fb in famous_brands):
                    sim += 0.20
                    
                rec_scores.append(sim)

            df["rec_score"] = rec_scores
            top3 = df[df["rec_score"] > 0].sort_values(by="rec_score", ascending=False).head(3)

            if top3.empty:
                st.warning("조건에 맞는 향수를 찾지 못했습니다. 취향 필터를 줄여보세요!")
            else:
                st.success(f"분석 완료! {user_name}님의 사주팔자는 **[{saju_name}]** 입니다.")
                
                # 3. AI 맞춤 풀이 호출
                best_perfume = top3.iloc[0]
                ai_reading = generate_saju_ai_reading(
                    saju_name, strongest, weakest, best_perfume["Name"], best_perfume["Brand"], best_perfume["Notes"]
                )
                
                st.markdown("### 💌 수석 조향사 & 명리학자의 맞춤 처방전")
                st.info(ai_reading)
                
                st.markdown("---")
                st.markdown(f"### 🏆 {user_name}님을 위한 운세 발복 향수 Top 3")
                
                for rank, (idx, row) in enumerate(top3.iterrows(), 1):
                    brand = row["Brand"]
                    name = row["Name"]
                    notes = row["Notes"]
                    
                    st.markdown(f"**{rank}위. {brand} - {name}**")
                    st.write(f"- 🌿 **주요 향(Notes):** {notes}")
                    
                    # 네이버 쇼핑 링크
                    query = f"{brand} {name} 향수"
                    url = f"https://search.shopping.naver.com/search/all?query={query.replace(' ', '%20')}"
                    st.markdown(f"[🛍️ 네이버 쇼핑에서 검색하기]({url})")
                    st.markdown("<br>", unsafe_allow_html=True)
                
                # 4. 로그 저장 로직 (선택사항, 필요시 추가)
                # ... (기존 로그 저장 로직 동일) ...
