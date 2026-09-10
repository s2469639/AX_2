import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# 2. 페이지 설정
st.set_page_config(page_title="떠나자 해외여행", page_icon="✈️", layout="wide")

# 3. 뮤트톤 컬러 팔레트 & 슬라이더 전면 개선 CSS
st.markdown("""
<style>
    /* 전체 배경: 은은하고 따뜻한 웜 그레이지 */
    .stApp {
        background: linear-gradient(180deg, #F5F6F5 0%, #EBECE9 100%) !important;
        color: #2F3E46 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Pretendard", sans-serif;
    }

    /* 제목 및 텍스트 딥차콜/세이지 */
    h1, h2, h3, h4 {
        color: #354F52 !important;
        font-weight: 700 !important;
    }

    /* 메트릭 줄바꿈 및 뮤트 폰트 */
    [data-testid="stMetricValue"] {
        white-space: normal !important;
        word-break: keep-all !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #2F3E46 !important;
    }
    [data-testid="stMetricLabel"] {
        white-space: normal !important;
        word-break: keep-all !important;
        color: #52796F !important;
        font-weight: 600 !important;
    }

    /* 입력창 및 셀렉트 박스: 은은한 베이지-화이트 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        background-color: #FAFAFA !important;
        border: 1px solid #D8DDD6 !important;
        border-radius: 8px !important;
    }

    /* ==========================================
       [핵심 수정] 슬라이더 톤온톤 뮤트 세이지 & 웜그레이
       ========================================== */
    /* 1. 슬라이더 바탕 트랙 (연한 그레이지) */
    div[data-baseweb="slider"] > div > div {
        background-color: #DDE2DA !important;
    }

    /* 2. 채워진 트랙 바 (차분한 세이지 그린) */
    div[data-baseweb="slider"] > div > div > div {
        background-color: #728B80 !important;
    }

    /* 3. 슬라이더 손잡이 동그라미(Thumb) */
    div[data-baseweb="slider"] [role="slider"] {
        background-color: #587166 !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12) !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* 4. 슬라이더 숫자 팝업 툴팁 (말풍선 배경 & 폰트) */
    div[data-baseweb="popover"] div,
    div[role="tooltip"] {
        background-color: #4A5D54 !important;
        color: #F8F9FA !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        border: none !important;
    }

    /* 5. 슬라이더 양 끝 최소/최대값 텍스트 */
    div[data-baseweb="slider"] + div {
        color: #84968E !important;
        font-size: 0.8rem !important;
    }

    /* 라디오 버튼 선택 시 뮤트톤 유지 */
    div[role="radiogroup"] [aria-checked="true"] > div {
        border-color: #587166 !important;
        background-color: #587166 !important;
    }

    /* 성공 박스 (연한 톤온톤 세이지) */
    .stAlert {
        background-color: rgba(220, 227, 218, 0.6) !important;
        color: #2F3E46 !important;
        border: 1px solid #CAD2C5 !important;
        border-radius: 8px !important;
    }

    /* 아코디언(맛집) */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.75) !important;
        border-radius: 8px !important;
        color: #354F52 !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 여행지 데이터베이스
DESTINATIONS = {
    "도쿄 (Tokyo, 일본)": {
        "city_en": "Tokyo",
        "currency": "JPY",
        "time_diff": "한국과 시차 없음 (0시간)",
        "visa": "90일 무비자 입국",
        "voltage": "100V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음 (영수증 정가 지불)",
        "transport_tip": "스이카(Suica)/파스모 교통카드 또는 도쿄 서브웨이 티켓 추천",
        "price_compare": {
            "커피 1잔 (스벅 톨)": "약 4,500원\n(한국과 유사)",
            "대중교통 기본요금": "약 1,800원\n(한국보다 약간 높음)",
            "식당 한 끼 식사": "약 9,000~15,000원\n(선택 폭 넓음)"
        },
        "spots": ["시부야 스카이 전망대", "센소지 (아사쿠사)", "메이지 신궁", "오모테산도 & 캣스트리트"],
        "restaurants": [
            {"name": "이치란 라멘 (본점/시부야)", "menu": "돈코츠 라멘", "tip": "비밀 소스 맵기 조절 가능, 1인 좌석 완비"},
            {"name": "규카츠 모토무라", "menu": "규카츠 정식", "tip": "미니 화로에 직접 구워 먹는 재미, 오픈런 추천"},
            {"name": "미도리 스시", "menu": "모둠 초밥", "tip": "가성비 뛰어난 현지 인기 스시 체인"}
        ]
    },
    "오사카 (Osaka, 일본)": {
        "city_en": "Osaka",
        "currency": "JPY",
        "time_diff": "한국과 시차 없음 (0시간)",
        "visa": "90일 무비자 입국",
        "voltage": "100V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음",
        "transport_tip": "오사카 주유패스 (관광지 무료입장) 또는 이코카(ICOCA) 카드",
        "price_compare": {
            "커피 1잔": "약 4,200원\n(한국과 유사)",
            "대중교통 기본요금": "약 2,000원\n(한국 대비 높음)",
            "타코야키/라멘 한 끼": "약 7,000~12,000원\n(길거리 음식 발달)"
        },
        "spots": ["도톤보리 글리코상", "오사카성 천수각", "유니버설 스튜디오 재팬(USJ)", "우메다 공중정원"],
        "restaurants": [
            {"name": "앗치치혼포", "menu": "타코야키", "tip": "도톤보리 강변 앞, 타코폰즈 소스 조합 추천"},
            {"name": "모토무라 규카츠 난바점", "menu": "규카츠", "tip": "점심 피크를 피해 14시 이후 방문 권장"},
            {"name": "키지 (우메다)", "menu": "오코노미야키", "tip": "우메다 스카이빌딩 지하 레트로 식당가 위치"}
        ]
    },
    "다낭 (Da Nang, 베트남)": {
        "city_en": "Da Nang",
        "currency": "VND",
        "time_diff": "한국보다 2시간 느림",
        "visa": "45일 무비자 입국",
        "voltage": "220V (한국 전자제품 그대로 호환)",
        "tipping": "의무는 아니나 마사지샵은 2~5만동 매너 팁 일반적",
        "transport_tip": "그랩(Grab) 앱 호출이 가장 저렴하고 바가지 위험 없음",
        "price_compare": {
            "코코넛 커피 1잔": "약 2,000~2,800원\n(매우 저렴)",
            "그랩 택시 기본요금": "약 1,200원\n(부담 없는 이동)",
            "로컬 쌀국수 한 그릇": "약 2,500~4,000원\n(가성비 최상)"
        },
        "spots": ["바나힐 골든브릿지", "미케 비치 해변", "호이안 올드타운 (근교 야경)", "용다리 불쇼"],
        "restaurants": [
            {"name": "포홍 (Pho Hong)", "menu": "소고기 쌀국수", "tip": "로컬 1등 쌀국수, 바삭한 꿔이를 국물에 곁들이기"},
            {"name": "마담란", "menu": "반쎄오, 분짜", "tip": "에어컨과 쾌적한 인테리어를 갖춘 대형 레스토랑"},
            {"name": "콩카페 (Cong Caphe)", "menu": "코코넛 스무디 커피", "tip": "한강변 뷰를 보며 여유롭게 힐링하기 좋음"}
        ]
    },
    "타이베이 (Taipei, 대만)": {
        "city_en": "Taipei",
        "currency": "TWD",
        "time_diff": "한국보다 1시간 느림",
        "visa": "90일 무비자 입국",
        "voltage": "110V (11자 돼지코 어댑터 필요)",
        "tipping": "팁 문화 없음 (고급 식당만 10% 봉사료 추가)",
        "transport_tip": "이지카드(EasyCard) 구매 필수 (지하철, 버스, 편의점 공용)",
        "price_compare": {
            "버블티 1잔 (라지)": "약 2,500~3,500원\n(한국의 절반 수준)",
            "MRT 지하철 기본요금": "약 900원\n(한국보다 훨씬 저렴)",
            "우육면 한 그릇": "약 7,000~9,500원\n(푸짐한 고기 양)"
        },
        "spots": ["타이베이 101 타워", "지우펀 옛거리", "스린 야시장", "국립고궁박물원"],
        "restaurants": [
            {"name": "딘타이펑 본점", "menu": "샤오롱바오", "tip": "현장 번호표 발급 후 주변 거리 산책 추천"},
            {"name": "융캉우육면", "menu": "홍샤오 우육면", "tip": "진한 소고기 육수와 쫄깃한 면발의 조화"},
            {"name": "삼형매 빙수", "menu": "망고 눈꽃빙수", "tip": "시먼딩 대표 디저트로 식후 방문 추천"}
        ]
    },
    "방콕 (Bangkok, 태국)": {
        "city_en": "Bangkok",
        "currency": "THB",
        "time_diff": "한국보다 2시간 느림",
        "visa": "90일 무비자 입국",
        "voltage": "220V (한국 플러그 대부분 호환)",
        "tipping": "마사지샵 50~100바트, 호텔 벨보이 20~40바트 권장",
        "transport_tip": "출퇴근 시간에는 지상철(BTS)/지하철(MRT) 위주 이용",
        "price_compare": {
            "땡모반 (수박주스)": "약 1,800~2,500원\n(시원하고 저렴)",
            "팟타이 1접시": "약 2,500~4,500원\n(길거리/야시장 기준)",
            "타이 마사지 1시간": "약 12,000~20,000원\n(한국의 1/3 수준)"
        },
        "spots": ["왓 아룬 (새벽 사원)", "짜뚜짝 주말시장", "카오산 로드", "아이콘시암 분수쇼"],
        "restaurants": [
            {"name": "팁싸마이 (Thipsamai)", "menu": "오리지널 팟타이", "tip": "달콤한 생과육 오렌지 주스 주문 필수"},
            {"name": "쏜통 포차나", "menu": "뿌팟퐁커리, 모닝글로리", "tip": "한국인 입맛에 가장 잘 맞는 해산물 명소"},
            {"name": "폴로 프라이드 치킨", "menu": "마늘 튀김 치킨", "tip": "룸피니 공원 근처 미쉐린 빕구르망 맛집"}
        ]
    },
    "파리 (Paris, 프랑스)": {
        "city_en": "Paris",
        "currency": "EUR",
        "time_diff": "한국보다 7~8시간 느림",
        "visa": "무비자 (솅겐 협약 90일)",
        "voltage": "230V (한국 2핀 플러그 그대로 사용)",
        "tipping": "청구서에 서비스 요금 포함되어 의무 아님 (보통 1~2유로)",
        "transport_tip": "나비고 이지(Navigo Easy) 카드 발급 후 티켓 충전 이용",
        "price_compare": {
            "에스프레소 1잔": "약 3,500~4,500원\n(스탠딩 바가 더 저렴)",
            "정통 바게트 1개": "약 1,800~2,200원\n(빵류는 한국보다 저렴)",
            "식당 점심 코스 1인": "약 35,000~60,000원\n(외식 물가 높음)"
        },
        "spots": ["에펠탑 & 샤요궁", "루브르 박물관", "몽마르트르 언덕", "개선문 & 샹젤리제 거리"],
        "restaurants": [
            {"name": "Le Bouillon Chartier", "menu": "에스카르고, 오리 콩피", "tip": "100년 전통 파리 최고의 가성비 클래식 식당"},
            {"name": "Café de Flore", "menu": "크루아상 & 쇼콜라 쇼", "tip": "생제르맹 거리의 고풍스러운 야외 테라스석"},
            {"name": "L'As du Fallafel", "menu": "팔라펠 샌드위치", "tip": "마레 지구 필수 테이크아웃 간편 맛집"}
        ]
    },
    "런던 (London, 영국)": {
        "city_en": "London",
        "currency": "GBP",
        "time_diff": "한국보다 8~9시간 느림",
        "visa": "6개월 무비자 입국",
        "voltage": "230V (영국식 3핀 G타입 어댑터 필수)",
        "tipping": "식당 영수증에 12.5% 서비스 차지가 자동 부과되는 경우 다수",
        "transport_tip": "컨택리스(Contactless) 해외 결제 카드로 교통카드 태그 탑승",
        "price_compare": {
            "플랫화이트 커피 1잔": "약 6,000~7,500원\n(물가 체감 높음)",
            "지하철(Tube) 1회": "약 4,800원\n(교통비 매우 비쌈)",
            "일반 식당 1인 식사": "약 30,000~55,000원\n(팁 포함 시 상당함)"
        },
        "spots": ["빅벤 & 웨스트민스터", "타워 브리지", "대영박물관 (무료입장)", "하이드 파크"],
        "restaurants": [
            {"name": "Flat Iron", "menu": "플랫 아이언 스테이크", "tip": "런던 중심가 가성비 스테이크, 후식 아이스크림 제공"},
            {"name": "Poppies Fish & Chips", "menu": "피시 앤 칩스", "tip": "소호 거리의 정통 영국식 튀김 요리 전문점"},
            {"name": "Monmouth Coffee", "menu": "드립 커피 / 플랫 화이트", "tip": "버러 마켓 근처 런던 3대 스페셜티 카페"}
        ]
    },
    "바르셀로나 (Barcelona, 스페인)": {
        "city_en": "Barcelona",
        "currency": "EUR",
        "time_diff": "한국보다 7~8시간 느림",
        "visa": "무비자 (솅겐 협약 90일)",
        "voltage": "230V (한국 플러그 그대로 호환)",
        "tipping": "원칙적으로 팁 의무 없음 (잔돈 1~2유로 남기는 편)",
        "transport_tip": "T-Usual 또는 T-Casual(10회권) 대중교통 카드 권장",
        "price_compare": {
            "카페 콘 레체(라떼)": "약 2,500~3,500원\n(한국보다 저렴)",
            "타파스 1접시": "약 6,000~12,000원\n(다양하게 맛보기 좋음)",
            "해산물 빠에야 1인": "약 25,000~35,000원\n(2인 이상 주문 필수 多)"
        },
        "spots": ["사그라다 파밀리아 성당", "구엘 공원", "카사 바트요", "보케리아 전통시장"],
        "restaurants": [
            {"name": "Cervecería Catalana", "menu": "맛조개 구이, 타파스", "tip": "예약 불가, 오픈 15분 전 미리 대기 추천"},
            {"name": "El Glop", "menu": "먹물 빠에야", "tip": "덜 짜게 먹으려면 'Sin Sal(소금 빼주세요)' 메모 제시"},
            {"name": "Churrería San Román", "menu": "수제 츄러스 & 쇼콜라", "tip": "고딕지구의 갓 튀겨낸 바삭한 츄러스 명소"}
        ]
    },
    "뉴욕 (New York, 미국)": {
        "city_en": "New York",
        "currency": "USD",
        "time_diff": "한국보다 13~14시간 느림",
        "visa": "ESTA(전자여행허가) 사전 발급 필수",
        "voltage": "120V (11자 돼지코 어댑터 필수)",
        "tipping": "팁 필수 (테이블 서빙 식당 기준 18% ~ 22%)",
        "transport_tip": "OMNY 비접촉 결제 카드로 지하철 개찰구 직접 태그",
        "price_compare": {
            "아메리카노 1잔": "약 7,000~9,000원\n(물가 매우 높음)",
            "지하철 1회 요금": "약 4,000원\n(환승 1회 무료)",
            "식당 식사 (팁/세금 포함)": "약 45,000~85,000원\n(외식비 부담 큰 편)"
        },
        "spots": ["센트럴 파크", "엠파이어 스테이트 & 탑오브더락", "타임스스퀘어", "브루클린 브릿지"],
        "restaurants": [
            {"name": "Peter Luger Steak House", "menu": "포터하우스 스테이크", "tip": "브루클린 130년 전통, 현금/직불카드 권장"},
            {"name": "Joe's Pizza", "menu": "치즈 피자 슬라이스", "tip": "그리니치 빌리지의 가성비 정통 뉴욕 조각 피자"},
            {"name": "Katz's Delicatessen", "menu": "파스트라미 샌드위치", "tip": "엄청난 두께의 훈제 소고기 패티, 입장 티켓 분실 주의"}
        ]
    },
    "시드니 (Sydney, 호주)": {
        "city_en": "Sydney",
        "currency": "AUD",
        "time_diff": "한국보다 1~2시간 빠름",
        "visa": "ETA(전자여행비자) 전용 앱 사전 신청",
        "voltage": "240V (사선형 3핀 삼각 플러그 어댑터 필수)",
        "tipping": "원칙적으로 팁 문화 없음",
        "transport_tip": "오팔(Opal) 카드 또는 일반 해외 결제 컨택리스 신용카드",
        "price_compare": {
            "플랫화이트 커피 1잔": "약 4,800~5,800원\n(커피 퀄리티 최상)",
            "피시 앤 칩스": "약 18,000~25,000원\n(비치 주변 추천)",
            "브런치 1개 플레이트": "약 22,000~32,000원\n(한국보다 조금 높음)"
        },
        "spots": ["오페라 하우스 & 하버 브릿지", "본다이 비치 해안 트레킹", "블루 마운틴", "달링 하버"],
        "restaurants": [
            {"name": "Pancake on the Rocks", "menu": "팬케이크 & 바베큐 립", "tip": "달링하버 인근, 늦은 밤까지 식사 가능"},
            {"name": "Hurricane's Grill", "menu": "폭립(Pork Ribs)", "tip": "달콤짭조름한 소스가 일품, 사전 예약 필수"},
            {"name": "Single O Surry Hills", "menu": "스페셜티 커피 & 브런치", "tip": "시드니 로컬 커피 애호가들의 성지"}
        ]
    }
}

# ==========================================
# 헤더 & 도시 선택
# ==========================================
st.title("✈️ 떠나자 해외여행")
st.caption("실시간 현지 날씨, 환율 계산, 한국과의 물가 비교 및 실속 팁을 제공합니다.")

selected_city_name = st.selectbox(
    "여행할 도시를 선택하세요:",
    list(DESTINATIONS.keys()),
    index=0
)
city_data = DESTINATIONS[selected_city_name]
target_currency = city_data["currency"]

st.write("")

# 2열 분할: [실시간 날씨] vs [환율 & 환전 계산기]
col1, col2 = st.columns([1, 1], gap="medium")

# 1. 날씨
with col1:
    st.subheader(f"☀️ {city_data['city_en']} 실시간 날씨")
    if OPENWEATHER_API_KEY:
        try:
            weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city_data['city_en']}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
            )
            res = requests.get(weather_url, timeout=5).json()

            if res.get("cod") == 200:
                temp = res["main"]["temp"]
                feels_like = res["main"]["feels_like"]
                humidity = res["main"]["humidity"]
                desc = res["weather"][0]["description"]
                icon = res["weather"][0]["icon"]

                w1, w2 = st.columns([1, 2])
                with w1:
                    st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=90)
                with w2:
                    st.metric(label="현재 기온", value=f"{temp:.1f} °C", delta=f"체감 {feels_like:.1f} °C")
                    st.caption(f"날씨: **{desc.capitalize()}** | 습도: **{humidity}%**")
            else:
                st.warning("날씨 정보를 불러오지 못했습니다.")
        except Exception as e:
            st.error(f"날씨 오류: {e}")
    else:
        st.info("`.env` 파일에 `OPENWEATHER_API_KEY`를 설정하면 날씨가 표시됩니다.")

# 2. 환율
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

    # 등락폭 계산
    rate_key = f"prev_{target_currency}"
    if rate_key in st.session_state:
        diff = current_rate - st.session_state[rate_key]
        delta_label = f"{diff:+.2f} 원" if abs(diff) > 0.001 else "변동 없음"
    else:
        delta_label = "실시간 기준"
    st.session_state[rate_key] = current_rate

    unit_mult = 100 if target_currency in ["JPY", "VND"] else 1
    unit_label = f"100 {target_currency}당" if unit_mult == 100 else f"1 {target_currency}당"

    # [수정] 슬라이더 바
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
# 3. 한국 비교 & 실속 체크리스트
# ==========================================
st.subheader(f"🇰🇷 한국과 비교해보는 {selected_city_name} 체크리스트")

c1, c2, c3, c4 = st.columns(4)
c1.info(f"⏰ **시차**\n\n{city_data['time_diff']}")
c2.info(f"🛂 **비자**\n\n{city_data['visa']}")
c3.info(f"🔌 **전압/콘센트**\n\n{city_data['voltage']}")
c4.info(f"🪙 **팁 문화**\n\n{city_data['tipping']}")

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
# 4. 관광 명소 & 추천 맛집
# ==========================================
st.subheader(f"📍 {selected_city_name} 필수 랜드마크 & 대표 맛집")
col_spots, col_food = st.columns(2, gap="large")

with col_spots:
    st.markdown("#### 🏛️ 추천 명소 & 랜드마크")
    for s in city_data["spots"]:
        st.markdown(f"- 🚩 **{s}**")

with col_food:
    st.markdown("#### 🍽️ 현지 추천 맛집 & 팁")
    for r in city_data["restaurants"]:
        with st.expander(f"🍴 {r['name']} ({r['menu']})"):
            st.markdown(f"**대표 메뉴:** `{r['menu']}`")
            st.markdown(f"**방문 팁:** {r['tip']}")