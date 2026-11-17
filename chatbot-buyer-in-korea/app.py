"""GUESTLY Streamlit 채팅 화면.

실행: streamlit run app.py
"""

import streamlit as st

import config
import graph
import ui_style
import usage

st.set_page_config(page_title="GUESTLY", layout="centered")

EXAMPLES = [
    "강남에서 독일 바이어 2명과 1인 7만 원 정도로 조용한 저녁 식당 추천해 줘",
    "처음 한국에 온 바이어에게 5만 원 이하로 가져가기 편한 한국적인 선물 추천해 줘",
    "채식하는 바이어와 종로에서 점심 먹고, 차를 좋아하셔서 4만 원 이하 선물도 드리고 싶어",
]
MOODS = ["조용함", "개별 룸", "격식 있음", "캐주얼", "전망 좋음", "한국 전통 분위기"]
DIETS = ["채식", "비건", "할랄", "돼지고기 제외", "해산물 제외", "술 안 마심"]
GIFT_STYLES = ["한국적·전통", "실용적", "격식 있음", "가벼운 기념품", "차·식품", "화장품"]
QUICK_MENU = [("restaurant", "식당 추천"), ("gift", "선물 추천"),
              ("both", "식당 + 선물"), ("profile", "바이어 정보 입력")]


def init_state() -> None:
    """대화 기록, 이전 조건, 바이어 정보, 열린 입력 폼을 세션에 준비한다."""
    st.session_state.setdefault("messages", [])        # {"role", "content", "sources"}
    st.session_state.setdefault("prev_conditions", None)
    st.session_state.setdefault("profile", {})         # 바이어 정보 입력 내용
    st.session_state.setdefault("mode", None)          # 열려 있는 입력 폼
    st.session_state.setdefault("pending", None)       # 버튼·폼으로 만든 질문


def reset_chat() -> None:
    """대화 기록과 이전 조건을 지운다 (바이어 정보는 유지)."""
    st.session_state.messages = []
    st.session_state.prev_conditions = None
    st.session_state.mode = None


def set_mode(mode: str | None) -> None:
    """버튼을 누르면 해당 입력 폼을 연다 (같은 버튼을 다시 누르면 닫는다)."""
    st.session_state.mode = None if st.session_state.mode == mode else mode


def ask(question: str) -> None:
    """버튼이나 폼에서 만든 질문을 다음 실행 때 처리하도록 맡겨 둔다."""
    st.session_state.pending = question
    st.session_state.mode = None


def profile_text() -> str:
    """저장된 바이어 정보를 질문 앞에 붙일 한 줄로 만든다."""
    p = st.session_state.profile
    parts = []
    if p.get("company"):
        parts.append(f"바이어 소속: {p['company']}")
    if p.get("people"):
        parts.append(f"인원 {p['people']}명")
    if p.get("purpose"):
        parts.append(f"방문 목적: {p['purpose']}")
    if p.get("diets"):
        parts.append(f"식이 제한: {', '.join(p['diets'])}")
    if p.get("drink") and p["drink"] != "모름":
        parts.append(f"음주: {p['drink']}")
    if p.get("taste"):
        parts.append(f"취향: {p['taste']}")
    return f"[바이어 정보] {', '.join(parts)}" if parts else ""


def render_sidebar() -> None:
    """사이드바에 초기화, 바이어 정보, 기능 소개, 데이터·비용 안내를 보여 준다."""
    with st.sidebar:
        st.markdown('<div class="serif" style="font-size:1.3rem;font-weight:700">의전 수첩</div>',
                    unsafe_allow_html=True)
        st.button("새 대화 시작", on_click=reset_chat, use_container_width=True)

        st.markdown(ui_style.side_label("BUYER · 바이어 정보"), unsafe_allow_html=True)
        info = profile_text().replace("[바이어 정보] ", "")
        safe_info = ui_style.html.escape(info) if info else "아직 입력하지 않았어요."
        st.markdown(f'<div class="gl-side-card">{safe_info}</div>',
                    unsafe_allow_html=True)
        st.button("바이어 정보 입력·수정", on_click=set_mode, args=("profile",),
                  use_container_width=True)

        st.markdown(ui_style.side_label("GUIDE · 할 수 있는 일"), unsafe_allow_html=True)
        st.markdown(
            '<div class="gl-side-card"><b>식당</b> 지역·인원·예산·분위기·식이 제한<br>'
            '<b>선물</b> 예산·취향·휴대성·격식<br>'
            '<b>후속 요청</b> "좀 더 저렴한 곳으로"</div>', unsafe_allow_html=True)

        st.markdown(ui_style.side_label("BUDGET · 예상 사용액"), unsafe_allow_html=True)
        day, month = usage.spent_totals()
        st.progress(min(day / config.DAILY_BUDGET_USD, 1.0),
                    text=f"오늘 ${day:.4f} / ${config.DAILY_BUDGET_USD:.2f}")
        st.progress(min(month / config.MONTHLY_BUDGET_USD, 1.0),
                    text=f"이번 달 ${month:.4f} / ${config.MONTHLY_BUDGET_USD:.2f}")
        st.caption("이 컴퓨터의 기록 기준이며 실제 청구액과 다를 수 있어요. "
                   "식당 24곳·선물 24개·의전 지침 12개는 모두 가상 데이터예요.")


