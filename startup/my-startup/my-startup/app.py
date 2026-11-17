"""한 줄 회고 보드 — F1(한 줄 기록) + F2(기분 태그). 실행: streamlit run app.py"""
from datetime import date

import streamlit as st

import logic
import storage

st.set_page_config(page_title="한 줄 회고 보드", page_icon="📝")
st.title("📝 한 줄 회고 보드")

st.session_state.setdefault("n", 0)      # 입력칸을 비우기 위한 번호
st.session_state.setdefault("flash", None)

MOOD_NAMES = dict(logic.MOODS)

read_error = None
try:
    entries = storage.read_entries()
except storage.StorageError as e:
    read_error = str(e)
    entries = []

streak_days, wrote_today = logic.streak_info(entries, date.today())
st.markdown(f"### 🔥 연속 기록 {streak_days}일째")
if streak_days > 0 and not wrote_today:
    st.caption(logic.MSG_KEEP_STREAK)

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = None

st.markdown("#### 이번 주 요약 (월~일)")
summary = logic.week_summary(entries, date.today())
if summary is None:
    st.info(logic.MSG_NO_WEEK)
else:
    st.write(f"기록 수: **{summary['count']}개**")
    if summary["top_moods"]:
        moods_text = " · ".join(f"{m} {MOOD_NAMES[m]}" for m in summary["top_moods"])
    else:
        moods_text = logic.NO_MOOD_MARK
    st.write(f"가장 많은 기분: **{moods_text}**")
    longest = summary["longest"]
    st.write(f"가장 긴 한 줄: **{longest['text']}** ({longest['date']})")

with st.form("add"):
    raw = st.text_input("오늘의 한 줄 (100자까지)", key=f"line_{st.session_state.n}")
    mood = st.radio(
        "오늘 기분 (하나를 꼭 골라 주세요)",
        logic.MOOD_EMOJIS,
        index=None,
        horizontal=True,
        format_func=lambda e: f"{e} {MOOD_NAMES[e]}",
        key=f"mood_{st.session_state.n}",
    )
    submitted = st.form_submit_button("저장")

if submitted:
    problems = [p for p in (logic.validate_text(raw), logic.validate_mood(mood)) if p]
    if problems:
        for p in problems:
            st.error(p)
    else:
        try:
            storage.append_entry(logic.make_entry(raw, date.today(), mood))
        except storage.StorageError as e:
            st.error(str(e))
        else:
            st.session_state.n += 1
            st.session_state.flash = "저장했어요!"
            st.rerun()

st.subheader("기록")
if read_error:
    st.error(read_error)

# 저장하면 번호(n)가 바뀌어 검색칸도 비워져요. (검색어가 남아 있으면 방금 쓴 글이 안 보일 수 있어서)
query = st.text_input(
    "단어 검색 (치고 Enter · 비우면 전체 기록)", key=f"search_{st.session_state.n}"
)

if not entries:
    st.info(logic.MSG_NO_ENTRIES)
else:
    shown = logic.search_entries(entries, query)
    if not shown:
        st.info(logic.MSG_NO_RESULT)
    for e in logic.sort_newest_first(shown):
        st.write(f"**{e['date']}**  {logic.mood_display(e['mood'])}  {e['text']}")
