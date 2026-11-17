import os  # 환경 변수(.env 에서 읽은 값)를 꺼내 쓰는 파이썬 기본 부품
import sys  # 문제가 있을 때 프로그램을 끝내는 파이썬 기본 부품
from pathlib import Path  # 파일 위치(경로)를 다루는 파이썬 기본 부품

from dotenv import load_dotenv  # .env 파일의 값을 환경 변수로 불러 주는 부품
from langchain_core.prompts import ChatPromptTemplate  # 빈칸이 있는 질문 틀(프롬프트 템플릿)을 만드는 부품
from langchain_openai import ChatOpenAI  # OpenAI 채팅 모델을 부르는 부품


def main():
    """.env 를 읽고, 'CIF' 설명을 모델에게 딱 한 번 물어 결과를 출력해요."""
    env_path = Path(__file__).parent / ".env"  # 이 파일과 같은 폴더의 .env 위치를 만든다
    if not env_path.exists():  # .env 파일이 없는지 확인한다
        print(".env 파일이 없어요. .env.example 을 .env 로 복사하고 키를 직접 넣어 주세요.")  # 쉬운 안내 문구를 보여 준다
        sys.exit(1)  # 프로그램을 여기서 끝낸다
    load_dotenv(env_path)  # .env 의 값(키, 모델 이름)을 환경 변수로 불러온다 (내용은 출력하지 않는다)

    model_name = os.getenv("OPENAI_MODEL")  # .env 에 적어 둔 대화 모델 이름을 꺼낸다
    if not os.getenv("OPENAI_API_KEY") or not model_name:  # 키나 모델 이름이 비어 있는지 확인한다
        print(".env 에 OPENAI_API_KEY 와 OPENAI_MODEL 값이 모두 있어야 해요.")  # 쉬운 안내 문구를 보여 준다
        sys.exit(1)  # 프로그램을 여기서 끝낸다

    prompt = ChatPromptTemplate.from_template(  # 질문 틀을 만든다 ({term} 자리에 나중에 단어가 들어간다)
        "너는 무역 초보를 돕는 선생님이야. {term} 을 비전공자도 알게 두 문장으로 설명해 줘."  # 모델에게 보낼 질문 문장 틀
    )  # 질문 틀 만들기 끝
    model = ChatOpenAI(model=model_name, reasoning_effort="low")  # 모델 이름은 .env 에서, 생각 깊이는 "낮음"으로 채팅 모델을 준비한다

    chain = prompt | model  # 질문 틀 다음에 모델이 이어지도록 한 줄로 연결한다 (체인)
    try:  # 호출이 실패해도 쉬운 말로 알려 주려고 감싼다
        response = chain.invoke({"term": "CIF"})  # {term} 에 "CIF" 를 넣어 모델을 딱 한 번 부른다
    except Exception as e:  # 호출 중 문제가 생기면 여기로 온다
        print(f"모델 호출에 실패했어요 ({type(e).__name__}). 키와 모델 이름을 확인해 주세요.")  # 오류 종류만 알려 준다 (키가 섞일 수 있어서 자세한 내용은 숨김)
        sys.exit(1)  # 프로그램을 여기서 끝낸다

    print(f"모델: {model_name}")  # 어떤 모델로 불렀는지 보여 준다
    print(response.content)  # 모델이 돌려준 설명 글만 꺼내 보여 준다


if __name__ == "__main__":  # 이 파일을 직접 실행했을 때만 아래를 실행한다는 뜻
    main()  # 위에서 만든 main 함수를 실행한다
