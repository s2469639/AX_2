# app.py
import streamlit as st
import time
from questions import QUESTIONS, JOB_PROFILES
import base64
import urllib.parse

# --- 1. 페이지 설정 및 파스텔 테마 커스텀 CSS ---
st.set_page_config(
    page_title="무역직군 MBTI 적성·흥미 테스트",
    page_icon="⛵",
    layout="centered"
)

PASTEL_CSS = """
<style>
    /* 전체 배경: 은은한 파스텔 오프화이트/소프트 피치 아이보리 */
    .stApp {
        background: linear-gradient(135deg, #FBFBFD 0%, #FFF9F5 50%, #F5F7FA 100%);
        color: #2D3748;
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Segoe UI", sans-serif;
    }

    /* 메인 헤더 영역 */
    .main-header {
        text-align: center;
        padding: 32px 20px 24px 20px;
        background: linear-gradient(120deg, #FFE5EC, #F0E6FF, #E8F0FE);
        border-radius: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 30px;
    }
    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #2B3A42;
        margin-bottom: 8px;
    }
    .main-desc {
        font-size: 1.02rem;
        color: #64748B;
        margin-bottom: 0;
    }

    /* 문항 카드 */
    .question-card {
        background-color: #FFFFFF;
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        border: 1px solid #F1F3F5;
        margin-bottom: 24px;
    }
    .question-badge {
        display: inline-block;
        background-color: #E2ECE9;
        color: #3B5F5D;
        font-size: 0.88rem;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 14px;
        margin-bottom: 14px;
    }
    .question-text {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1A202C;
        line-height: 1.6;
        margin-bottom: 8px;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
    }

    /* ====================================================
       라디오 버튼 선택지: 적당한 크기 + 단어 단위 줄바꿈(keep-all)
       ==================================================== */
    div[data-testid="stRadio"] label {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        color: #2D3748 !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #EDF2F7 !important;
        transition: all 0.2s ease;
        margin-bottom: 4px !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stRadio"] label p {
        font-size: 1.10rem !important;
        font-weight: 500 !important;
        line-height: 1.55 !important;
        color: #2D3748 !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        transform: translateY(-1px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 10px;
    }

    /* 결과 메인 카드 */
    .result-card {
        background-color: #FFFFFF;
        border-radius: 22px;
        padding: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        border: 1px solid #EAEAEA;
        margin-bottom: 25px;
    }
    .result-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #1A202C;
        margin-bottom: 6px;
    }
    .result-subtitle {
        font-size: 0.98rem;
        color: #718096;
        margin-bottom: 16px;
    }
    .tagline-box {
        background-color: #FFF3EA;
        border-left: 4px solid #F4A261;
        padding: 14px 18px;
        border-radius: 10px;
        font-size: 1.05rem;
        font-weight: 600;
        color: #B25E29;
        margin-bottom: 20px;
        word-break: keep-all;
    }

    /* 성향 매칭 이유 전용 박스 */
    .why-fit-box {
        background-color: #FAF5FF;
        border-left: 5px solid #9F7AEA;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 25px;
        box-shadow: 0 2px 10px rgba(159, 122, 234, 0.08);
    }
    .why-fit-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #553C9A;
        margin-bottom: 8px;
    }
    .why-fit-core {
        font-size: 1.02rem;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 14px;
        line-height: 1.55;
        word-break: keep-all;
    }
    .why-fit-item {
        font-size: 0.93rem;
        color: #4A5568;
        line-height: 1.65;
        margin-bottom: 8px;
        padding-left: 4px;
        word-break: keep-all;
    }

    /* 실무 강점 카드 */
    .strength-card {
        background-color: #FFFFFF;
        border-left: 4px solid #4299E1;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border-top: 1px solid #EDF2F7;
        border-right: 1px solid #EDF2F7;
        border-bottom: 1px solid #EDF2F7;
    }
    .strength-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #2B6CB0;
        margin-bottom: 6px;
        word-break: keep-all;
    }
    .strength-detail {
        font-size: 0.92rem;
        color: #4A5568;
        line-height: 1.6;
        word-break: keep-all;
    }

    .activity-item {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        color: #334155;
        border-left: 3px solid #38B2AC;
        line-height: 1.5;
        word-break: keep-all;
    }

    .cert-item {
        background-color: #F8FAFC;
        border-left: 3px solid #805AD5;
        border-radius: 8px;
        padding: 11px 15px;
        margin-bottom: 10px;
    }
    .cert-title {
        font-size: 0.96rem;
        font-weight: 700;
        color: #2D3748;
    }
    .cert-org {
        font-size: 0.8rem;
        color: #718096;
        font-weight: 500;
        margin-left: 6px;
    }
    .cert-desc {
        font-size: 0.86rem;
        color: #4A5568;
        margin-top: 4px;
        line-height: 1.45;
        word-break: keep-all;
    }

    /* 버튼 스타일 */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #BDE0FE 0%, #A2D2FF 100%);
        color: #1E3A8A;
        border: none;
        border-radius: 14px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 10px rgba(162, 210, 255, 0.4);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(162, 210, 255, 0.6);
        color: #0F2557;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FFC6FF, #BDB2FF, #A0C4FF);
    }

    /* ====================================================
       ⛵ 로딩 화면: Streamlit 내부 박스 투명화 + 기둥 제거
       ==================================================== */
    .ocean-loading-box {
        width: 100%;
        background: linear-gradient(135deg, #D4EBFC 0%, #BFE1FB 50%, #A7D4F9 100%) !important;
        border-radius: 24px;
        padding: 40px 20px 32px 20px;
        box-shadow: 0 10px 25px rgba(167, 212, 249, 0.45);
        text-align: center;
        overflow: hidden;
        position: relative;
        margin-bottom: 25px;
        border: 1px solid #E1EFFF;
    }
    
    .ocean-loading-box, .ocean-loading-box * {
        box-sizing: border-box;
    }
    .ocean-loading-box div, 
    .ocean-loading-box p, 
    .ocean-loading-box span {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    .loading-header-text {
        font-size: 1.42rem;
        font-weight: 700;
        color: #1E3A8A !important;
        margin-bottom: 6px;
        letter-spacing: -0.3px;
    }
    .loading-sub-text {
        font-size: 0.94rem;
        color: #3B608C !important;
        margin-bottom: 20px;
    }
    .sea-stage {
        position: relative;
        width: 100%;
        height: 105px;
        overflow: hidden;
        background: transparent !important;
    }
    .sailing-ship-smooth {
        position: absolute;
        top: 2px;
        width: 110px;
        height: 95px;
        background: transparent !important;
        animation: cruise 4.5s linear infinite, floating 1.6s ease-in-out infinite alternate;
    }
    .sailing-ship-smooth svg {
        display: block;
        width: 100%;
        height: 100%;
        background: transparent !important;
    }
    @keyframes cruise {
        0% { left: -120px; }
        100% { left: 105%; }
    }
    @keyframes floating {
        0% { transform: translateY(0px) rotate(-3deg); }
        50% { transform: translateY(-7px) rotate(2deg); }
        100% { transform: translateY(2px) rotate(4deg); }
    }

    /* ====================================================
       📱 모바일 및 태블릿 완전 대응 반응형(Responsive) 미디어 쿼리
       ==================================================== */
    @media (max-width: 768px) {
        /* 상단 메인 헤더 컴팩트화 */
        .main-header {
            padding: 24px 14px 18px 14px !important;
            border-radius: 18px !important;
            margin-bottom: 20px !important;
        }
        .main-title {
            font-size: 1.45rem !important;
            line-height: 1.35 !important;
        }
        .main-desc {
            font-size: 0.88rem !important;
        }

        /* 질문지 카드 모바일 여백 */
        .question-card {
            padding: 18px 14px !important;
            border-radius: 14px !important;
            margin-bottom: 16px !important;
        }
        .question-text {
            font-size: 1.10rem !important;
            line-height: 1.5 !important;
        }
        .question-badge {
            font-size: 0.8rem !important;
            padding: 4px 10px !important;
            margin-bottom: 10px !important;
        }

        /* 모바일 라디오 선택지 터치 최적화 */
        div[data-testid="stRadio"] label {
            padding: 11px 13px !important;
            font-size: 0.98rem !important;
            border-radius: 10px !important;
        }
        div[data-testid="stRadio"] label p {
            font-size: 0.96rem !important;
            line-height: 1.45 !important;
        }

        /* 결과 화면 모바일 스케일링 */
        .result-card {
            padding: 20px 15px !important;
            border-radius: 16px !important;
        }
        .result-title {
            font-size: 1.35rem !important;
        }
        .result-subtitle {
            font-size: 0.88rem !important;
        }
        .tagline-box {
            font-size: 0.92rem !important;
            padding: 11px 14px !important;
        }
        .why-fit-box {
            padding: 16px 14px !important;
            border-radius: 12px !important;
        }
        .why-fit-header {
            font-size: 1.05rem !important;
        }
        .why-fit-core {
            font-size: 0.92rem !important;
        }

        /* 버튼 풀사이즈 최적화 */
        div.stButton > button:first-child {
            padding: 10px 18px !important;
            font-size: 0.98rem !important;
        }
    }
</style>
"""
st.markdown(PASTEL_CSS, unsafe_allow_html=True)

