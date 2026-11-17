"""GUESTLY 화면 꾸밈 (한지 위의 비즈니스 서신 콘셉트). 새 라이브러리 없이 CSS만 쓴다."""

import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap');

:root {
  --paper: #F5EFE3;
  --paper-deep: #EAE1CF;
  --ink: #1E2633;
  --ink-soft: #5B6372;
  --vermilion: #B4432B;
  --celadon: #5E8C7F;
  --line: rgba(30, 38, 51, 0.14);
}

/* 한지 결: 아주 옅은 섬유 무늬와 빛 번짐 */
.stApp {
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(180, 67, 43, 0.07), transparent 60%),
    radial-gradient(900px 600px at -10% 110%, rgba(94, 140, 127, 0.08), transparent 60%),
    repeating-linear-gradient(97deg, rgba(30, 38, 51, 0.012) 0 2px, transparent 2px 7px),
    var(--paper);
}
html, body, .stApp, .stMarkdown, button, input, textarea {
  font-family: 'IBM Plex Sans KR', sans-serif;
}
h1, h2, h3, .serif { font-family: 'Gowun Batang', serif !important; letter-spacing: -0.01em; }
.block-container { padding-top: 2.2rem; max-width: 780px; }
header[data-testid="stHeader"] { background: transparent; }

/* 머리글: 서신 윗부분처럼 */
.gl-hero { position: relative; padding: 0.4rem 0 1.4rem; margin-bottom: 1.2rem;
  border-bottom: 1px solid var(--line); animation: gl-rise .7s ease both; }
.gl-hero::after { content: ""; position: absolute; left: 0; bottom: -4px; width: 100%;
  border-bottom: 1px solid var(--line); }
.gl-eyebrow { font-size: .72rem; letter-spacing: .28em; color: var(--ink-soft); text-transform: uppercase; }
.gl-title { display: flex; align-items: center; gap: .9rem; margin: .5rem 0 .4rem; }
.gl-seal { width: 52px; height: 52px; flex: none; display: grid; place-items: center;
  background: var(--vermilion); color: #FBF3E6; border-radius: 6px;
  font-family: 'Gowun Batang', serif; font-size: 1.75rem; font-weight: 700;
  box-shadow: inset 0 0 0 3px rgba(251, 243, 230, .35), 0 6px 18px rgba(180, 67, 43, .25);
  transform: rotate(-4deg); }
.gl-wordmark { font-family: 'Gowun Batang', serif; font-size: 2.6rem; font-weight: 700;
  color: var(--ink); line-height: 1; letter-spacing: .04em; }
.gl-lede { color: var(--ink-soft); font-size: 1rem; margin: 0; }
.gl-note { display: inline-flex; align-items: center; gap: .45rem; margin-top: .9rem;
  font-size: .78rem; color: var(--celadon); border: 1px solid rgba(94, 140, 127, .45);
  border-radius: 999px; padding: .2rem .75rem; background: rgba(94, 140, 127, .06); }

.gl-section { font-family: 'Gowun Batang', serif; font-size: 1.05rem; color: var(--ink);
  margin: 1.2rem 0 .6rem; display: flex; align-items: center; gap: .6rem; }
.gl-section::after { content: ""; flex: 1; border-bottom: 1px dashed var(--line); }

/* 빠른 시작 버튼: 명함 카드처럼 */
.st-key-quick .stButton > button {
  min-height: 74px; justify-content: flex-start; text-align: left; padding: .9rem 1.1rem;
  background: #FBF7EF; border: 1px solid var(--line); border-left: 4px solid var(--celadon);
  border-radius: 10px; color: var(--ink); font-weight: 600; font-size: .98rem;
  box-shadow: 0 1px 0 rgba(30, 38, 51, .04); transition: transform .18s ease, box-shadow .18s ease, border-color .18s;
}
.st-key-quick .stButton > button div, .st-key-examples .stButton > button div { justify-content: flex-start; text-align: left; }
.st-key-quick .stButton > button:hover { transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(30, 38, 51, .08); border-left-color: var(--vermilion); color: var(--ink); }
.st-key-quick .stButton > button[kind="primary"] { background: var(--ink); color: #F5EFE3;
  border-color: var(--ink); border-left-color: var(--vermilion); }
.st-key-quick > div { animation: gl-rise .6s ease both; }

/* 예시 질문: 인용문처럼 가볍게 */
.st-key-examples .stButton > button {
  justify-content: flex-start; text-align: left; background: transparent; border: none;
  border-bottom: 1px solid var(--line); border-radius: 0; color: var(--ink-soft);
  padding: .7rem .2rem; font-size: .92rem;
}
.st-key-examples .stButton > button:hover { color: var(--vermilion); background: rgba(180, 67, 43, .04); }

/* 입력 폼 */
[data-testid="stForm"] { background: #FBF7EF; border: 1px solid var(--line); border-radius: 12px;
  padding: 1.2rem 1.3rem; animation: gl-rise .35s ease both; }

