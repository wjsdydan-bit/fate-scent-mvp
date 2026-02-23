import streamlit as st
import pandas as pd
import datetime
import os
import math
from korean_lunar_calendar import KoreanLunarCalendar
from openai import OpenAI

# =========================================================
# 0) 기본 설정 및 프리미엄 스타일 적용
# =========================================================
st.set_page_config(page_title="향수 사쥬", page_icon="🔮", layout="wide")

# UI 디자인을 위한 커스텀 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; height: 3em; font-weight: bold; }
    .saju-card { background-color: white; padding: 25px; border-radius: 15px; border-left: 5px solid #764ba2; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .perfume-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; text-align: center; }
    .result-header { color: #2d3436; font-weight: bold; border-bottom: 2px solid #764ba2; padding-bottom: 10px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# OpenAI API 클라이언트 세팅
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    HAS_AI = True
except Exception:
    HAS_AI = False

base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(base_dir, "processed_perfumes_fixed_0223.csv")
ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
ELEMENTS_KO = {"Wood": "목(나무)", "Fire": "화(불)", "Earth": "토(흙)", "Metal": "금(쇠)", "Water": "수(물)"}

# =========================================================
# 1) 만세력 및 AI 로직 함수
# =========================================================
def get_real_saju_elements(year, month, day, hour, minute):
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)
    gapja = cal.getGapJaString().split()
    if len(gapja) < 3: return None, None, None, None

    # 사주 8글자 추출
    year_char, month_char, day_char = gapja[0], gapja[1], gapja[2]
    stems, branches = "갑을병정무기경신임계", "자축인묘진사오미신유술해"
    
    total_mins = hour * 60 + minute
    time_branch_idx = 0 if total_mins >= 1410 or total_mins < 90 else ((total_mins - 90) // 120 + 1) % 12
    time_branch = branches[time_branch_idx]
    time_stem = stems[((stems.find(day_char[0]) % 5) * 2 + time_branch_idx) % 10]
    
    saju_chars = [year_char[0], year_char[1], month_char[0], month_char[1], day_char[0], day_char[1], time_stem, time_branch]
    element_map = {'갑':'Wood','을':'Wood','인':'Wood','묘':'Wood','병':'Fire','정':'Fire','사':'Fire','오':'Fire','무':'Earth','기':'Earth','진':'Earth','술':'Earth','축':'Earth','미':'Earth','경':'Metal','신':'Metal','유':'Metal','申':'Metal','임':'Water','계':'Water','해':'Water','자':'Water'}
    
    counts = {e: 0 for e in ELEMENTS}
    for c in saju_chars:
        if c in element_map: counts[element_map[c]] += 1
            
    sorted_e = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return f"{year_char} {month_char} {day_char} {time_stem}{time_branch}", counts, sorted_e[0][0], sorted_e[-1][0]

def generate_ai_reading(saju_name, weakest, perfume):
    if not HAS_AI: return "AI 풀이를 불러올 수 없습니다."
    
    weak_ko = ELEMENTS_KO.get(weakest)
    prompt = f"""
    당신은 명리학자와 조향사가 결합된 '향수 사쥬' 마스터입니다.
    고객의 사주 [{saju_name}]를 분석한 결과, [{weak_ko}] 기운이 가장 부족합니다.
    이 부족한 기운을 채우기 위해 [{perfume['Brand']}]의 [{perfume['Name']}] 향수를 처방했습니다.
    
    이 향수의 성분과 오행 에너지가 고객의 막힌 운을 어떻게 뚫어주는지, 
    특히 연애, 재물, 사회적 성공 중 어떤 부분에 마법처럼 작용할지 
    매우 소름 돋고 다정하게 3문단으로 설명해 주세요. (문단별로 소제목을 붙여주세요)
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "운명을 바꾸는 향수 전문가입니다."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# =========================================================
# 2) 데이터 로드
# =========================================================
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df["all_text"] = (df["Name"] + " " + df["Brand"] + " " + df["Notes"]).fillna("").str.lower()
        for e in ELEMENTS: df[e] = pd.to_numeric(df[e], errors="coerce").fillna(0.0)
        return df
    return pd.DataFrame()

df = load_data()

# =========================================================
# 3) 메인 화면 UI
# =========================================================
st.title("🔮 향수 사쥬")
st.write("나의 **사주팔자**를 분석해, 부족한 기운을 채우고 **운을 바꿔줄 향수**를 처방받으세요.")

with st.container():
    st.markdown('<div class="saju-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        u_name = st.text_input("성함/닉네임", placeholder="이름을 입력하세요")
    with col2:
        u_birth = st.date_input("생년월일", min_value=datetime.date(1950, 1, 1))
    with col3:
        u_time = st.time_input("태어난 시간", datetime.time(12, 0))
    
    p_tags = st.multiselect("선호하는 향기", ["우디", "플로럴", "시트러스", "머스크", "프루티", "아쿠아"])
    d_tags = st.multiselect("기피하는 향기", ["우디", "플로럴", "시트러스", "머스크", "프루티", "아쿠아"])
    
    submit = st.button("운명의 향수 처방받기")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 4) 결과 출력
# =========================================================
if submit and u_name:
    s_name, e_counts, strong, weak = get_real_saju_elements(u_birth.year, u_birth.month, u_birth.day, u_time.hour, u_time.minute)
    
    # 추천 알고리즘 (브랜드 가중치 대폭 강화)
    famous = ['Jo Malone', 'Diptyque', 'Byredo', 'Aesop', 'Chanel', 'Dior', 'Clean', 'Forment', 'Tamburins', 'Nonfiction', 'Le Labo']
    target = [1.0 if e == weak else (0.0 if e == strong else 0.5) for e in ELEMENTS]
    
    res = []
    for idx, row in df.iterrows():
        if any(t.lower() in row["all_text"] for t in d_tags): 
            res.append(-1); continue
        
        vec = [row[e] for e in ELEMENTS]
        sim = sum(t*v for t, v in zip(target, vec)) / (math.sqrt(sum(t**2 for t in target)) * math.sqrt(sum(v**2 for v in vec) or 1))
        
        # 💡 강력한 브랜드 가중치 (+0.4) - 이제 웬만하면 유명 브랜드가 1위에 뜹니다.
        if any(f.lower() in str(row['Brand']).lower() for f in famous): sim += 0.4
        res.append(sim)
    
    df["score"] = res
    top3 = df.sort_values("score", ascending=False).head(3)
    
    st.markdown(f'<h2 class="result-header">✨ {u_name}님의 사주 분석 결과: {s_name}</h2>', unsafe_allow_html=True)
    
    # AI 마스터의 설명 (가장 강조)
    best = top3.iloc[0]
    with st.spinner("AI 사쥬 마스터가 운명을 분석 중입니다..."):
        reading = generate_ai_reading(s_name, weak, best)
        st.markdown(f'<div class="saju-card"><h3>📜 운명을 바꾸는 처방전</h3>{reading}</div>', unsafe_allow_html=True)
    
    # 향수 카드 레이아웃
    st.markdown('<h3 class="result-header">🧴 처방된 향수 Top 3</h3>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(f'<div class="perfume-card">', unsafe_allow_html=True)
            # 이미지 처리
            img = row.get("Image URL")
            if pd.isna(img) or img == "":
                st.markdown("🎨 **이미지 준비 중**")
            else:
                st.image(img, use_container_width=True)
            
            st.markdown(f"**{row['Brand']}**")
            st.markdown(f"#### {row['Name']}")
            st.caption(f"주요 노트: {row['Notes']}")
            
            q = f"{row['Brand']} {row['Name']} 향수"
            st.markdown(f"[네이버 쇼핑]({f'https://search.shopping.naver.com/search/all?query={q.replace(' ', '%20')}'})")
            st.markdown('</div>', unsafe_allow_html=True)