# --- 2. 세션 상태 초기화 ---
if "step" not in st.session_state:
    st.session_state.step = "start"
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "scores_mbti" not in st.session_state:
    st.session_state.scores_mbti = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
if "scores_job" not in st.session_state:
    st.session_state.scores_job = {job: 0 for job in JOB_PROFILES.keys()}
if "view_rank" not in st.session_state:
    st.session_state.view_rank = 1

# --- 3. 화면 렌더링 함수들 ---
def render_start_page():
    st.markdown("""
        <div class="main-header">
            <div class="main-title">⛵ 무역직군 MBTI 적성·흥미 테스트</div>
            <div class="main-desc">"나의 비즈니스 성향과 꼭 맞는 무역 실무 직무는 무엇일까?"</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    수출입 현장에서 마주하는 **20가지 생생한 실무 시나리오**를 통해,  
    자신의 업무 성향을 분석하고 가장 시너지가 날 **6대 무역 직무**와 **성향 궁합 분석·실무 강점·추천 활동·자격증 로드맵**을 매칭해 드립니다!

    ---
    #### 🧭 매칭 대상 6대 핵심 무역 직무
    1. **해외영업 및 시장개척** (Global Sales & Business Development)
    2. **무역사무 및 수출입 오퍼레이션** (Import/Export Operations)
    3. **해외소싱 및 글로벌 바잉 MD** (Global Sourcing & Buying MD)
    4. **글로벌 물류 및 SCM 관리** (Global Logistics & SCM)
    5. **관세·통관·FTA 컨설팅** (Customs Clearance & FTA)
    6. **외환 및 무역금융 리스크 관리** (Trade Finance & FX Management)
    
    소요 시간은 약 **3~5분**입니다. 편안한 마음으로 가장 본능적으로 와닿는 보기를 선택해보세요!
    """)

    st.write("")
    if st.button("🚀 테스트 시작하기", use_container_width=True):
        st.session_state.step = "quiz"
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.session_state.scores_mbti = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        st.session_state.scores_job = {job: 0 for job in JOB_PROFILES.keys()}
        st.session_state.view_rank = 1
        st.rerun()

