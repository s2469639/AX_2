// 서비스 목록 데이터 — 서비스를 추가하려면 배열에 한 덩어리만 더하세요.
// 요금은 2026년 10월 기준이며 서비스 사정에 따라 바뀔 수 있습니다.
const CATEGORIES = ["글쓰기·대화", "리서치·검색", "바이브 코딩", "웹·UI/UX 디자인", "이미지 생성·편집", "동영상 생성", "동영상 편집", "음성·번역", "음악", "문서·업무", "시각화·PPT", "회의록·기록", "자동화", "범용 AI 에이전트"];

const services = [
  {
    "name": "ChatGPT",
    "categories": [
      "글쓰기·대화"
    ],
    "desc": "글쓰기·요약·분석·이미지까지 두루 쓰는 OpenAI의 대표 AI 챗봇",
    "url": "https://chatgpt.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 기본 모델, 사용량 제한",
      "Go: 월 $8",
      "Plus: 월 $20 (Deep Research, Codex 포함)",
      "Pro: 월 $100부터 (상위 $200)"
    ],
    "pros": [
      "대화·글쓰기·분석·이미지 생성을 한 곳에서",
      "음성 대화와 파일 분석 지원",
      "GPTs와 연동 앱이 풍부함"
    ],
    "useCase": "보고서 초안, 아이디어 정리, 엑셀·코드 질문",
    "id": 1
  },
  {
    "name": "Claude",
    "categories": [
      "글쓰기·대화"
    ],
    "desc": "긴 글을 자연스럽게 읽고 쓰는 Anthropic의 AI 어시스턴트",
    "url": "https://claude.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 웹 검색·파일 생성 포함, 사용량 제한",
      "Pro: 월 $20 (연 $200)",
      "Max: 월 $100 / $200"
    ],
    "pros": [
      "긴 문서를 이해하고 사람처럼 매끄럽게 글을 씀",
      "파일·PDF 분석과 코드 작성에 강함",
      "차분하고 일관된 말투"
    ],
    "useCase": "긴 문서 요약, 글 다듬기, 코드 리뷰",
    "id": 2
  },
  {
    "name": "Gemini",
    "categories": [
      "글쓰기·대화"
    ],
    "desc": "Gmail·Docs 등 Google 서비스와 이어 쓰는 Google의 AI 어시스턴트",
    "url": "https://gemini.google.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 기본 모델, Deep Research 월 5회",
      "AI Plus: 월 $4.99",
      "AI Pro: 월 $19.99 (Veo 영상, 크레딧 포함)",
      "AI Ultra: 월 $99.99 / $199.99"
    ],
    "pros": [
      "Gmail·Drive·Docs 등 Google 앱과 바로 연동",
      "이미지(Nano Banana)·영상(Veo)까지 한 곳에서 생성",
      "많은 자료를 한 번에 읽는 데 유리"
    ],
    "useCase": "메일·문서 정리, 자료 조사, Google 업무 도구 활용",
    "id": 3
  },
  {
    "name": "Consensus",
    "categories": [
      "리서치·검색"
    ],
    "desc": "연구 논문들이 어떤 주장에 얼마나 동의하는지 한눈에 보여 주는 AI",
    "url": "https://consensus.app/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 논문 검색 무제한, Pro 답변 월 15회, Deep 리뷰 월 3회",
      "Pro: 월 $20 (연간 결제 시 월 $12)",
      "Deep: 월 $65 (연간 결제 시 월 $45)",
      "학생 인증 시 할인"
    ],
    "pros": [
      "연구로 검증된 근거만 사용",
      "예/아니오로 답할 수 있는 질문에 대해 \"연구 몇 %가 그렇다고 한다\"처럼 연구들의 합의 정도를 보여 줌"
    ],
    "useCase": "어떤 주장이 과학적으로 맞는지 빠르게 확인",
    "id": 4
  },
  {
    "name": "Elicit",
    "categories": [
      "리서치·검색"
    ],
    "desc": "여러 논문의 연구 방법과 결과를 표로 뽑아 비교해 주는 AI",
    "url": "https://elicit.com/",
    "priceType": "freemium",
    "priceDetail": [
      "Basic(무료): 논문 검색·요약·채팅 무제한, 리서치 에이전트·리포트는 횟수 제한",
      "Pro: 연간 결제 시 월 $49 (연 $588), 표 열 20개·논문 5,000편 선별",
      "Scale: 연간 결제 시 월 $169 (연 $2,028), 팀 협업"
    ],
    "pros": [
      "여러 논문에서 연구 방법, 대상 수, 결과 같은 항목을 뽑아 표로 정리"
    ],
    "useCase": "레포트나 논문 쓸 때 선행연구 비교·정리",
    "id": 5
  },
  {
    "name": "Gemini Deep Research",
    "categories": [
      "리서치·검색"
    ],
    "desc": "주제 하나로 웹을 조사해 보고서 작성",
    "url": "https://gemini.google.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: Gemini 무료 계정으로 사용 가능, 사용량 많은 시간대에는 제한될 수 있음",
      "Google AI Plus: 무료의 약 2배 사용량",
      "Google AI Pro: 월 약 29,000원 ($19.99), 무료의 약 4배 사용량",
      "Google AI Ultra: 월 $99.99부터"
    ],
    "pros": [
      "조사 계획을 확인·수정한 뒤 수많은 웹페이지를 읽고 보고서로 정리하며, Google Docs로 바로 내보낼 수 있음"
    ],
    "useCase": "과제 초반 자료 조사",
    "id": 6
  },
  {
    "name": "Liner",
    "categories": [
      "리서치·검색"
    ],
    "desc": "웹과 논문을 함께 찾고, 논문의 어느 문단이 근거인지까지 보여 주는 학술 검색",
    "url": "https://app.liner.com/ko",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 광고 포함, 리서치 어시스턴트 하루 10회, 파일 업로드 하루 1개(25MB)",
      "Pro: 월 $17.99 (연간 결제 시 월 $14.99), 에이전트 크레딧 1,000, 광고 없음",
      "Max: 월 $35.99 (연간 결제 시 월 $29.99), 에이전트 크레딧 2,500, 파일 업로드 무제한"
    ],
    "pros": [
      "한국어 화면, 학술 자료 중심"
    ],
    "useCase": "레포트 참고문헌 찾기",
    "id": 7
  },
  {
    "name": "NotebookLM",
    "categories": [
      "리서치·검색",
      "문서·업무"
    ],
    "desc": "내가 모은 자료 안에서만 답해 주는 나만의 자료 비서",
    "url": "https://notebooklm.google.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 노트북 100개, 노트북당 자료 50개",
      "2026.9.2부터 채팅·스튜디오는 사용량 기준 제한 (5시간마다 회복, 주간 한도)",
      "Google AI Plus: 무료의 약 2배 사용량, 노트북당 자료 100개",
      "Google AI Pro: 월 약 29,000원 ($19.99), 무료의 약 4배, 노트북당 자료 300개"
    ],
    "pros": [
      "올린 자료 안에서만 답해서 엉뚱한 답이 적음, 음성 요약 기능"
    ],
    "useCase": "강의자료·논문 요약, 시험 공부",
    "id": 8
  },
  {
    "name": "Perplexity",
    "categories": [
      "리서치·검색"
    ],
    "desc": "궁금한 것을 바로 묻고, 출처 링크와 함께 빠르게 답을 얻는 AI 검색",
    "url": "https://www.perplexity.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 기본 검색 무제한, Pro 검색 하루 약 3회, 리서치 월 1회",
      "Pro: 월 $20",
      "Education Pro: 월 $10 (학생·교육자 인증 시)",
      "Max: 월 $200"
    ],
    "pros": [
      "답마다 출처 링크가 붙어 바로 검증할 수 있음"
    ],
    "useCase": "뉴스 조사, 팩트 체크",
    "id": 9
  },
  {
    "name": "Bolt",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "브라우저 안에서 앱을 만들고 실행·미리보기까지 되는 AI 개발 도구",
    "url": "https://bolt.new/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 100만 토큰 (하루 30만 한도)",
      "Pro: 월 $25 (1,000만 토큰)",
      "Teams: 인당 월 $30"
    ],
    "pros": [
      "설치 없이 브라우저에서 바로 개발·미리보기",
      "프롬프트 하나로 프로젝트 틀을 빠르게 생성",
      "코드를 직접 보고 고칠 수 있음"
    ],
    "useCase": "빠른 프로토타입, 웹 화면 시안 구현",
    "id": 10
  },
  {
    "name": "Claude Code",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "터미널과 IDE에서 코드베이스 전체를 읽고 직접 수정하는 코딩 에이전트",
    "url": "https://claude.com/product/claude-code",
    "priceType": "paid",
    "priceDetail": [
      "무료 플랜 미포함",
      "Pro: 월 $20 (연 $200)",
      "Max: 월 $100 / $200 (사용량 5배·20배)"
    ],
    "pros": [
      "프로젝트 전체 파일을 읽고 여러 파일을 함께 수정",
      "테스트 실행·git 작업까지 스스로 진행",
      "대화로 요구사항을 바꿔 가며 개발 가능"
    ],
    "useCase": "기능 추가, 버그 수정, 코드 리팩터링, 프로젝트 전체 개발",
    "id": 11
  },
  {
    "name": "Cursor",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "클로드보다는 구현이 잘 안되는 거 같아서 간단한 코딩을 빠르게 보고 싶을 때 추천",
    "url": "https://cursor.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료 (Hobby): 에이전트 요청·탭 완성 제한적 제공, 신규 가입 시 Pro 1주 체험",
      "Pro: 월 $20",
      "Pro+: 월 $60",
      "Ultra: 월 $200"
    ],
    "pros": [
      "사용자 작업에 맞는 프롬프트/수정 방향 제안",
      "웹 기반 AI 툴 대비 빠른 코드 반영 및 실행 속도"
    ],
    "useCase": "바이브 코딩",
    "id": 12
  },
  {
    "name": "Lovable",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "말로 설명하면 웹앱을 만들고 바로 배포까지 해주는 서비스",
    "url": "https://lovable.dev/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 하루 5 크레딧 (월 약 30)",
      "Pro: 월 $25 (월 100 크레딧)",
      "Business: 월 $50"
    ],
    "pros": [
      "코딩 지식 없이 대화만으로 웹앱 완성",
      "만든 결과를 바로 배포하고 도메인 연결",
      "디자인이 깔끔하게 나옴"
    ],
    "useCase": "아이디어 시제품(MVP), 랜딩페이지, 간단한 웹서비스",
    "id": 13
  },
  {
    "name": "OpenAI Codex",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "ChatGPT 요금제에 포함된 OpenAI의 코딩 에이전트",
    "url": "https://openai.com/codex/",
    "priceType": "freemium",
    "priceDetail": [
      "Free·Go: 체험 수준의 제한된 사용",
      "Plus: 월 $20 (정기적으로 초기화되는 사용량)",
      "Pro: 월 $100부터, 더 큰 사용량",
      "별도 구독 없이 ChatGPT 요금제에 포함"
    ],
    "pros": [
      "ChatGPT 계정 하나로 바로 사용",
      "클라우드·CLI·IDE 등 여러 방식으로 작업 요청",
      "여러 작업을 병렬로 맡길 수 있음"
    ],
    "useCase": "버그 수정, 코드 작성 위임, PR 단위 작업",
    "id": 14
  },
  {
    "name": "Windsurf",
    "categories": [
      "바이브 코딩"
    ],
    "desc": "AI가 알아서 파일과 터미널을 오가며 코딩해줘서 손을 최소한으로 쓰며 바이브 코딩하고 싶을 때 추천",
    "url": "https://windsurf.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 소량 쿼터(일부 모델 제한), 탭 자동완성·인라인 편집 무제한",
      "Pro: 월 $20",
      "Teams: 인당 월 $40",
      "Max: $200"
    ],
    "pros": [
      "여러 파일을 스스로 탐색하고 터미널 명령어까지 알아서 실행해 줌",
      "Cursor 대비 전체 코드 맥락 파악 및 연계 수정 능력이 뛰어남"
    ],
    "useCase": "바이브 코딩, 다중 파일(풀스택) 웹/앱 개발, 터미널 작업 자동화",
    "id": 15
  },
  {
    "name": "Canva",
    "categories": [
      "웹·UI/UX 디자인",
      "이미지 생성·편집",
      "시각화·PPT"
    ],
    "desc": "템플릿과 AI 기능으로 홍보물·카드뉴스·발표 자료까지 만드는 올인원 디자인 도구",
    "url": "https://www.canva.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 템플릿 100만 개 이상, AI 기능 소량",
      "Pro: 월 ₩9,900 (연 ₩99,000)",
      "Business: 1인당 연 ₩139,000, 팀 협업",
      "교육기관·비영리: 무료 또는 할인"
    ],
    "pros": [
      "템플릿이 많아 디자인 경험이 없어도 쉬움",
      "배경 제거(누끼)와 이미지 편집이 강력함",
      "협업과 세부 조정이 쉬움"
    ],
    "useCase": "홍보물, 썸네일, 카드뉴스, SNS 배너, 간단한 발표 자료",
    "id": 16
  },
  {
    "name": "Claude Design",
    "categories": [
      "웹·UI/UX 디자인"
    ],
    "desc": "대화하면서 프로토타입과 발표 슬라이드를 만드는 AI",
    "url": "https://claude.ai/design",
    "priceType": "paid",
    "priceDetail": [
      "무료 플랜 미포함",
      "Claude Max: 월 $100부터",
      "별도 결제 없이 구독에 포함, 사용 한도는 Claude 사용량과 함께 계산"
    ],
    "pros": [
      "대화로 수정하며 프로토타입과 슬라이드를 함께 만들 수 있음"
    ],
    "useCase": "아이디어를 클릭되는 시제품으로 보여 줄 때",
    "id": 17
  },
  {
    "name": "Figma",
    "categories": [
      "웹·UI/UX 디자인"
    ],
    "desc": "AI로 만든 화면을 세밀하게 직접 다듬는 업계 표준 디자인 툴",
    "url": "https://www.figma.com/",
    "priceType": "freemium",
    "priceDetail": [
      "Starter(무료): 파일 3개, 에디터 2명, AI 크레딧 월 500",
      "Professional: 연간 결제 시 1인당 월 $16, AI 크레딧 월 3,000",
      "Organization 월 $55 / Enterprise 월 $90 (1인당)",
      "학생·교육자: Figma Education 인증 시 무료"
    ],
    "pros": [
      "원하는 대로 세밀하게 수정 가능, 팀원과 동시 작업"
    ],
    "useCase": "시안을 완성도 있게 다듬을 때",
    "id": 18
  },
  {
    "name": "Framer",
    "categories": [
      "웹·UI/UX 디자인"
    ],
    "desc": "프롬프트로 웹사이트를 만들고 바로 인터넷에 배포하는 툴",
    "url": "https://www.framer.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: Framer 기본 도메인, 월 대역폭 1GB, AI 크레딧 500",
      "Basic: 월 $10 (연 $120), 개인 도메인 연결, AI 크레딧 월 1,000",
      "Pro: 월 $30 (연 $360), AI 크레딧 월 3,000"
    ],
    "pros": [
      "코딩 없이 사이트를 만들고 바로 공개"
    ],
    "useCase": "포트폴리오·소개 사이트를 빨리 공개할 때",
    "id": 19
  },
  {
    "name": "Google Stitch",
    "categories": [
      "웹·UI/UX 디자인"
    ],
    "desc": "말로 설명하면 화면 시안을 여러 개 뽑아 비교하게 해 주는 무료 AI",
    "url": "https://stitch.withgoogle.com/",
    "priceType": "freemium",
    "priceDetail": [
      "Google Labs 베타로 유료 플랜 없음 (2026년 4월 기준)",
      "하루 디자인 크레딧 400 + 리디자인 15",
      "매일 한국 시간 오전 9시(UTC 자정)에 초기화"
    ],
    "pros": [
      "무료이고, 시안을 여러 개 받아 비교할 수 있음",
      "Figma로 내보내기 가능"
    ],
    "useCase": "디자인 방향을 정하기 전 아이디어 얻기",
    "id": 20
  },
  {
    "name": "v0",
    "categories": [
      "웹·UI/UX 디자인"
    ],
    "desc": "말로 설명한 화면을 실제로 작동하는 코드로 만들어 주는 AI",
    "url": "https://v0.dev/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 $5 상당 크레딧, 하루 메시지 7개",
      "개인 유료: 월 $20 (월 $20 크레딧)",
      "Team: 1인당 월 $30 (월 $30 크레딧)",
      "Business: 1인당 월 $100",
      "크레딧 초과 시 사용한 만큼 추가 결제"
    ],
    "pros": [
      "미리보기 화면과 코드가 함께 나와 바로 개발에 쓸 수 있음"
    ],
    "useCase": "디자인을 실제 웹페이지로 옮길 때",
    "id": 21
  },
  {
    "name": "Ideogram",
    "categories": [
      "이미지 생성·편집"
    ],
    "desc": "글자 타이포그래피 구현에 특화된 AI",
    "url": "https://ideogram.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 매일 10회 느린 생성 크레딧 리셋",
      "유료: Basic 월 $8 / Plus 월 $20부터"
    ],
    "pros": [
      "기본 생성 시 4가지 시안을 한 번에 제공하여 의도에 가장 가까운 결과를 선택하기 수월함",
      "커뮤니티 피드를 통해 고품질 결과물의 프롬프트를 확인하고 벤치마킹(학습)할 수 있음"
    ],
    "useCase": "영문 타이포그래피 로고 시안, 영문 포스터 및 굿즈 그래픽 생성",
    "id": 22
  },
  {
    "name": "Leonardo",
    "categories": [
      "이미지 생성·편집"
    ],
    "desc": "스타일과 모델을 골라 만드는 이미지·영상 생성 플랫폼",
    "url": "https://leonardo.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 하루 150 토큰 (결과물 공개, 상업 이용 제한)",
      "Apprentice: 월 $12",
      "Artisan: 월 $30",
      "Maestro: 월 $60"
    ],
    "pros": [
      "모델·스타일 선택이 다양함",
      "나만의 커스텀 모델 학습 가능",
      "이미지를 영상으로 확장할 수 있음"
    ],
    "useCase": "게임·컨셉 아트, 캐릭터 일러스트, 이미지 에셋 제작",
    "id": 23
  },
  {
    "name": "Midjourney",
    "categories": [
      "이미지 생성·편집"
    ],
    "desc": "극사실주의 묘사와 예술적 질감 표현에 특화된 대표 이미지 생성 AI",
    "url": "https://www.midjourney.com/",
    "priceType": "paid",
    "priceDetail": [
      "무료 체험 불가",
      "Basic 플랜: 월 $10부터"
    ],
    "pros": [
      "압도적인 사실적 그래픽 디테일, 조명·질감 묘사 최상급, 예술적 연출력 탁월"
    ],
    "useCase": "포토리얼리즘 인물/배경 그래픽, 판타지·SF 컨셉 아트, 고화질 상업용 일러스트 시안",
    "id": 24
  },
  {
    "name": "Nano Banana",
    "categories": [
      "이미지 생성·편집"
    ],
    "desc": "Google Gemini의 이미지 생성·편집 모델로, 문장으로 사진을 수정할 수 있음",
    "url": "https://gemini.google.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: Gemini 앱에서 하루 약 20장 (고급 모델은 하루 2장, 워터마크)",
      "Google AI Pro: 하루 약 100장",
      "한도는 수시로 바뀔 수 있음"
    ],
    "pros": [
      "말로 지시해 배경 교체·부분 수정이 자연스러움",
      "인물과 캐릭터의 일관성을 잘 유지",
      "이미지 속 글자 표현이 좋은 편"
    ],
    "useCase": "사진 보정, 썸네일·캐릭터 시안, 제품 이미지 편집",
    "id": 25
  },
  {
    "name": "Google Flow (Veo)",
    "categories": [
      "동영상 생성"
    ],
    "desc": "Google의 Veo 3.1 모델로 영상을 만드는 제작 도구",
    "url": "https://flow.google.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 하루 50 크레딧 (이월 안 됨)",
      "Google AI Pro: $19.99/월",
      "Google AI Ultra: 상위 요금제"
    ],
    "pros": [
      "Google AI Pro 구독 시 크레딧이 넉넉함",
      "채팅하듯 수정 사항을 바로 반영 가능",
      "영상과 소리를 함께 생성"
    ],
    "useCase": "이미 Google AI Pro를 구독 중인 경우, 여러 번 고쳐가며 완성도를 높이는 작업",
    "id": 26
  },
  {
    "name": "HeyGen",
    "categories": [
      "동영상 생성"
    ],
    "desc": "대본만 넣으면 AI 아바타가 말하는 영상을 만들어주는 서비스",
    "url": "https://www.heygen.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 3개 영상 (3분, 720p)",
      "Creator: 월 $29 (연간 결제 시 $24)",
      "Team: 인당 월 $39"
    ],
    "pros": [
      "촬영 없이 아바타 영상 제작",
      "30개 이상 언어로 번역·립싱크",
      "내 모습으로 아바타를 만들 수 있음"
    ],
    "useCase": "교육·소개 영상, 다국어 안내 영상",
    "id": 27
  },
  {
    "name": "Kling",
    "categories": [
      "동영상 생성"
    ],
    "desc": "사람의 움직임 표현과 가성비가 강점인 영상 생성 서비스",
    "url": "https://kling.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 로그인 크레딧 (확인 시점 66)",
      "Standard: $6.99/월부터 (월 660 크레딧)",
      "상위: Pro, Premier, Ultra"
    ],
    "pros": [
      "생성 전에 필요한 크레딧을 바로 확인 가능",
      "해상도, 길이, 오디오 설정이 한눈에 보임"
    ],
    "useCase": "비용을 미리 계산하며 짧은 클립을 만드는 작업",
    "id": 28
  },
  {
    "name": "Runway",
    "categories": [
      "동영상 생성"
    ],
    "desc": "영상 생성과 편집 도구를 함께 갖춘 크리에이터용 영상 AI",
    "url": "https://runwayml.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 125 크레딧 1회 (워터마크)",
      "Standard: 월 $15 (625 크레딧)",
      "Pro: 월 $35 (2,250 크레딧)"
    ],
    "pros": [
      "생성뿐 아니라 배경 제거·확장 등 편집 도구가 풍부",
      "카메라 움직임 등 연출 제어가 가능",
      "영화·광고 현장에서도 쓰이는 완성도"
    ],
    "useCase": "광고·뮤직비디오 클립, 영상 효과·합성",
    "id": 29
  },
  {
    "name": "CapCut",
    "categories": [
      "동영상 편집"
    ],
    "desc": "컷 편집, 자막, 효과, 템플릿을 갖춘 범용 편집기",
    "url": "https://www.capcut.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 기본 편집 기능, 자동 캡션 등은 월 횟수 제한",
      "스탠다드: 월 약 ₩9,900 (모바일 중심 프리미엄 기능)",
      "프로: 월 약 ₩19,800 (PC·모바일 전체 기능, 4K 내보내기, 클라우드 100GB)"
    ],
    "pros": [
      "영상 템플릿이 풍부해 구성과 디자인을 빠르게 잡을 수 있음",
      "자막을 짧게 나눠줘서 화면에 한 번에 뜨는 글자가 적음",
      "AI 이미지·영상 생성도 지원"
    ],
    "useCase": "템플릿과 효과로 꾸미는 숏폼, SNS 홍보 영상",
    "id": 30
  },
  {
    "name": "Vrew",
    "categories": [
      "동영상 편집"
    ],
    "desc": "음성 인식 자막과 텍스트 기반 컷 편집이 되는 국산 편집기",
    "url": "https://vrew.ai/ko/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 200 크레딧",
      "유료: 라이트, 스탠다드, 비즈니스"
    ],
    "pros": [
      "한 문장을 자막 하나로 묶어줘서 내용 파악이 쉬움",
      "단어 단위로 표시되어 잘못 말한 단어만 골라 지울 수 있음",
      "무음 구간이 표시되어 찾기 쉬움",
      "AI 이미지·영상 생성까지 한 곳에서 가능 (영상 모델 11개 지원)"
    ],
    "useCase": "말소리 중심의 설명, 소개, 인터뷰 영상의 자막 작업과 컷 편집",
    "id": 31
  },
  {
    "name": "DeepL",
    "categories": [
      "음성·번역"
    ],
    "desc": "자연스러운 문장의 AI 번역기",
    "url": "https://www.deepl.com/ko/translator",
    "priceType": "freemium",
    "priceDetail": [
      "Individual 월 $10.49"
    ],
    "pros": [
      "문맥을 살린 번역, 문서 파일 번역 특화, 다수 파일 일괄 번역 가능"
    ],
    "useCase": "업무 메일, 보고서, 논문",
    "id": 32
  },
  {
    "name": "ElevenLabs",
    "categories": [
      "음성·번역"
    ],
    "desc": "사람 같은 목소리를 만드는 AI 음성 툴",
    "url": "https://elevenlabs.io/",
    "priceType": "freemium",
    "priceDetail": [
      "Creator $11"
    ],
    "pros": [
      "자연스러운 감정 표현, 음성 세부 조정 용이, 목소리 복제 가능"
    ],
    "useCase": "영상 내레이션, 더빙",
    "id": 33
  },
  {
    "name": "Papago",
    "categories": [
      "음성·번역"
    ],
    "desc": "한국어에 특화된 네이버 번역기",
    "url": "https://papago.naver.com/",
    "priceType": "freemium",
    "priceDetail": [
      "Plus Basic 월 ₩13,000"
    ],
    "pros": [
      "자연스러운 구어체, 접근성 편리, 요금 제약이 낮음"
    ],
    "useCase": "단어 검색, 일상 대화, 여행",
    "id": 34
  },
  {
    "name": "Suno",
    "categories": [
      "음악"
    ],
    "desc": "가사와 분위기만 쓰면 보컬이 포함된 곡을 만들어주는 AI 음악 서비스",
    "url": "https://suno.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 하루 50 크레딧 (약 10곡, 다운로드·상업 이용 불가)",
      "Pro: 월 $10",
      "Premier: 월 $30"
    ],
    "pros": [
      "가사·장르만 입력하면 보컬까지 곡 완성",
      "장르와 스타일이 다양함",
      "4분 정도의 긴 곡도 생성"
    ],
    "useCase": "배경음악, 영상 BGM, 노래 아이디어 스케치",
    "id": 35
  },
  {
    "name": "Udio",
    "categories": [
      "음악"
    ],
    "desc": "자연스러운 음질과 곡 이어 만들기가 강점인 AI 음악 서비스",
    "url": "https://www.udio.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 하루 10 크레딧 (월 100 한도)",
      "Standard: 월 $10",
      "Pro: 월 $30",
      "음원사 계약으로 다운로드 기능이 제한되어 있음"
    ],
    "pros": [
      "생성된 음악의 음질이 자연스러움",
      "곡의 일부를 고치고 이어 붙이기 가능",
      "다양한 장르 표현"
    ],
    "useCase": "감상용 곡 제작, 음악 아이디어 탐색",
    "id": 36
  },
  {
    "name": "Microsoft Copilot",
    "categories": [
      "문서·업무"
    ],
    "desc": "Word·Excel·PowerPoint와 Windows에서 쓰는 Microsoft의 AI 비서",
    "url": "https://copilot.microsoft.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: Copilot 앱·웹 사용",
      "Microsoft 365 Personal: 월 $9.99부터",
      "Microsoft 365 Premium: 월 $19.99 (Office 앱 내 Copilot, 가장 큰 사용량)"
    ],
    "pros": [
      "Word·Excel·PowerPoint 안에서 바로 사용",
      "Windows·Edge에 기본 연동",
      "리서치와 데이터 분석 기능 제공"
    ],
    "useCase": "문서 작성, 엑셀 분석, 발표 자료 만들기",
    "id": 37
  },
  {
    "name": "Notion AI",
    "categories": [
      "문서·업무"
    ],
    "desc": "Notion 문서·데이터베이스 안에서 요약·작성·검색을 도와주는 AI",
    "url": "https://www.notion.com/product/ai",
    "priceType": "freemium",
    "priceDetail": [
      "무료·Plus: AI는 제한된 체험",
      "Business: 인당 월 $20 (연간 결제, AI 포함)"
    ],
    "pros": [
      "쓰던 노트와 문서 안에서 바로 AI 사용",
      "워크스페이스 전체를 검색하며 질문 가능",
      "회의 노트와 요약 자동화"
    ],
    "useCase": "회의록 정리, 문서 초안, 팀 지식 검색",
    "id": 38
  },
  {
    "name": "Gamma",
    "categories": [
      "시각화·PPT"
    ],
    "desc": "프롬프트로 PPT를 만들어 주는 AI",
    "url": "https://gamma.app/",
    "priceType": "freemium",
    "priceDetail": [
      "Plus 월간 $12"
    ],
    "pros": [
      "몇 분 만에 초안 완성 가능"
    ],
    "useCase": "발표 초안, 빠른 공유용 자료",
    "id": 39
  },
  {
    "name": "Otter.ai",
    "categories": [
      "회의록·기록"
    ],
    "desc": "실시간 회의에 봇이 참여해 영문 전사 및 회의록을 생성하는 글로벌 툴",
    "url": "https://otter.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "Basic 무료: 매월 300분 (1회 미팅당 최대 30분)",
      "Pro: 연간 결제 시 월 $8.33 / 월간 결제 시 $16.99"
    ],
    "pros": [
      "주요 화상회의(Zoom, Teams, Meet) 캘린더 자동 연동, 실시간 화면 캡처 및 영문 회의록 템플릿 요약 우수"
    ],
    "useCase": "글로벌 영어 화상 미팅 실시간 전사, 해외 바이어 미팅 및 웨비나 기록",
    "id": 40
  },
  {
    "name": "다글로",
    "categories": [
      "회의록·기록"
    ],
    "desc": "회의 녹음, 유튜브 링크, 오디오 파일을 텍스트로 바꾸고 분석하는 기록 AI",
    "url": "https://daglo.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 매월 1,000 크레딧(약 4시간 상당)",
      "Pro: 월 11,900원부터"
    ],
    "pros": [
      "녹음 내용을 바탕으로 PPT 슬라이드 및 퀴즈 제작 기능이 있음",
      "받아쓴 텍스트 기반 대화형 질의응답(보드챗) 가능",
      "노션 연결성"
    ],
    "useCase": "강의 및 사내 교육 내용 복습, 인터뷰 자료 정리, 회의 내용 바탕 발표자료(PPT/퀴즈) 빠른 초안 제작",
    "id": 41
  },
  {
    "name": "클로바노트",
    "categories": [
      "회의록·기록"
    ],
    "desc": "네이버 하이퍼클로바 기반으로 한국어 구어체까지 정확히 받아적는 서비스",
    "url": "https://clovanote.naver.com/",
    "priceType": "freemium",
    "priceDetail": [
      "매월 300분 무료 (데이터 수집 동의 시 최대 600분)"
    ],
    "pros": [
      "한국어 구어체/방언 인식률 최상급",
      "화자 분리 우수",
      "네이버 계정 연동 및 모바일-PC 동기화 편리"
    ],
    "useCase": "오프라인 미팅 녹음 및 전사, 인터뷰 정리, 회의 시간대별 핵심 요약",
    "id": 42
  },
  {
    "name": "Dify",
    "categories": [
      "자동화"
    ],
    "desc": "AI 챗봇, 에이전트, AI 작업 흐름을 코딩 없이 만드는 오픈소스 플랫폼",
    "url": "https://dify.ai/ko",
    "priceType": "freemium",
    "priceDetail": [
      "무료(Sandbox): 메시지 크레딧 200, 멤버 1명, 앱 5개",
      "Professional: $59/월 (월 5,000 크레딧)",
      "Team: $159/월 (월 1만 크레딧)",
      "직접 설치(셀프호스팅): 무료"
    ],
    "pros": [
      "AI 챗봇, 에이전트, AI 작업 흐름을 코딩 없이 제작",
      "사내 문서를 올려 그 내용으로 답하는 챗봇을 만들 수 있음",
      "가입 직후 기본 크레딧으로 AI 모델 사용 가능",
      "오픈소스라 직접 설치하면 무료"
    ],
    "useCase": "고객 문의 응대 챗봇, 문서 요약과 분류처럼 AI가 중심인 업무",
    "id": 43
  },
  {
    "name": "Make",
    "categories": [
      "자동화"
    ],
    "desc": "여러 앱을 블록처럼 이어 붙여 반복 업무를 자동화하는 노코드 도구",
    "url": "https://www.make.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 1,000 크레딧, 활성 시나리오 2개, 최소 실행 간격 15분 (기간 제한 없음)",
      "Core: 월 $9부터 (연간 결제 기준, 1만 크레딧)",
      "상위: Pro, Teams, Enterprise"
    ],
    "pros": [
      "블록을 이어 붙이는 방식이라 흐름이 한눈에 보임",
      "AI 도우미 Maia에게 말로 설명하면 시나리오 초안을 만들어줌 (베타)",
      "자체 AI 모듈이 있어 외부 AI 가입 없이 요약 같은 작업이 가능",
      "실행 후 모듈마다 처리 결과를 눌러서 확인할 수 있음",
      "무료 플랜이 기간 제한 없이 유지됨 (월 1,000 크레딧)"
    ],
    "useCase": "코딩 없이 구글 시트, 메일, 메신저 등 여러 앱 사이의 반복 업무를 자동화",
    "id": 44
  },
  {
    "name": "n8n",
    "categories": [
      "자동화"
    ],
    "desc": "자유도가 높은 워크플로 자동화 도구로, 직접 설치하면 무료",
    "url": "https://n8n.io/",
    "priceType": "freemium",
    "priceDetail": [
      "클라우드: 영구 무료 플랜 없음, 14일 무료 체험",
      "Starter: 월 €20부터 (연간 결제 기준, 실행 2,500회)",
      "직접 설치(Community Edition): 무료, 실행 횟수 무제한"
    ],
    "pros": [
      "직접 설치하면 무료이고 실행 횟수 제한이 없음",
      "단계 수가 아니라 실행 1회 단위로 계산해 복잡한 흐름에 유리",
      "코드를 섞어 쓸 수 있어 자유도가 가장 높음",
      "데이터를 자체 서버에 둘 수 있음"
    ],
    "useCase": "개발 인력이 있고, 자동화 실행량이 많거나 데이터를 사내에 두어야 하는 경우",
    "id": 45
  },
  {
    "name": "Zapier",
    "categories": [
      "자동화"
    ],
    "desc": "수천 개 앱을 연결해 반복 업무를 자동화하는 노코드 도구",
    "url": "https://zapier.com/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 월 100 task, 2단계 Zap",
      "Professional: 월 $19.99부터 (연간 결제, 750 task)",
      "월간 결제 시 월 $29.99"
    ],
    "pros": [
      "연결할 수 있는 앱이 매우 많음",
      "템플릿으로 빠르게 시작",
      "AI 기능과 결합 가능"
    ],
    "useCase": "메일·시트·메신저 사이의 반복 업무 자동화",
    "id": 46
  },
  {
    "name": "Genspark",
    "categories": [
      "범용 AI 에이전트"
    ],
    "desc": "대시보드를 간단하게 만들어 보고 싶을 때 추천",
    "url": "https://www.genspark.ai/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 매일 100 크레딧",
      "1단계(월 10,000 크레딧): 월 $24.99",
      "2단계(월 21,000 크레딧): 월 $49.99",
      "3단계(월 125,000 크레딧): 월 $249.99"
    ],
    "pros": [
      "용도에 맞는 대시보드 템플릿을 다양하게 제공",
      "만들어지는 과정을 단계별로 세세하게 보여줌",
      "대시보드를 단계에 맞게 체계적으로 완성"
    ],
    "useCase": "대시보드 제작 과정을 단계별로 확인하며 빠르게 시각화/초안을 만들고 싶을 때",
    "id": 47
  },
  {
    "name": "Manus",
    "categories": [
      "범용 AI 에이전트"
    ],
    "desc": "자료 조사를 다양한 곳에서 하고 싶고 ppt의 대략적인 흐름만 파악하고 싶을 때 사용하면 좋은 AI",
    "url": "https://manus.im/",
    "priceType": "freemium",
    "priceDetail": [
      "무료: 매일 300 크레딧 (작업 2개 정도 요청하면 소진되는 양)",
      "Pro(월 4,000 크레딧): 3개월간 월 $10, 이후 월 $20",
      "Pro(월 8,000 크레딧): 3개월간 월 $30, 이후 월 $40",
      "Pro(월 40,000 크레딧): 3개월간 월 $190, 이후 월 $200"
    ],
    "pros": [
      "출처 제대로 표기",
      "다양한 곳에서 데이터 수집"
    ],
    "useCase": "다양한 곳에서 자료 조사하기를 원할 때",
    "id": 48
  }
];
