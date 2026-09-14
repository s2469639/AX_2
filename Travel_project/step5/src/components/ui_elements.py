import streamlit as st
from pathlib import Path

# 현재 파일(ui_elements.py) 위치에서 프로젝트 루트(step5) 폴더 탐색
# ui_elements.py -> components -> src -> step5 (상위로 3번 이동)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

def render_country_card(data: dict):
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        # assets 폴더 내 이미지 파일 경로 생성
        img_path = ASSETS_DIR / data["image_filename"]
        
        if img_path.exists():
            st.image(str(img_path), use_container_width=True, caption=data["name"])
        else:
            st.warning(f"⚠️ 이미지를 찾을 수 없습니다: `{img_path.name}`")

    with col2:
        st.subheader("기본 정보")
        st.markdown(f"**수도:** {data['capital']}")
        st.markdown(f"**언어:** {data['language']}")
        st.markdown(f"**통화:** {data['currency']}")
        st.write(data["description"])
        
        st.write("")
        st.link_button(
            label=f"✈️ {data['name'].split()[0]} 공식 여행 사이트 방문하기",
            url=data["travel_url"],
            type="primary"
        )