def render_quiz_page():
    q_idx = st.session_state.current_q
    total_q = len(QUESTIONS)
    q_data = QUESTIONS[q_idx]

    progress = (q_idx + 1) / total_q
    st.progress(progress)
    st.caption(f"문항 진행도: {q_idx + 1} / {total_q} ({int(progress * 100)}%)")

    dimension_names = {
        "EI": "대인 소통 & 에너지 방향", 
        "SN": "시장 인식 & 비즈니스 관점", 
        "TF": "판단 기준 & 문제 해결 스타일", 
        "JP": "실행 방식 & 리스크 대응 스타일"
    }
    category_label = dimension_names.get(q_data["dimension"], "성향 진단")

    st.markdown(f"""
        <div class="question-card">
            <span class="question-badge">Q{q_data['id']}. {category_label}</span>
            <div class="question-text">{q_data['question']}</div>
        </div>
    """, unsafe_allow_html=True)

    letters = ["A", "B", "C", "D"]
    option_texts = [f"{letters[i]}.  {opt['text']}" for i, opt in enumerate(q_data['options'])]

    selected_option = st.radio(
        label="답변을 선택해주세요:",
        options=option_texts,
        index=0,
        label_visibility="collapsed"
    )

    st.write("")
    col1, col2 = st.columns([1, 1])

    with col2:
        btn_label = "다음 문항 ➡️" if q_idx < total_q - 1 else "결과 분석하기 🌊"
        if st.button(btn_label, use_container_width=True):
            chosen_letter = selected_option[0]
            choice_idx = letters.index(chosen_letter) if chosen_letter in letters else 0
            chosen = q_data['options'][choice_idx]
            
            if "type" in chosen and chosen["type"]:
                st.session_state.scores_mbti[chosen["type"]] += 1
                
            for job, wt in chosen.get("job_weights", {}).items():
                if job in st.session_state.scores_job:
                    st.session_state.scores_job[job] += wt

            st.session_state.answers.append(choice_idx)

            if q_idx < total_q - 1:
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.session_state.step = "loading"
                st.rerun()

