# raw_trade_data.csv 파일 활용
# hscode가 85로 시작하는 (반도체류) + 국가명 미국 또는 베트남 + 수출금액 0보다 큰 수(실제 수출실적이 있는)
# 다중 조건으로 필터링한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv로 저장
# streamlit 사용 streamlit run 090802.py
# 코드 버전 다시 시도123123

import base64
from pathlib import Path
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 설정 및 소프트 파스텔 테마 적용
# ==========================================
st.set_page_config(
    page_title="반도체류(HS 85) 수출 실적 대시보드",
    page_icon="🌸",
    layout="wide",
)

current_dir = Path(__file__).resolve().parent
font_path = current_dir.parent / "day3" / "NanumGothic.ttf"
csv_path = current_dir.parent / "common" / "raw_trade_data.csv"
output_path = current_dir / "report.csv"

# 폰트 로드
font_css = ""
if font_path.exists():
    with open(font_path, "rb") as f:
        font_data = base64.b64encode(f.read()).decode()
    font_css = f"""
        @font-face {{
            font-family: 'NanumGothic';
            src: url(data:font/truetype;charset=utf-8;base64,{font_data}) format('truetype');
        }}
        html, body, [class*="css"], div, span, p, h1, h2, h3, button, input {{
            font-family: 'NanumGothic', sans-serif !important;
        }}
    """