def restaurant_question(region, people, budget, meal, moods, diets, extra) -> str:
    """식당 폼 입력값을 자연스러운 질문 문장으로 바꾼다."""
    text = f"{region}에서 {people}명이 {meal} 식사를 하려고 해. 1인당 {budget}만 원 정도"
    if moods:
        text += f", 분위기는 {', '.join(moods)}"
    if diets:
        text += f", 식이 제한은 {', '.join(diets)}"
    if extra:
        text += f", {extra}"
    return text + "인 식당을 추천해 줘."


def gift_question(budget, styles, portable, extra) -> str:
    """선물 폼 입력값을 자연스러운 질문 문장으로 바꾼다."""
    text = f"바이어에게 {budget}만 원 이하 선물을 주고 싶어"
    if styles:
        text += f". {', '.join(styles)} 느낌이면 좋겠어"
    if portable:
        text += ". 작고 가벼워서 가져가기 편한 것"
    if extra:
        text += f". {extra}"
    return text + ". 추천해 줘."


def restaurant_fields(key: str) -> tuple:
    """식당 조건 입력칸을 그리고 입력값을 돌려준다."""
    c1, c2, c3 = st.columns(3)
    region = c1.selectbox("지역", config.REGIONS, key=f"{key}_region")
    people = c2.number_input("인원", 1, 30, st.session_state.profile.get("people") or 2, key=f"{key}_people")
    budget = c3.number_input("1인 예산(만 원)", 1, 30, 7, key=f"{key}_budget")
    meal = st.radio("식사", ["점심", "저녁"], index=1, horizontal=True, key=f"{key}_meal")
    moods = st.multiselect("분위기", MOODS, key=f"{key}_moods")
    diets = st.multiselect("식이 제한", DIETS, default=st.session_state.profile.get("diets", []),
                           key=f"{key}_diets")
    return region, people, budget, meal, moods, diets


def gift_fields(key: str) -> tuple:
    """선물 조건 입력칸을 그리고 입력값을 돌려준다."""
    budget = st.number_input("선물 예산(만 원 이하)", 1, 50, 5, key=f"{key}_gbudget")
    styles = st.multiselect("선물 느낌", GIFT_STYLES, key=f"{key}_styles")
    portable = st.checkbox("작고 가벼운 것 (귀국할 때 가져가기 편하게)", value=True, key=f"{key}_portable")
    return budget, styles, portable


def render_form() -> None:
    """버튼으로 연 입력 폼을 그리고, 제출하면 질문을 만든다."""
    mode = st.session_state.mode
    if mode == "restaurant":
        with st.form("restaurant_form"):
            st.markdown("**식당 조건**")
            values = restaurant_fields("r")
            extra = st.text_input("그 밖의 요청 (선택)", placeholder="예: 한국 전통 음식을 경험하게 해 드리고 싶어")
            if st.form_submit_button("식당 추천 받기", type="primary"):
                ask(restaurant_question(*values, extra))
                st.rerun()
    elif mode == "gift":
        with st.form("gift_form"):
            st.markdown("**선물 조건**")
            values = gift_fields("g")
            extra = st.text_input("받는 분 취향 (선택)", placeholder="예: 차를 좋아하심")
            if st.form_submit_button("선물 추천 받기", type="primary"):
                ask(gift_question(*values, extra))
                st.rerun()
    elif mode == "both":
        with st.form("both_form"):
            st.markdown("**식당 조건**")
            r = restaurant_fields("b")
            st.markdown("**선물 조건**")
            g = gift_fields("b")
            extra = st.text_input("그 밖의 요청 (선택)")
            if st.form_submit_button("함께 추천 받기", type="primary"):
                question = (restaurant_question(*r, "").rstrip(".") + " 그리고 "
                            + gift_question(*g, extra))
                ask(question)
                st.rerun()
    elif mode == "profile":
        p = st.session_state.profile
        with st.form("profile_form"):
            st.markdown("**바이어 정보** — 저장하면 다음 질문부터 함께 반영돼요.")
            company = st.text_input("바이어 소속·이름 (선택)", p.get("company", ""))
            c1, c2 = st.columns(2)
            people = c1.number_input("방문 인원 (우리 측 포함)", 1, 30, p.get("people") or 2)
            drink = c2.radio("음주", ["모름", "마심", "안 마심"], horizontal=True,
                             index=["모름", "마심", "안 마심"].index(p.get("drink", "모름")))
            purpose = st.text_input("방문 목적 (선택)", p.get("purpose", ""), placeholder="예: 첫 미팅, 계약 체결")
            diets = st.multiselect("식이 제한", DIETS, default=p.get("diets", []))
            taste = st.text_input("취향 (선택)", p.get("taste", ""), placeholder="예: 차를 좋아함, 매운 음식은 어려움")
            st.caption("국적만으로 취향을 짐작하지 않아요. 본인에게 확인한 내용을 적어 주세요.")
            if st.form_submit_button("저장", type="primary"):
                st.session_state.profile = {"company": company, "people": people, "drink": drink,
                                            "purpose": purpose, "diets": diets, "taste": taste}
                st.session_state.mode = None
                st.rerun()


