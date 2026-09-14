import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# 1. 파이썬 모듈 검색 경로(sys.path) 등록 (ImportError 방지)
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# 2. 로컬 환경 변수 (.env) 로드
ENV_PATH = CURRENT_DIR.parent.parent / ".env"
PAGES_DIR = CURRENT_DIR / "src" / "pages"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# 3. Streamlit Cloud 배포 환경 Secrets를 os.environ으로 주입
try:
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ[key] = value.strip()
except Exception:
    pass

# 4. 기본 페이지 설정
st.set_page_config(
    page_title="All-in-One Travel Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 5. 사이드바 API 상태 점검
with st.sidebar:
    st.markdown("### 🔑 API 연결 상태")
    openweather_ok = bool(os.getenv("OPENWEATHER_API_KEY"))
    exchange_ok = bool(os.getenv("EXCHANGE_API_KEY"))
    kakao_ok = bool(os.getenv("KAKAO_REST_KEY") or os.getenv("MAP_API_KEY"))
    
    status_text = [
        "✅ 날씨" if openweather_ok else "❌ 날씨",
        "✅ 환율" if exchange_ok else "❌ 환율",
        "✅ 카카오" if kakao_ok else "❌ 카카오"
    ]
    st.caption(" | ".join(status_text))
    
    if not (openweather_ok and exchange_ok and kakao_ok):
        st.warning("⚠️ Secrets 또는 .env 파일의 API 키 설정을 확인해주세요.")
    st.divider()

# 6. 멀티페이지 정의
home_page = st.Page(
    str(PAGES_DIR / "home_korea.py"), 
    title="대한민국 (Home)", 
    icon="🇰🇷", 
    default=True
)

japan_page = st.Page(
    str(PAGES_DIR / "japan.py"), 
    title="일본 (Japan)", 
    icon="🇯🇵"
)

china_page = st.Page(
    str(PAGES_DIR / "china.py"), 
    title="중국 (China)", 
    icon="🇨🇳"
)

usa_page = st.Page(
    str(PAGES_DIR / "usa.py"), 
    title="미국 (USA)", 
    icon="🇺🇸"
)

other_page = st.Page(
    str(PAGES_DIR / "other.py"), 
    title="기타 국가 검색 (Other)", 
    icon="🌐"
)

# 7. 네비게이션 등록 및 실행
pg = st.navigation({
    "홈": [home_page],
    "해외 여행지": [japan_page, china_page, usa_page],
    "기타": [other_page]
})

pg.run()