def render_loading_page():
    """작동이 잘 되는 원본 배 로딩 코드 그대로 유지[cite: 3]"""
    raw_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 110" width="100%" height="100%">
        <polygon points="81,8 100,15 81,22" fill="#FF7043" />
        <line x1="81" y1="8" x2="81" y2="72" stroke="#4E342E" stroke-width="4" stroke-linecap="round"/>
        <path d="M79 14 Q40 44 36 70 L79 70 Z" fill="#FFFDF8" stroke="#3E2723" stroke-width="2.2" stroke-linejoin="round"/>
        <path d="M83 18 Q106 48 98 70 L83 70 Z" fill="#F4EDE0" stroke="#3E2723" stroke-width="2.2" stroke-linejoin="round"/>
        <rect x="60" y="62" width="36" height="13" rx="3" fill="#E65100" stroke="#3E2723" stroke-width="1.6"/>
        <rect x="64" y="65" width="6" height="6" rx="1" fill="#FFFDE7"/>
        <rect x="75" y="65" width="6" height="6" rx="1" fill="#FFFDE7"/>
        <rect x="86" y="65" width="6" height="6" rx="1" fill="#FFFDE7"/>
        <path d="M22 74 C30 96 50 102 80 102 C110 102 130 96 138 74 Z" fill="#D87D2B" stroke="#3E2723" stroke-width="2.2" stroke-linejoin="round"/>
        <path d="M28 78 C40 94 60 98 80 98 C100 98 120 94 132 78 C120 90 100 94 80 94 C60 94 40 90 28 78 Z" fill="#1976D2"/>
    </svg>"""
    
    encoded_svg = urllib.parse.quote(raw_svg)
    img_src = f"data:image/svg+xml;utf8,{encoded_svg}"

    st.markdown(f"""
        <style>
            .sea-stage-img {{
                position: relative;
                width: 100%;
                height: 115px;
                overflow: hidden;
                background: transparent !important;
                line-height: 0 !important;
                font-size: 0 !important;
            }}
            .sailing-ship-img {{
                position: absolute;
                top: 0px;
                width: 110px;
                height: 95px;
                animation: cruise 4.5s linear infinite, floating 1.6s ease-in-out infinite alternate;
                border: none !important;
                outline: none !important;
            }}
            .sailing-ship-img img {{
                width: 100%;
                height: 100%;
                display: block;
                border: none !important;
            }}
            .sea-bottom-cover {{
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 35px;
                background: linear-gradient(180deg, rgba(191, 225, 251, 0) 0%, #BFE1FB 40%, #A7D4F9 100%) !important;
                pointer-events: none;
            }}
        </style>
        <div class="ocean-loading-box">
            <div class="loading-header-text">당신의 무역 MBTI를 분석중입니다...</div>
            <div class="loading-sub-text">20개의 응답 데이터를 바탕으로 최적의 직무를 찾고 있어요 🧭</div>
            <div class="sea-stage-img">
                <div class="sailing-ship-img">
                    <img src="{img_src}" alt="sailing boat" />
                </div>
                <div class="sea-bottom-cover"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    time.sleep(4.5)
    st.session_state.step = "result"
    st.session_state.view_rank = 1
    st.rerun()

def render_result_page():
    # 1. MBTI 산출[cite: 3]
    mbti = ""
    mbti += "E" if st.session_state.scores_mbti["E"] >= st.session_state.scores_mbti["I"] else "I"
    mbti += "S" if st.session_state.scores_mbti["S"] >= st.session_state.scores_mbti["N"] else "N"
    mbti += "T" if st.session_state.scores_mbti["T"] >= st.session_state.scores_mbti["F"] else "F"
    mbti += "J" if st.session_state.scores_mbti["J"] >= st.session_state.scores_mbti["P"] else "P"

    # 2. 직무 점수 랭킹 도출[cite: 3]
    sorted_jobs = sorted(st.session_state.scores_job.items(), key=lambda x: x[1], reverse=True)
    best_job_key = sorted_jobs[0][0]
    second_job_key = sorted_jobs[1][0]
    
    is_viewing_first = (st.session_state.view_rank == 1)
    current_job_key = best_job_key if is_viewing_first else second_job_key
    target_job = JOB_PROFILES[current_job_key]
    rank_badge_text = "🏆 1순위 추천 직무" if is_viewing_first else "🥈 2순위 추천 직무"

    st.markdown(f"""
        <div class="main-header" style="background: linear-gradient(120deg, #FDE2E4, #E2ECE9, #DFE7FD);">
            <div class="main-desc">글로벌 무역 DNA 분석 완료</div>
            <div class="main-title">✨ 무역 MBTI: {mbti} Type ✨</div>
        </div>
    """, unsafe_allow_html=True)

    col_rank_a, col_rank_b = st.columns(2)
    with col_rank_a:
        if st.button("🏆 1순위 직무 보기" + (" (현재)" if is_viewing_first else ""), use_container_width=True):
            st.session_state.view_rank = 1
            st.rerun()
    with col_rank_b:
        if st.button(f"🥈 2순위 직무 보기 [{second_job_key}]" + (" (현재)" if not is_viewing_first else ""), use_container_width=True):
            st.session_state.view_rank = 2
            st.rerun()

    st.write("")

    # 메인 직무 카드[cite: 3]
    st.markdown(f"""
        <div class="result-card" style="border-top: 6px solid {target_job['accent']};">
            <span class="question-badge" style="background-color: {target_job['color']}; color: #2D3748;">{rank_badge_text}</span>
            <div class="result-title">{target_job['title']}</div>
            <div class="result-subtitle">{target_job['subtitle']}</div>
            <div class="tagline-box">💡 "{target_job['tagline']}"</div>
            <p style="font-size: 1.02rem; line-height: 1.6; color: #4A5568; word-break: keep-all;">{target_job['desc']}</p>
        </div>
    """, unsafe_allow_html=True)

    # 성향 매칭 이유[cite: 3]
    why_fit_data = target_job.get("why_fit", {})
    if why_fit_data:
        points_html = "".join([f"<div class='why-fit-item'>• {p}</div>" for p in why_fit_data.get("personality_points", [])])
        st.markdown(f"""
            <div class="why-fit-box">
                <div class="why-fit-header"> 왜 나의 성격과 이 직무가 찰떡궁합일까?</div>
                <div class="why-fit-core">"{why_fit_data.get('core_reason', '')}"</div>
                {points_html}
            </div>
        """, unsafe_allow_html=True)

    # 실무 강점[cite: 3]
    st.markdown(f"### 💡 [{current_job_key}] 실무에서 발휘될 당신의 구체적 강점")
    for item in target_job["detailed_strengths"]:
        st.markdown(f"""
            <div class="strength-card">
                <div class="strength-title">✔ {item['point']}</div>
                <div class="strength-detail">{item['detail']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 자격증 및 추천 대외활동[cite: 3]
    col1, col2 = st.columns(2)
    with col1:
        cert_html_list = ""
        for cert in target_job["certificates"]:
            cert_html_list += f"""
            <div class="cert-item">
                <span class="cert-title">{cert['name']}</span>
                <span class="cert-org">({cert['org']})</span>
                <div class="cert-desc">{cert['desc']}</div>
            </div>
            """

        st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 22px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #EDF2F7; height: 100%;">
                <h4 style="color: #805AD5; margin-top:0; margin-bottom: 14px;">🎓 준비하면 좋은 자격증</h4>
                {cert_html_list}
            </div>
        """, unsafe_allow_html=True)

    with col2:
        activity_html_list = ""
        for act in target_job["recommend_activities"]:
            activity_html_list += f"""
            <div class="activity-item">
                📌 {act}
            </div>
            """

        st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 22px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #EDF2F7; height: 100%;">
                <h4 style="color: #319795; margin-top:0; margin-bottom: 14px;">🚀 직무 맞춤 대외활동 & 인턴 경험</h4>
                {activity_html_list}
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    if is_viewing_first:
        st.info(f"💡 2순위 직무인 [{second_job_key}]도 높은 점수를 기록했습니다. 아래 버튼을 눌러 2순위 직무 분석도 확인해 보세요!")
        if st.button(f"👉 2순위 [{second_job_key}] 직무 상세 분석 보러가기", use_container_width=True):
            st.session_state.view_rank = 2
            st.rerun()
    else:
        st.info(f"💡 현재 **2순위 직무 [{second_job_key}]** 상세 분석을 보고 계십니다. 1순위로 돌아가려면 아래 버튼을 누르세요.")
        if st.button(f"🔙 1순위 [{best_job_key}] 직무 상세 분석으로 돌아가기", use_container_width=True):
            st.session_state.view_rank = 1
            st.rerun()

    st.write("")
    
    # 6대 직무 적합도 점수 랭킹[cite: 3]
    st.markdown("### 📊 나의 6대 무역 직무 적합도 랭킹")
    total_score = sum(st.session_state.scores_job.values())
    for job_key, score in sorted_jobs:
        job_info = JOB_PROFILES[job_key]
        pct = int((score / total_score) * 100) if total_score > 0 else 0
        st.markdown(f"**{job_info['title'].split(',')[1].strip() if ',' in job_info['title'] else job_key}** ({pct}%)")
        st.progress(pct / 100.0)

    st.write("")
    if st.button("🔄 테스트 다시 하기", use_container_width=True):
        st.session_state.step = "start"
        st.session_state.current_q = 0
        st.session_state.answers = []
        st.session_state.view_rank = 1
        st.rerun()

# --- 4. 메인 실행 라우팅 ---
if st.session_state.step == "start":
    render_start_page()
elif st.session_state.step == "quiz":
    render_quiz_page()
elif st.session_state.step == "loading":
    render_loading_page()
elif st.session_state.step == "result":
    render_result_page()