def render_start() -> None:
    """첫 화면: 빠른 시작 버튼, 입력 폼, 예시 질문 버튼을 보여 준다."""
    st.markdown(ui_style.section("무엇을 도와드릴까요?"), unsafe_allow_html=True)
    with st.container(key="quick"):
        cols = st.columns(2)
        for i, (mode, label) in enumerate(QUICK_MENU):
            selected = st.session_state.mode == mode
            cols[i % 2].button(label, on_click=set_mode, args=(mode,), use_container_width=True,
                               type="primary" if selected else "secondary")
    render_form()
    st.markdown(ui_style.section("이렇게 물어보세요"), unsafe_allow_html=True)
    with st.container(key="examples"):
        for example in EXAMPLES:
            st.button(f"→  {example}", on_click=ask, args=(example,), use_container_width=True)


def render_message(message: dict) -> None:
    """채팅 메시지 하나와 출처를 그린다."""
    role = message["role"]
    with st.chat_message(role):
        st.markdown(ui_style.role_marker(role), unsafe_allow_html=True)
        st.markdown(message["content"])
        if message.get("profile"):
            st.markdown(f'<div class="gl-profile-tag">{ui_style.html.escape(message["profile"])}</div>',
                        unsafe_allow_html=True)
        if message.get("sources"):
            st.markdown(ui_style.sources_html(message["sources"]), unsafe_allow_html=True)


def recent_history() -> list[dict]:
    """모델에 넘길 최근 대화(최대 4개)를 만든다."""
    recent = st.session_state.messages[-config.MAX_HISTORY_MESSAGES:]
    return [{"role": m["role"], "content": m["content"]} for m in recent]


def answer_question(question: str) -> dict:
    """질문을 그래프에 넣어 답변을 받고, 문제가 생기면 쉬운 안내 문구로 바꾼다."""
    try:
        result = graph.run(question, recent_history(), st.session_state.prev_conditions)
    except (usage.BudgetError, RuntimeError, ValueError) as error:
        return {"role": "assistant", "content": f"{error}", "sources": []}
    except Exception as error:  # 예상하지 못한 오류 (자세한 내용은 터미널에만)
        print(f"[GUESTLY 오류] {type(error).__name__}: {error}")
        return {"role": "assistant",
                "content": "답변을 만드는 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요. "
                           "계속되면 인터넷 연결과 API 키 설정을 확인해 주세요.",
                "sources": []}
    conditions = result.get("conditions") or {}
    if conditions.get("intent") not in (None, "unsupported"):
        st.session_state.prev_conditions = conditions  # 후속 질문에서 유지할 조건
    return {"role": "assistant", "content": result["answer"],
            "sources": result.get("sources", [])}


def handle(question: str) -> None:
    """질문 하나를 처리해 대화 기록에 더한다. 바이어 정보가 있으면 함께 보낸다."""
    info = profile_text()
    user_message = {"role": "user", "content": question, "sources": [], "profile": info}
    render_message(user_message)
    with st.spinner("문서를 찾아보고 있어요..."):
        reply = answer_question(f"{info}\n{question}" if info else question)
    st.session_state.messages += [user_message, reply]
    render_message(reply)


def main() -> None:
    """화면 전체를 그리고 입력을 처리한다."""
    init_state()
    st.markdown(ui_style.CSS, unsafe_allow_html=True)
    render_sidebar()
    st.markdown(ui_style.HERO, unsafe_allow_html=True)

    if not st.session_state.messages:
        render_start()
    elif st.session_state.mode == "profile":
        render_form()  # 대화 중에도 사이드바에서 바이어 정보를 고칠 수 있게

    for message in st.session_state.messages:
        render_message(message)

    typed = st.chat_input("바이어 정보와 원하는 조건을 적어 주세요")
    question = typed or st.session_state.pending
    st.session_state.pending = None
    if question:
        handle(question)
        st.rerun()  # 첫 화면 정리와 사이드바 사용액 갱신


if __name__ == "__main__":
    main()