/* 채팅 말풍선 */
[data-testid="stChatMessage"] { background: transparent; padding: .2rem 0; animation: gl-rise .4s ease both; }
/* 말풍선 옆 아이콘: 질문은 청자색, 답변은 주홍색 바탕에 흰 아이콘 */
[data-testid="stChatMessage"] > div:first-child { border-radius: 8px; color: #FFFFFF; border: none; }
[data-testid="stChatMessage"] > div:first-child svg { fill: #FFFFFF; color: #FFFFFF; }
[data-testid="stChatMessage"]:has(.gl-msg-user) > div:first-child { background: var(--celadon); }
[data-testid="stChatMessage"]:has(.gl-msg-assistant) > div:first-child { background: var(--vermilion); }
[data-testid="stChatMessage"]:has(.gl-msg-assistant) [data-testid="stChatMessageContent"] {
  background: #FFFDF8; border: 1px solid var(--line); border-top: 3px solid var(--vermilion);
  border-radius: 4px 12px 12px 12px; padding: 1rem 1.25rem; box-shadow: 0 8px 24px rgba(30, 38, 51, .06); }
[data-testid="stChatMessage"]:has(.gl-msg-user) [data-testid="stChatMessageContent"] {
  background: rgba(94, 140, 127, .10); border: 1px solid rgba(94, 140, 127, .25);
  border-radius: 12px 4px 12px 12px; padding: .7rem 1rem; }
[data-testid="stChatMessageContent"] strong { color: var(--ink); }
[data-testid="stChatMessageContent"] h1, [data-testid="stChatMessageContent"] h2 { font-size: 1.1rem; }

/* 출처 칩 */
.gl-sources { margin-top: .9rem; padding-top: .7rem; border-top: 1px dashed var(--line); }
.gl-sources-label { font-size: .72rem; letter-spacing: .2em; color: var(--ink-soft); margin-bottom: .4rem; }
.gl-chip { display: inline-block; margin: 0 .35rem .35rem 0; padding: .18rem .6rem;
  font-family: 'IBM Plex Mono', monospace; font-size: .74rem; color: var(--ink);
  background: var(--paper-deep); border-radius: 4px; border: 1px solid var(--line); }
.gl-profile-tag { font-size: .78rem; color: var(--celadon); margin-top: .35rem; }

/* 입력창 */
[data-testid="stChatInput"] textarea { font-size: .98rem; }
[data-testid="stChatInput"] > div { border-radius: 14px; border-color: rgba(30, 38, 51, .25);
  background: #FFFDF8; box-shadow: 0 8px 26px rgba(30, 38, 51, .08); }
[data-testid="stBottom"] > div { background: linear-gradient(180deg, rgba(245, 239, 227, 0) 0%, var(--paper) 30%); }

/* 사이드바: 먹색 의전 수첩 */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1E2633 0%, #252F3F 100%); }
[data-testid="stSidebar"] * { color: #E9E2D3; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FBF3E6; }
[data-testid="stSidebar"] .stButton > button { background: transparent; border: 1px solid rgba(233, 226, 211, .35); }
[data-testid="stSidebar"] .stButton > button:hover { border-color: var(--vermilion); color: #FFFFFF; }
[data-testid="stSidebar"] [data-testid="stProgress"] p { font-size: .82rem; }
.gl-side-label { font-size: .7rem; letter-spacing: .25em; color: #B9B19F !important; margin: 1.3rem 0 .4rem; }
.gl-side-card { border: 1px solid rgba(233, 226, 211, .2); border-radius: 10px; padding: .7rem .85rem;
  font-size: .85rem; line-height: 1.55; background: rgba(255, 255, 255, .03); }

@keyframes gl-rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
"""

HERO = """
<div class="gl-hero">
  <div class="gl-eyebrow">Business Hospitality · Seoul</div>
  <div class="gl-title"><div class="gl-seal">客</div><div class="gl-wordmark">GUESTLY</div></div>
  <p class="gl-lede">한국을 찾은 해외 바이어를 위한 식당·선물 추천. 조건을 알려 주시면 문서에서 근거를 찾아 드려요.</p>
  <div class="gl-note">● 실습용 가상 데이터 — 실제 상호·상품·주소·연락처가 아니에요</div>
</div>
"""


def section(title: str) -> str:
    """점선이 이어지는 작은 구역 제목 HTML을 만든다."""
    return f'<div class="gl-section">{html.escape(title)}</div>'


def side_label(text: str) -> str:
    """사이드바 구역 이름 HTML을 만든다."""
    return f'<div class="gl-side-label">{html.escape(text)}</div>'


def sources_html(sources: list[str]) -> str:
    """출처 목록을 칩 모양 HTML로 만든다 (글자는 이스케이프)."""
    chips = "".join(f'<span class="gl-chip">{html.escape(s)}</span>' for s in sources)
    return f'<div class="gl-sources"><div class="gl-sources-label">출처</div>{chips}</div>'


def role_marker(role: str) -> str:
    """말풍선 모양을 구분하기 위한 보이지 않는 표시를 만든다."""
    return f'<span class="gl-msg-{role}"></span>'
