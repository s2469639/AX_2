# OpenAI + streamlit 앱 
# 질문 하나 입력하면 OpenAI chat Completions API 한번 호출
# 답변을 받아오는 가장 단순한 방법
# 대화기록을 기억하지 않는 단발성 질문-답변
# streamlit run newchatbot.py

import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title='첫번째 챗봇', page_icon='🤖')
st.title('예제1: 나의 첫번째 챗봇')
st.caption('단발성 질문-답변 & 토큰 비용 감 잡기')

# 사이드바 (API 키 입력 & 모델 선택)
with st.sidebar:
    st.header('설정')
    api_key = st.text_input(
        "OpenAI API Key",
        type='password',
        help='sk-로 시작하는 OpenAI API key를 입력하세요.'
    )
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o', 'gpt-4'], index=0)
    st.markdown('[API 발급 받기](https://openai.com/ko-KR/index/openai-api/)')

# 메인 화면: 질문 입력창
question = st.text_input('질문을 입력하세요', placeholder='예: 오늘 공부 하나도 안 했는데 어떡하죠?')

# ----------------- 빨간색 버튼 스타일 적용 -----------------
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #ff4b4b;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}
div.stButton > button:first-child:hover {
    background-color: #d32f2f;
    color: white;
}
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------------

# 버튼 클릭 시 실행
if st.button('🔥 팩트폭격 받기'):
    if not api_key:
        st.error('API 키를 먼저 입력해 줘!')
    elif not question:
        st.warning('질문 내용을 적어줘야 답변을 하지!')
    else:
        try:
            client = OpenAI(api_key=api_key)

            with st.spinner('답변을 생각하는 중...'):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            # 친근한 반말 + 극 T 팩폭 + 2~3문장 제한 프롬프트
                            "content": (
                                "너는 감정적 공감 없이 오직 논리와 팩트로만 승부하는 극 T 성향의 친구야. "
                                "상투적이고 딱딱한 설명문투는 절대 쓰지 말고, 친근하고 털털한 '반말'로 말해. "
                                "구구절절 길게 말하지 말고 딱 2~3문장 안으로 간결하게 핵심만 찔러서 답변해."
                            )
                        },
                        {"role": "user", "content": question}
                    ]
                )

            # 답변 화면 출력
            answer = response.choices[0].message.content
            st.markdown("### 🤖 팩폭 답변")
            st.write(answer)

            # 토큰 사용량 확인 메트릭
            usage = response.usage
            st.divider()
            st.subheader("📊 사용된 토큰 수")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="입력 토큰", value=usage.prompt_tokens)
            col2.metric(label="출력 토큰", value=usage.completion_tokens)
            col3.metric(label="총 토큰", value=usage.total_tokens)

        except Exception as e:
            st.error(f"문제가 생겼어: {e}")