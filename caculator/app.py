import base64
import os
import requests
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# 1. 파일 및 디렉터리 경로 정의
# ==========================================
CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent              # caculator 폴더
PROJECT_ROOT = APP_DIR.parent             # AX_2 (최상위 루트 폴더)

# ==========================================
# 2. 폰트 Base64 인코딩 (에이투지체 로드)
# ==========================================
def get_font_base64(font_filename):
    for base_dir in [PROJECT_ROOT, APP_DIR]:
        font_path = base_dir / font_filename
        if font_path.exists():
            with open(font_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return None

font_regular_b64 = get_font_base64("에이투지체-4Regular.ttf")
font_semibold_b64 = get_font_base64("에이투지체-6SemiBold.ttf")

# ==========================================
# 3. 환경 변수 로드
# ==========================================
ROOT_ENV = PROJECT_ROOT / ".env"
LOCAL_ENV = APP_DIR / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
elif LOCAL_ENV.exists():
    load_dotenv(dotenv_path=LOCAL_ENV)
else:
    load_dotenv()

# API 키 읽기 (공백 제거)
OPENWEATHER_API_KEY = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
EXCHANGE_API_KEY = (os.getenv("EXCHANGE_API_KEY") or "").strip()

# ==========================================
# 4. 페이지 설정
# ==========================================
st.set_page_config(page_title="떠나자 해외여행", page_icon="✈️", layout="wide")

# ==========================================
# 5. 커스텀 CSS (아이콘 폰트 보존 + 에이투지체 적용)
# ==========================================
font_face_css = ""
if font_regular_b64:
    font_face_css += f"""
    @font-face {{
        font-family: 'A2Z';
        src: url(data:font/truetype;charset=utf-8;base64,{font_regular_b64}) format('truetype');
        font-weight: 400;
        font-style: normal;
    }}
    """
if font_semibold_b64:
    font_face_css += f"""
    @font-face {{
        font-family: 'A2Z';
        src: url(data:font/truetype;charset=utf-8;base64,{font_semibold_b64}) format('truetype');
        font-weight: 600;
        font-style: normal;
    }}
    """

st.markdown(f"""
<style>
    {font_face_css}

    /* 1. 기본 본문 텍스트: 에이투지체 레귤러 */
    html, body, .stApp, p, label, input, button, select, [data-baseweb="tab"] {{
        font-family: 'A2Z', -apple-system, BlinkMacSystemFont, "Pretendard", sans-serif !important;
        font-weight: 400 !important;
    }}

    /* Streamlit 기본 머티리얼 아이콘 폰트 강제 보존 (화살표 텍스트 깨짐 및 글자 겹침 방지) */
    [data-testid="stIconMaterial"], 
    .material-symbols-rounded, 
    .material-icons,
    span[data-testid="stExpanderIcon"],
    [data-testid="stExpanderToggleIcon"] {{
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }}

    /* expander 아코디언 제목 및 내용 글씨체 지정 */
    details[data-testid="stExpander"] summary p,
    [data-testid="stExpanderDetails"] p,
    [data-testid="stExpanderDetails"] div {{
        font-family: 'A2Z', sans-serif !important;
    }}

    /* 전체 배경: 웜 그레이지 */
    .stApp {{
        background: linear-gradient(180deg, #F5F6F5 0%, #EBECE9 100%) !important;
        color: #2F3E46 !important;
    }}

    /* 2. 제목 및 주요 헤더: 에이투지체 세미볼드 */
    h1, h2, h3, h4, h5, h6,
    .stHeadingContainer h1, .stHeadingContainer h2, .stHeadingContainer h3,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {{
        font-family: 'A2Z', -apple-system, BlinkMacSystemFont, "Pretendard", sans-serif !important;
        font-weight: 600 !important;
        color: #354F52 !important;
    }}

    /* 메트릭 텍스트 줄바꿈 및 색상 */
    [data-testid="stMetricValue"] {{
        white-space: normal !important;
        word-break: keep-all !important;
        font-size: 1.35rem !important;
        color: #2F3E46 !important;
    }}
    [data-testid="stMetricLabel"] {{
        white-space: normal !important;
        word-break: keep-all !important;
        color: #52796F !important;
    }}

    /* 슬라이더 바 세이지 톤온톤 */
    div[data-baseweb="slider"] > div > div {{ background-color: #DDE2DA !important; }}
    div[data-baseweb="slider"] > div > div > div {{ background-color: #728B80 !important; }}
    div[data-baseweb="slider"] [role="slider"] {{
        background-color: #587166 !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12) !important;
    }}
    div[data-baseweb="popover"] div, div[role="tooltip"] {{
        background-color: #4A5D54 !important;
        color: #F8F9FA !important;
    }}

    /* 날씨 모던 배지 */
    .weather-box {{
        display: flex;
        align-items: center;
        gap: 16px;
        background: rgba(255, 255, 255, 0.65);
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid #D8DDD6;
    }}
    .weather-svg {{
        width: 60px;
        height: 60px;
        flex-shrink: 0;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.06));
    }}
    .weather-desc-badge {{
        display: inline-block;
        background-color: #E2E8E4;
        color: #354F52;
        padding: 2px 8px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 4px;
    }}

    /* 모바일 반응형 최적화 (화면 폭 768px 이하) */
    @media (max-width: 768px) {{
        h1 {{
            font-size: 1.8rem !important;
        }}
        div[data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 12px !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.15rem !important;
        }}
        .weather-box {{
            padding: 12px 14px !important;
            gap: 12px !important;
        }}
        .weather-svg {{
            width: 50px !important;
            height: 50px !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 여행지 데이터베이스
# ==========================================
DESTINATIONS = {
    "도쿄 (Tokyo, 일본)": {
        "city_en": "Tokyo",
        "currency": "JPY",
        "timezone": "Asia/Tokyo",
        "time_diff_desc": "한국과 시차 없음 (동일)",
        "best_season": "3월–5월 (봄 벚꽃), 10월–11월 (단풍과 쾌적한 날씨)",
        "visa": "90일 무비자 입국",
        "voltage": "100V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음 (영수증 정가 지불)",
        "transport_tip": "스이카(Suica)/파스모 카드 또는 도쿄 서브웨이 티켓",
        "price_compare": {
            "커피 1잔 (스벅 톨)": "약 4,500원\n(한국과 유사)",
            "대중교통 기본요금": "약 1,800원\n(한국보다 약간 높음)",
            "식당 한 끼 식사": "약 9,000~15,000원\n(선택 폭 넓음)"
        },
        "themes": {
            "🏛️ 랜드마크 & 역사": ["센소지 (아사쿠사)", "메이지 신궁", "도쿄 타워"],
            "🛍️ 쇼핑 & 거리": ["긴자 명품 거리", "시부야 스크램블 교차로", "오모테산도 & 캣스트리트"],
            "🌿 힐링 & 공원": ["신주쿠 교엔 국립정원", "우에노 온시 공원"],
            "📸 인생샷 명소": ["시부야 스카이 전망대", "팀랩 플래닛 도쿄"]
        },
        "restaurants": [
            {"name": "이치란 라멘 (본점/시부야)", "menu": "돈코츠 라멘", "tip": "비밀 소스 맵기 조절 가능, 1인 좌석 완비"},
            {"name": "규카츠 모토무라", "menu": "규카츠 정식", "tip": "미니 화로에 직접 구워 먹는 재미, 오픈런 추천"},
            {"name": "미도리 스시", "menu": "모둠 초밥", "tip": "가성비 뛰어난 현지 인기 스시 체인"}
        ]
    },
    "오사카 (Osaka, 일본)": {
        "city_en": "Osaka",
        "currency": "JPY",
        "timezone": "Asia/Tokyo",
        "time_diff_desc": "한국과 시차 없음 (동일)",
        "best_season": "3월–5월 (봄 벚꽃), 9월–11월 (선선한 가을 날씨)",
        "visa": "90일 무비자 입국",
        "voltage": "100V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음",
        "transport_tip": "오사카 주유패스 (관광지 무료입장) 또는 이코카(ICOCA) 카드",
        "price_compare": {
            "커피 1잔": "약 4,200원\n(한국과 유사)",
            "대중교통 기본요금": "약 2,000원\n(한국 대비 높음)",
            "타코야키/라멘": "약 7,000~12,000원\n(길거리 음식 발달)"
        },
        "themes": {
            "🏛️ 랜드마크 & 역사": ["오사카성 천수각", "시텐노지 사찰"],
            "🛍️ 쇼핑 & 거리": ["도톤보리 거리", "신사이바시스지 아케이드", "우메다 한큐백화점"],
            "🌿 힐링 & 테마파크": ["유니버설 스튜디오 재팬 (USJ)", "나카노시마 공원"],
            "📸 인생샷 명소": ["도톤보리 글리코상 앞", "우메다 공중정원 전망대"]
        },
        "restaurants": [
            {"name": "앗치치혼포", "menu": "타코야키", "tip": "도톤보리 강변 앞, 타코폰즈 소스 조합 추천"},
            {"name": "모토무라 규카츠 난바점", "menu": "규카츠", "tip": "점심 피크를 피해 14시 이후 방문 권장"},
            {"name": "키지 (우메다)", "menu": "오코노미야키", "tip": "우메다 스카이빌딩 지하 레트로 식당가 위치"}
        ]
    },
    "다낭 (Da Nang, 베트남)": {
        "city_en": "Da Nang",
        "currency": "VND",
        "timezone": "Asia/Ho_Chi_Minh",
        "time_diff_desc": "한국보다 2시간 느림",
        "best_season": "2월–5월 (건기 시즌으로 비가 적고 쾌적함)",
        "visa": "45일 무비자 입국",
        "voltage": "220V (한국 전자제품 호환)",
        "tipping": "의무는 아니나 마사지샵은 2~5만동 매너 팁 일반적",
        "transport_tip": "그랩(Grab) 앱 호출이 가장 저렴하고 안전함",
        "price_compare": {
            "코코넛 커피 1잔": "약 2,000~2,800원\n(매우 저렴)",
            "그랩 택시 기본요금": "약 1,200원\n(부담 없는 이동)",
            "쌀국수 한 그릇": "약 2,500~4,000원\n(가성비 최상)"
        },
        "themes": {
            "🏛️ 랜드마크 & 역사": ["다낭 대성당 (핑크성당)", "영흥사 (해수관음상)", "오행산(마블마운틴)"],
            "🛍️ 쇼핑 & 로컬": ["한시장 (아오자이/크록스/라탄)", "선짜 야시장"],
            "🌿 힐링 & 휴양": ["미케 비치 해변 산책", "호이안 올드타운 투어"],
            "📸 인생샷 명소": ["바나힐 골든브릿지 (신의 손)", "용다리 야경 및 불쇼"]
        },
        "restaurants": [
            {"name": "포홍 (Pho Hong)", "menu": "소고기 쌀국수", "tip": "로컬 1등 쌀국수, 바삭한 꿔이를 국물에 곁들이기"},
            {"name": "마담란", "menu": "반쎄오, 분짜", "tip": "에어컨과 쾌적한 인테리어를 갖춘 대형 레스토랑"},
            {"name": "콩카페 (Cong Caphe)", "menu": "코코넛 스무디 커피", "tip": "한강변 뷰를 보며 여유롭게 힐링하기 좋음"}
        ]
    },
    "타이베이 (Taipei, 대만)": {
        "city_en": "Taipei",
        "currency": "TWD",
        "timezone": "Asia/Taipei",
        "time_diff_desc": "한국보다 1시간 느림",
        "best_season": "10월–12월 및 3월–4월 (선선하고 걷기 좋은 기온)",
        "visa": "90일 무비자 입국",
        "voltage": "110V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음 (고급 식당만 10% 봉사료 부과)",
        "transport_tip": "이지카드(EasyCard) 구매 필수 (지하철, 버스 공용)",
        "price_compare": {
            "버블티 1잔 (라지)": "약 2,500~3,500원\n(한국의 절반 수준)",
            "MRT 기본요금": "약 900원\n(한국보다 훨씬 저렴)",
            "우육면 한 그릇": "약 7,000~9,500원\n(푸짐한 고기 양)"
        },
        "themes": {
            "🏛️ 랜드마크 & 역사": ["중정기념당", "국립고궁박물원", "용산사"],
            "🛍️ 쇼핑 & 야시장": ["스린 야시장", "라오허제 야시장", "시먼딩 젊음의 거리"],
            "🌿 힐링 & 자연": ["양명산 국립공원", "베이터우 유황 온천"],
            "📸 인생샷 명소": ["타이베이 101 전망대", "지우펀 홍등거리 (센과 치히로 배경)"]
        },
        "restaurants": [
            {"name": "딘타이펑 본점", "menu": "샤오롱바오", "tip": "현장 번호표 발급 후 주변 거리 산책 추천"},
            {"name": "융캉우육면", "menu": "홍샤오 우육면", "tip": "진한 소고기 육수와 쫄깃한 면발의 조화"},
            {"name": "삼형매 빙수", "menu": "망고 눈꽃빙수", "tip": "시먼딩 대표 디저트로 식후 방문 추천"}
        ]
    },
    "방콕 (Bangkok, 태국)": {
        "city_en": "Bangkok",
        "currency": "THB",
        "timezone": "Asia/Bangkok",
        "time_diff_desc": "한국보다 2시간 느림",
        "best_season": "11월–2월 (건기 시즌으로 가장 시원하고 쾌적함)",
        "visa": "90일 무비자 입국",
        "voltage": "220V (한국 플러그 대부분 호환)",
        "tipping": "마사지샵 50~100바트, 호텔 벨보이 20~40바트 권장",
        "transport_tip": "출퇴근 시간에는 지상철(BTS)/지하철(MRT) 이용",
        "price_compare": {
            "땡모반 (수박주스)": "약 1,800~2,500원\n(시원하고 저렴)",
            "팟타이 1접시": "약 2,500~4,500원\n(야시장 기준)",
            "타이 마사지 1시간": "약 12,000~20,000원\n(한국의 1/3 수준)"
        },
        "themes": {
            "🏛️ 랜드마크 & 역사": ["방콕 왕궁 & 에메랄드 사원", "왓 아룬 (새벽 사원)", "왓 포"],
            "🛍️ 쇼핑 & 나이트라이프": ["아이콘시암 쇼핑몰", "짜뚜짝 주말시장", "카오산 로드"],
            "🌿 힐링 & 스파": ["룸피니 공원 도심 산책", "짜오프라야강 디너 크루즈"],
            "📸 인생샷 명소": ["왓 아룬 건너편 루프탑 카페", "티추카(Tichuca) 루프탑 바"]
        },
        "restaurants": [
            {"name": "팁싸마이 (Thipsamai)", "menu": "오리지널 팟타이", "tip": "달콤한 생과육 오렌지 주스 주문 필수"},
            {"name": "쏜통 포차나", "menu": "뿌팟퐁커리, 모닝글로리", "tip": "한국인 입맛에 가장 잘 맞는 해산물 명소"},
            {"name": "폴로 프라이드 치킨", "menu": "마늘 튀김 치킨", "tip": "룸피니 공원 근처 미쉐린 빕구르망 맛집"}
        ]
    },
    "파리 (Paris, 프랑스)": {
        "city_en": "Paris",
        "currency": "EUR",
        "timezone": "Europe/Paris",
        "time_diff_desc": "한국보다 7–8시간 느림 (서머타임 적용)",
        "best_season": "5월–6월 및 9월–10월 (맑은 하늘과 온화한 날씨)",
        "visa": "무비자 (솅겐 협약 90일)",
        "voltage": "230V (한국 2핀 플러그 호환)",
        "tipping": "청구서에 서비스 요금 포함 (만족 시 1~2유로 권장)",
        "transport_tip": "나비고 이지(Navigo Easy) 카드 충전 후 이용",
        "price_compare": {
            "에스프레소 1잔": "약 3,500~4,500원\n(스탠딩 바 권장)",
            "정통 바게트 1개": "약 1,800~2,200원\n(빵류는 저렴)",
            "점심 코스 1인": "약 35,000~60,000원\n(외식 물가 높음)"
        },
        "themes": {
            "🏛️ 랜드마크 & 박물관": ["루브르 박물관", "오르세 미술관", "개선문 & 샹젤리제"],
            "🛍️ 쇼핑 & 거리": ["마레 지구 빈티지 숍", "라파예트 백화점 본점"],
            "🌿 힐링 & 정원": ["튈르리 정원", "뤽상부르 공원 피크닉"],
            "📸 인생샷 명소": ["샤요궁에서 바라보는 에펠탑", "몽마르트르 언덕 사크레쾨르"]
        },
        "restaurants": [
            {"name": "Le Bouillon Chartier", "menu": "에스카르고, 오리 콩피", "tip": "100년 전통 최고의 가성비 클래식 식당"},
            {"name": "Café de Flore", "menu": "크루아상 & 쇼콜라 쇼", "tip": "생제르맹 거리의 고풍스러운 야외 테라스석"},
            {"name": "L'As du Fallafel", "menu": "팔라펠 샌드위치", "tip": "마레 지구 필수 테이크아웃 간편 맛집"}
        ]
    },
    "런던 (London, 영국)": {
        "city_en": "London",
        "currency": "GBP",
        "timezone": "Europe/London",
        "time_diff_desc": "한국보다 8–9시간 느림",
        "best_season": "6월–8월 (비가 적고 낮이 긴 초여름)",
        "visa": "6개월 무비자 입국",
        "voltage": "230V (영국식 3핀 G타입 어댑터 필수)",
        "tipping": "식당 영수증에 12.5% 서비스 차지가 자동 부과되는 편",
        "transport_tip": "컨택리스(Contactless) 해외 카드로 교통카드 태그",
        "price_compare": {
            "플랫화이트 커피 1잔": "약 6,000~7,500원\n(물가 체감 높음)",
            "지하철(Tube) 1회": "약 4,800원\n(교통비 비쌈)",
            "식당 1인 식사": "약 30,000~55,000원\n(팁 포함 시 상당함)"
        },
        "themes": {
            "🏛️ 랜드마크 & 박물관": ["대영박물관 (무료)", "빅벤 & 웨스트민스터 사원", "타워 브리지"],
            "🛍️ 마켓 & 거리": ["버러 마켓 (식도락)", "캠든 마켓", "소호 & 코벤트 가든"],
            "🌿 힐링 & 공원": ["하이드 파크", "리젠트 파크 & 프림로즈 힐"],
            "📸 인생샷 명소": ["런던아이", "밀레니엄 브릿지에서 본 세인트폴"]
        },
        "restaurants": [
            {"name": "Flat Iron", "menu": "플랫 아이언 스테이크", "tip": "가성비 스테이크, 후식 아이스크림 제공"},
            {"name": "Poppies Fish & Chips", "menu": "피시 앤 칩스", "tip": "소호 거리의 정통 영국식 튀김 요리"},
            {"name": "Monmouth Coffee", "menu": "드립 커피 / 플랫 화이트", "tip": "버러 마켓 근처 런던 3대 스페셜티 카페"}
        ]
    },
    "바르셀로나 (Barcelona, 스페인)": {
        "city_en": "Barcelona",
        "currency": "EUR",
        "timezone": "Europe/Madrid",
        "time_diff_desc": "한국보다 7–8시간 느림",
        "best_season": "5월–6월 및 9월–10월 (온화한 지중해성 날씨)",
        "visa": "무비자 (솅겐 협약 90일)",
        "voltage": "230V (한국 플러그 호환)",
        "tipping": "원칙적으로 팁 의무 없음 (잔돈 1~2유로 남기는 편)",
        "transport_tip": "T-Usual 또는 T-Casual(10회권) 대중교통 카드 권장",
        "price_compare": {
            "카페 콘 레체(라떼)": "약 2,500~3,500원\n(한국보다 저렴)",
            "타파스 1접시": "약 6,000~12,000원\n(다양하게 맛보기 좋음)",
            "해산물 빠에야 1인": "약 25,000~35,000원\n(2인 이상 주문 多)"
        },
        "themes": {
            "🏛️ 가우디 & 건축": ["사그라다 파밀리아 대성당", "구엘 공원", "카사 바트요 & 카사 밀라"],
            "🛍️ 마켓 & 구시가지": ["보케리아 전통시장", "고딕 지구 골목 투어", "람블라스 거리"],
            "🌿 해변 & 힐링": ["바르셀로네타 해변", "몬주익 언덕"],
            "📸 인생샷 명소": ["벙커(Bunkers del Carmel) 일몰 전망", "사그라다 파밀리아 앞 호수 공원"]
        },
        "restaurants": [
            {"name": "Cervecería Catalana", "menu": "맛조개 구이, 타파스", "tip": "예약 불가, 오픈 15분 전 대기 추천"},
            {"name": "El Glop", "menu": "먹물 빠에야", "tip": "덜 짜게 먹으려면 'Sin Sal(소금 빼주세요)' 요청"},
            {"name": "Churrería San Román", "menu": "수제 츄러스 & 쇼콜라", "tip": "고딕지구의 갓 튀겨낸 바삭한 츄러스 명소"}
        ]
    },
    "뉴욕 (New York, 미국)": {
        "city_en": "New York",
        "currency": "USD",
        "timezone": "America/New_York",
        "time_diff_desc": "한국보다 13–14시간 느림",
        "best_season": "4월–5월 (봄꽃) 및 9월–11월 (선선한 가을 날씨)",
        "visa": "ESTA(전자여행허가) 사전 발급 필수",
        "voltage": "120V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 필수 (테이블 서빙 식당 18% ~ 22%)",
        "transport_tip": "OMNY 비접촉 결제 카드로 지하철 직접 태그",
        "price_compare": {
            "아메리카노 1잔": "약 7,000~9,000원\n(물가 매우 높음)",
            "지하철 1회": "약 4,000원\n(환승 1회 무료)",
            "식당 1인 (팁/세금 포함)": "약 45,000~85,000원\n(외식비 부담)"
        },
        "themes": {
            "🏛️ 랜드마크 & 전망대": ["엠파이어 스테이트 빌딩", "탑 오브 더 락", "서밋 원 밴더빌트"],
            "🛍️ 쇼핑 & 문화": ["소호(SOHO)", "브로드웨이 뮤지컬", "메트로폴리탄 미술관"],
            "🌿 힐링 & 도심 공원": ["센트럴 파크 피크닉", "하이라인 파크 & 더 베슬"],
            "📸 인생샷 명소": ["덤보(DUMBO) 맨해튼 브릿지 뷰", "브루클린 브릿지 일몰 산책"]
        },
        "restaurants": [
            {"name": "Peter Luger Steak House", "menu": "포터하우스 스테이크", "tip": "130년 전통, 현금/직불카드 권장"},
            {"name": "Joe's Pizza", "menu": "치즈 피자 슬라이스", "tip": "그리니치 빌리지의 가성비 조각 피자"},
            {"name": "Katz's Delicatessen", "menu": "파스트라미 샌드위치", "tip": "푸짐한 소고기 패티, 입장 티켓 분실 주의"}
        ]
    },
    "시드니 (Sydney, 호주)": {
        "city_en": "Sydney",
        "currency": "AUD",
        "timezone": "Australia/Sydney",
        "time_diff_desc": "한국보다 1–2시간 빠름",
        "best_season": "10월–11월 (봄 자카란다) 및 12월–2월 (따뜻한 여름)",
        "visa": "ETA(전자비자) 앱 사전 신청",
        "voltage": "240V (사선형 3핀 삼각 어댑터 필수)",
        "tipping": "원칙적으로 팁 문화 없음",
        "transport_tip": "오팔(Opal) 카드 또는 컨택리스 해외 신용카드",
        "price_compare": {
            "플랫화이트 커피 1잔": "약 4,800~5,800원\n(커피 수준 최상)",
            "피시 앤 칩스": "약 18,000~25,000원\n(비치 주변 추천)",
            "브런치 플레이트": "약 22,000~32,000원\n(한국보다 약간 높음)"
        },
        "themes": {
            "🏛️ 랜드마크 & 하버": ["시드니 오페라 하우스", "하버 브릿지", "달링 하버"],
            "🛍️ 마켓 & 로컬": ["패디스 마켓", "록스 주말 마켓", "더 그라운즈 오브 알렉산드리아"],
            "🌿 해변 & 대자연": ["본다이 비치 해안 트레킹", "맨리 비치", "블루 마운틴 투어"],
            "📸 인생샷 명소": ["미세스 맥쿼리 포인트 (오페라+하버 뷰)", "루나 파크"]
        },
        "restaurants": [
            {"name": "Pancake on the Rocks", "menu": "팬케이크 & 바베큐 립", "tip": "달링하버 인근, 늦은 밤까지 식사 가능"},
            {"name": "Hurricane's Grill", "menu": "폭립(Pork Ribs)", "tip": "달콤짭조름한 소스가 일품, 사전 예약 필수"},
            {"name": "Single O Surry Hills", "menu": "스페셜티 커피 & 브런치", "tip": "시드니 로컬 커피 애호가들의 성지"}
        ]
    }
}

# 날씨 상태별 모던 SVG 벡터 아이콘 매핑
def get_weather_svg(main_status):
    status = (main_status or "").lower()
    if "clear" in status:
        return '''<svg class="weather-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="14" fill="#E0A96D"/>
            <path d="M32 8V14M32 50V56M8 32H14M50 32H56M15 15L19.2 19.2M44.8 44.8L49 49M15 49L19.2 44.8M44.8 19.2L49 15" stroke="#E0A96D" stroke-width="4" stroke-linecap="round"/>
        </svg>'''
    elif "cloud" in status:
        return '''<svg class="weather-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M46 44H20C14.4772 44 10 39.5228 10 34C10 28.7956 13.9749 24.5194 19.0641 24.0485C20.6725 17.1592 26.8377 12 34.2 12C42.8156 12 49.845 18.7308 50.1837 27.2348C54.606 28.1887 58 32.0911 58 36.8C58 42.1019 53.7019 46.4 48.4 46.4" fill="#9BA4B5" opacity="0.85"/>
        </svg>'''
    elif "rain" in status or "drizzle" in status:
        return '''<svg class="weather-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M44 36H20C15.5817 36 12 32.4183 12 28C12 23.8365 15.1799 20.4155 19.2513 20.0388C20.538 14.5274 25.4702 10.4 31.36 10.4C38.2525 10.4 43.876 15.7846 44.147 22.5878C47.6848 23.3509 50.4 26.4729 50.4 30.24C50.4 34.4815 46.9615 37.92 42.72 37.92" fill="#7895B2"/>
            <path d="M22 44L18 52M32 44L28 52M42 44L38 52" stroke="#6096B4" stroke-width="3.5" stroke-linecap="round"/>
        </svg>'''
    elif "snow" in status:
        return '''<svg class="weather-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 12V52M12 32H52M18 18L46 46M18 46L46 18" stroke="#93BFCF" stroke-width="4" stroke-linecap="round"/>
        </svg>'''
    else:
        return '''<svg class="weather-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 24H50M10 32H54M18 40H46" stroke="#8997A5" stroke-width="4" stroke-linecap="round"/>
        </svg>'''

# ==========================================
# 7. 헤더 & 목적지 선택
# ==========================================
st.title("✈️ 떠나자 해외여행")
st.caption("실시간 날씨와 현지 시각, 환율 계산, 한국과의 물가 비교 및 테마별 여행 팁을 제공합니다.")

selected_city_name = st.selectbox(
    "여행할 도시를 선택하세요:",
    list(DESTINATIONS.keys()),
    index=0
)
city_data = DESTINATIONS[selected_city_name]
target_currency = city_data["currency"]

st.write("")

# 2열 분할: [실시간 날씨 & 시차 비교] vs [환율 & 환전 계산기]
col1, col2 = st.columns([1, 1], gap="medium")

# ==========================================
# 8. 날씨 & 시차 비교 섹션
# ==========================================
with col1:
    st.subheader(f"☀️ {city_data['city_en']} 날씨 & 시각")

    # 한국 시각 & 현지 시각 계산
    kst_now = datetime.now(ZoneInfo("Asia/Seoul"))
    local_now = datetime.now(ZoneInfo(city_data["timezone"]))

    t1, t2 = st.columns(2)
    with t1:
        st.metric(
            label="🇰🇷 대한민국 (서울)",
            value=kst_now.strftime("%H:%M"),
            delta=kst_now.strftime("%m월 %d일 (%a)")
        )
    with t2:
        st.metric(
            label=f"📍 {city_data['city_en']} 현지 시각",
            value=local_now.strftime("%H:%M"),
            delta=city_data["time_diff_desc"]
        )

    st.write("")

    if OPENWEATHER_API_KEY:
        try:
            weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city_data['city_en']}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
            )
            res = requests.get(weather_url, timeout=5).json()

            if str(res.get("cod")) == "200":
                temp = res["main"]["temp"]
                feels_like = res["main"]["feels_like"]
                humidity = res["main"]["humidity"]
                main_condition = res["weather"][0]["main"]
                desc = res["weather"][0]["description"]

                svg_icon = get_weather_svg(main_condition)

                st.markdown(f"""
                <div class="weather-box">
                    <div>{svg_icon}</div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #2F3E46;">
                            {temp:.1f} °C <span style="font-size: 0.9rem; font-weight: 500; color: #64748B;">(체감 {feels_like:.1f} °C)</span>
                        </div>
                        <div>
                            <span class="weather-desc-badge">{desc.capitalize()}</span>
                            <span style="font-size: 0.85rem; color: #52796F; margin-left: 8px; font-weight: 600;">습도 {humidity}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                err_msg = res.get("message", "도시 정보를 찾을 수 없습니다.")
                st.warning(f"날씨 데이터를 불러오지 못했습니다: {err_msg}")
        except Exception as e:
            st.error(f"날씨 API 호출 오류: {e}")
    else:
        st.info("💡 `.env` 파일에 `OPENWEATHER_API_KEY`를 설정하면 날씨가 표시됩니다.")

# ==========================================
# 9. 환율 & 계산기 섹션
# ==========================================
with col2:
    st.subheader(f"💵 실시간 환율 & 환전 ({target_currency})")
    current_rate = None

    if EXCHANGE_API_KEY:
        try:
            ex_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{target_currency}"
            ex_res = requests.get(ex_url, timeout=5).json()
            if ex_res.get("result") == "success":
                current_rate = ex_res["conversion_rates"]["KRW"]
        except Exception:
            pass

    fallback_rates = {"JPY": 9.2, "EUR": 1475.0, "USD": 1385.0, "THB": 38.5, "VND": 0.054, "TWD": 43.0, "GBP": 1780.0, "AUD": 910.0}
    if not current_rate:
        current_rate = fallback_rates.get(target_currency, 1300.0)

    rate_key = f"prev_{target_currency}"
    if rate_key in st.session_state:
        diff = current_rate - st.session_state[rate_key]
        delta_label = f"{diff:+.2f} 원" if abs(diff) > 0.001 else "변동 없음"
    else:
        delta_label = "실시간 기준"
    st.session_state[rate_key] = current_rate

    unit_mult = 100 if target_currency in ["JPY", "VND"] else 1
    unit_label = f"100 {target_currency}당" if unit_mult == 100 else f"1 {target_currency}당"

    spread = st.slider("환전 우대 수수료율 (스프레드 %)", 0.0, 3.0, 1.75, 0.25)
    cash_buy = current_rate * (1 + spread / 100)
    cash_sell = current_rate * (1 - spread / 100)

    r1, r2, r3 = st.columns(3)
    r1.metric(f"매매기준율 ({unit_label})", f"{current_rate * unit_mult:,.2f} 원", delta=delta_label)
    r2.metric("현찰 살 때 (매수)", f"{cash_buy * unit_mult:,.2f} 원")
    r3.metric("현찰 팔 때 (매도)", f"{cash_sell * unit_mult:,.2f} 원")

    c_type = st.radio("환전 방향 선택:", ["원화(KRW) ➡️ 외화 살 때", "외화 ➡️ 원화(KRW) 바꿀 때"], horizontal=True)
    if c_type.startswith("원화"):
        krw_v = st.number_input("환전할 원화 금액(KRW) 입력:", min_value=1000, value=100000, step=10000)
        st.success(f"👉 예상 수령액: **{krw_v / cash_buy:,.2f} {target_currency}**")
    else:
        for_v = st.number_input(f"남은 외화 금액({target_currency}) 입력:", min_value=1, value=100, step=10)
        st.success(f"👉 예상 환급액: **{for_v * cash_sell:,.0f} KRW**")

st.divider()

# ==========================================
# 10. 여행 전 체크리스트
# ==========================================
st.subheader(f"🇰🇷 여행 전 필수 체크리스트 ({selected_city_name})")

c1, c2, c3, c4 = st.columns(4)
c1.info(f"🗓️ **추천 여행 시기**\n\n{city_data['best_season']}")
c2.info(f"🛂 **비자 규정**\n\n{city_data['visa']}")
c3.info(f"🔌 **전압 및 콘센트**\n\n{city_data['voltage']}")
c4.info(f"🪙 **현지 팁 문화**\n\n{city_data['tipping']}")

st.write("")
st.markdown("#### 🛒 한국(서울) 기준 물가 체감 비교")

price_items = list(city_data["price_compare"].items())
price_cols = st.columns(len(price_items))
for i, (item_name, item_val) in enumerate(price_items):
    with price_cols[i]:
        st.metric(label=item_name, value=item_val)

st.caption(f"🚇 **교통패스 및 이동 꿀팁:** {city_data['transport_tip']}")

st.divider()

# ==========================================
# 11. 테마별 관광지 & 대표 맛집
# ==========================================
st.subheader(f"📍 {selected_city_name} 테마별 명소 & 대표 맛집")

col_theme, col_food = st.columns([1.2, 1], gap="large")

# 11-1. 테마별 관광지 (Tabs)
with col_theme:
    st.markdown("#### 🎯 여행 테마별 추천 코스")
    theme_tabs = st.tabs(list(city_data["themes"].keys()))
    for idx, (theme_name, spots) in enumerate(city_data["themes"].items()):
        with theme_tabs[idx]:
            for s in spots:
                st.markdown(f"- 🚩 **{s}**")

# 11-2. 현지 대표 맛집
with col_food:
    st.markdown("#### 🍽️ 현지 추천 맛집 & 팁")
    for r in city_data["restaurants"]:
        with st.expander(f"🍴 {r['name']} ({r['menu']})"):
            st.markdown(f"**대표 메뉴:** `{r['menu']}`")
            st.markdown(f"**방문 팁:** {r['tip']}")