# 눈이 편안한 소프트 파스텔 라벤더 스타일링
st.markdown(
    f"""
    <style>
    {font_css}

    /* 상단 헤더 배너: 부드러운 라벤더-블루 파스텔 그라데이션 */
    .pastel-header {{
        background: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 100%);
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        border: 1px solid #E9D5FF;
    }}
    .pastel-header h1 {{
        color: #4C1D95 !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }}
    .pastel-header p {{
        color: #6D28D9 !important;
        font-size: 0.95rem;
        margin: 6px 0 0 0;
        opacity: 0.85;
    }}

    /* 메트릭 카드: 은은한 파스텔 배경 & 부드러운 텍스트 */
    .metric-card {{
        background: linear-gradient(145deg, #FAF5FF 0%, #F5F3FF 100%);
        padding: 18px 20px;
        border-radius: 14px;
        border: 1px solid #EDE9FE;
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.04);
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: #DDD6FE;
        box-shadow: 0 4px 10px rgba(139, 92, 246, 0.08);
    }}
    .metric-title {{
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 1.55rem;
        font-weight: 800;
        color: #4338CA;
        letter-spacing: -0.3px;
    }}
    .metric-sub {{
        font-size: 0.78rem;
        color: #7C3AED;
        margin-top: 5px;
        font-weight: 500;
    }}

    /* 탭 스타일 조정 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0px 0px;
        padding: 8px 16px;
        color: #64748B;
    }}
    .stTabs [aria-selected="true"] {{
        color: #6D28D9 !important;
        font-weight: bold;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_and_filter_data(file_path: Path):
    if not file_path.exists():
        return None, None

    try:
        raw_df = pd.read_csv(file_path, dtype={"hs_code": str})
    except UnicodeDecodeError:
        raw_df = pd.read_csv(file_path, encoding="cp949", dtype={"hs_code": str})

    raw_df.columns = raw_df.columns.str.strip()

    if "수출금액" in raw_df.columns:
        raw_df["수출금액"] = (
            raw_df["수출금액"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        raw_df["수출금액"] = pd.to_numeric(raw_df["수출금액"], errors="coerce").fillna(0)

    # 조건 필터링
    cond_hs = raw_df["hs_code"].astype(str).str.strip().str.startswith("85")
    cond_country = raw_df["국가명"].astype(str).str.strip().isin(["미국", "베트남"])
    cond_amount = raw_df["수출금액"] > 0

    filtered = raw_df[cond_hs & cond_country & cond_amount].copy()
    top_10 = filtered.sort_values(by="수출금액", ascending=False).head(10).reset_index(drop=True)
    top_10.index = top_10.index + 1

    return filtered, top_10


if not csv_path.exists():
    st.error(f"⚠️ 데이터 파일을 찾을 수 없습니다: `{csv_path}`")
    st.stop()

filtered_df, top10_df = load_and_filter_data(csv_path)
top10_df.to_csv(output_path, index=False, encoding="utf-8-sig")

# ==========================================
# 3. 상단 파스텔 헤더
# ==========================================
st.markdown(
    """
    <div class="pastel-header">
        <h1>📊 반도체류(HS 85) 미국 · 베트남 수출 실적 리포트</h1>
        <p>실제 수출 실적이 발생한 HS Code 85 품목 대상 주요 통계 대시보드</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 4. 주요 수치 카드 (파스텔 그라데이션)
# ==========================================
top10_total = top10_df["수출금액"].sum()
all_filtered_total = filtered_df["수출금액"].sum()
max_export = top10_df["수출금액"].max() if not top10_df.empty else 0
us_total = filtered_df[filtered_df["국가명"] == "미국"]["수출금액"].sum()
vn_total = filtered_df[filtered_df["국가명"] == "베트남"]["수출금액"].sum()

us_ratio = (us_total / all_filtered_total * 100) if all_filtered_total > 0 else 0
vn_ratio = (vn_total / all_filtered_total * 100) if all_filtered_total > 0 else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">상위 10건 합계</div>
            <div class="metric-value">{top10_total:,.0f}</div>
            <div class="metric-sub">전체 대비 {(top10_total / all_filtered_total * 100) if all_filtered_total > 0 else 0:.1f}% 점유</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">조건 충족 총 실적</div>
            <div class="metric-value">{all_filtered_total:,.0f}</div>
            <div class="metric-sub">총 {len(filtered_df):,}건 거래 발생</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">단일 최고 실적 (1위)</div>
            <div class="metric-value">{max_export:,.0f}</div>
            <div class="metric-sub">{top10_df.iloc[0]['국가명'] if not top10_df.empty else '-'} 대상 품목</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">국가별 실적 비중</div>
            <div class="metric-value">미 {us_ratio:.0f}% : 베 {vn_ratio:.0f}%</div>
            <div class="metric-sub">미국 {us_total:,.0f} / 베트남 {vn_total:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ==========================================
# 5. 시각화 & 데이터 분석 탭
# ==========================================
tab1, tab2, tab3 = st.tabs(["📈 시각화 차트", "🏆 TOP 10 상세 내역", "📋 전체 데이터 조회"])

with tab1:
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.subheader("상위 10건 품목별 수출 실적")
        label_col = "품목명" if "품목명" in top10_df.columns else "hs_code"
        chart_data = top10_df[[label_col, "수출금액", "국가명"]].copy()
        chart_data["라벨"] = chart_data[label_col].astype(str) + " (" + chart_data["국가명"] + ")"
        
        # 은은한 라벤더/소프트 바이올렛 컬러 차트
        st.bar_chart(
            data=chart_data.set_index("라벨")["수출금액"],
            color="#A78BFA",
            use_container_width=True,
        )

    with chart_col2:
        st.subheader("국가별 수출액 합계")
        country_summary = (
            filtered_df.groupby("국가명")["수출금액"]
            .sum()
            .reindex(["미국", "베트남"])
            .fillna(0)
        )
        st.bar_chart(
            data=country_summary,
            color="#C4B5FD",
            use_container_width=True,
        )

with tab2:
    st.subheader("🏆 상위 10건 목록")
    
    column_config = {
        "수출금액": st.column_config.ProgressColumn(
            "수출금액",
            help="수출 실적 순위",
            format="%d",
            min_value=0,
            max_value=float(top10_df["수출금액"].max()) if not top10_df.empty else 1,
        )
    }

    st.dataframe(
        top10_df,
        use_container_width=True,
        column_config=column_config,
    )

    down_col1, down_col2 = st.columns([3, 1])
    with down_col1:
        st.caption(f"📁 결과 파일이 저장되었습니다: `{output_path.name}`")
    with down_col2:
        csv_download = top10_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 report.csv 다운로드",
            data=csv_download,
            file_name="report.csv",
            mime="text/csv",
            use_container_width=True,
        )

with tab3:
    st.subheader(f"전체 필터링 데이터 ({len(filtered_df):,}건)")
    st.dataframe(filtered_df, use_container_width=True)