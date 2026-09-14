import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title='멀티턴 챗봇 & 문서 요약기', page_icon='🤖', layout='wide')

# ----------------- 세션 상태 초기화 -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "summary_result" not in st.session_state:
    st.session_state.summary_result = None

# ----------------- 사이드바 설정 (환경 설정 전용) -----------------
with st.sidebar:
    st.header('⚙️ 기본 설정')
    api_key = st.text_input(
        "OpenAI API Key",
        type='password',
        help='sk-로 시작하는 OpenAI API key를 입력하세요.'
    )
    model = st.selectbox('모델 선택', ['gpt-4o-mini', 'gpt-4o', 'gpt-4'], index=0)
    
    st.divider()

    # 시스템 메시지 설정
    st.subheader('🎭 챗봇 성향 설정')
    default_system_prompt = (
        "너는 감정적 공감 없이 오직 논리와 팩트로만 승부하는 극 T 성향의 친구야. "
        "상투적이고 딱딱한 설명문투는 절대 쓰지 말고, 친근하고 털털한 '반말'로 말해."
    )
    system_prompt = st.text_area(
        "챗봇의 성격이나 역할을 정해주세요",
        value=default_system_prompt,
        height=120
    )
    
    st.divider()
    
    # 대화 기록 초기화 버튼
    if st.button('🗑️ 대화 기록 초기화', use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown('[API 발급 받기](https://openai.com/ko-KR/index/openai-api/)')

# ----------------- 메인 화면 상단: 문서 요약 섹션 -----------------
st.title('🤖 멀티턴 대화 기억 챗봇 & 문서 요약')
st.caption('문서를 업로드해 요약하거나, 아래 채팅창에서 챗봇과 자유롭게 대화해 보세요.')

# 메인 페이지에 배치한 문서 요약 영역 (화면을 깔끔하게 유지하기 위해 expander 활용)
with st.expander('📄 **문서 업로드 및 요약 정리 (README / TXT)**', expanded=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("파일 업로드 (.md, .txt)", type=['md', 'txt'])
    
    with col2:
        summary_length = st.select_slider(
            '요약 분량 조절',
            options=['아주 짧게 (1~2줄)', '보통 (3~5개 불릿)', '상세히 (섹션별 분석)'],
            value='보통 (3~5개 불릿)'
        )
        run_summary = st.button('✨ 문서 요약하기', use_container_width=True)

    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode('utf-8')
            
            # 원문 미리보기 탭과 요약 결과 탭 분리
            tab_preview, tab_summary = st.tabs(["📖 원문 미리보기", "📝 요약 결과"])
            
            with tab_preview:
                st.text_area("파일 원문 내용", value=file_content, height=180, disabled=True)
            
            # 요약 실행 로직
            if run_summary:
                if not api_key:
                    st.error('사이드바에 OpenAI API 키를 먼저 입력해 줘!')
                else:
                    client = OpenAI(api_key=api_key)
                    with st.spinner('문서를 분석하고 요약 중입니다...'):
                        summary_prompt = (
                            f"다음 문서의 핵심 내용을 '{summary_length}' 기준에 맞춰 가독성 좋게 정리해줘:\n\n"
                            f"{file_content}"
                        )
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": "너는 문서의 핵심 구조와 기술적 맥락을 정확하게 파악해 전달하는 테크니컬 라이터야."},
                                {"role": "user", "content": summary_prompt}
                            ]
                        )
                        st.session_state.summary_result = response.choices[0].message.content

            with tab_summary:
                if st.session_state.summary_result:
                    st.success("요약 완료!")
                    st.markdown(st.session_state.summary_result)
                else:
                    st.info("'✨ 문서 요약하기' 버튼을 누르면 여기에 정리된 내용이 표시됩니다.")

        except Exception as e:
            st.error(f"파일을 읽는 중 문제가 발생했습니다: {e}")

st.divider()

# ----------------- 메인 화면 하단: 대화 기록 렌더링 -----------------
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ----------------- 채팅 입력창 및 스트리밍 처리 -----------------
if question := st.chat_input('질문을 입력하세요 (예: 오늘 공부 하나도 안 했는데 어떡하죠?)'):
    if not api_key:
        st.error('사이드바에 API 키를 먼저 입력해 줘!')
    else:
        try:
            client = OpenAI(api_key=api_key)

            # 1. 사용자 메시지 기록 및 출력
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # 2. 시스템 프롬프트 + 이전 대화 기록 전달
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            # 3. 답변 스트리밍
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                stream = client.chat.completions.create(
                    model=model,
                    messages=full_messages,
                    stream=True,
                )

                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        full_response += content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

            # 4. 어시스턴트 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"문제가 생겼어: {e}")