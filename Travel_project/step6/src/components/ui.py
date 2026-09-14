from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st

def render_official_link(site_name: str, url: str):
    """공식 관광 정보 포털 바로가기 배너 버튼"""
    st.link_button(f"🔗 {site_name} 공식 관광 정보 바로가기", url, use_container_width=True)

def render_time_difference(country_name: str, tz_info_list: list):
    """
    한국 시간과 현지 시간을 직관적인 비교 카드로 표시
    tz_info_list: [{"label": "도쿄", "tz": "Asia/Tokyo"}, ...]
    """
    now_kr = datetime.now(ZoneInfo("Asia/Seoul"))
    
    st.markdown("##### 🕒 시차 및 현지 시각 비교")
    cols = st.columns(len(tz_info_list) + 1)
    
    with cols[0]:
        st.markdown(
            f"""
            <div style="background:#f1f5f9; padding:12px; border-radius:10px; border-left:4px solid #3b82f6; text-align:center;">
                <span style="font-size:12px; color:#64748b; font-weight:bold;">기준 국가</span><br>
                <b style="font-size:16px; color:#1e293b;">🇰🇷 서울 (한국)</b><br>
                <span style="font-size:20px; font-weight:800; color:#0f172a;">{now_kr.strftime('%H:%M')}</span><br>
                <span style="font-size:11px; color:#64748b;">{now_kr.strftime('%m월 %d일 (%a)')}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    for idx, target in enumerate(tz_info_list, start=1):
        target_tz = ZoneInfo(target["tz"])
        now_target = datetime.now(target_tz)
        
        diff_hours = int((now_target.utcoffset() - now_kr.utcoffset()).total_seconds() / 3600)
        if diff_hours > 0:
            diff_str = f"한국보다 +{diff_hours}시간 빠름"
        elif diff_hours < 0:
            diff_str = f"한국보다 {abs(diff_hours)}시간 느림"
        else:
            diff_str = "한국과 시차 없음"
            
        with cols[idx]:
            st.markdown(
                f"""
                <div style="background:#f8fafc; padding:12px; border-radius:10px; border-left:4px solid #10b981; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <span style="font-size:12px; color:#059669; font-weight:bold;">{diff_str}</span><br>
                    <b style="font-size:16px; color:#1e293b;">{target['label']}</b><br>
                    <span style="font-size:20px; font-weight:800; color:#0f172a;">{now_target.strftime('%H:%M')}</span><br>
                    <span style="font-size:11px; color:#64748b;">{now_target.strftime('%m월 %d일 (%a)')}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)

def render_weather_card(weather: dict, city_label: str):
    """그라데이션 및 뱃지 스타일을 적용한 고시인성 날씨 카드"""
    if "error" in weather:
        st.error(weather["error"])
        return

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 18px 22px; border-radius: 14px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="background:rgba(255,255,255,0.2); padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold;">LIVE WEATHER</span>
                    <h3 style="margin:6px 0 0 0; font-size:22px; color:white;">{city_label}</h3>
                    <p style="margin:2px 0 0 0; font-size:14px; opacity:0.9;">{weather.get('description', '')}</p>
                </div>
                <img src="{weather.get('icon_url', '')}" style="width:70px; height:70px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));" />
            </div>
            <div style="display:flex; align-items:baseline; margin-top:10px;">
                <span style="font-size:38px; font-weight:900; letter-spacing:-1px;">{weather.get('temp', '-')}°C</span>
                <span style="font-size:13px; margin-left:12px; opacity:0.85;">체감 {weather.get('feels_like', '-')}°C</span>
            </div>
            <div style="display:flex; gap:12px; margin-top:12px; padding-top:10px; border-top: 1px solid rgba(255,255,255,0.15); font-size:12px; opacity:0.9;">
                <span>💧 습도 <b>{weather.get('humidity', '-')}%</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_instant_exchange_widget(currency_code: str, base_rate: float, spread: float = 1.75):
    """진입 즉시 환율 정보가 시각화되고 간편 계산이 가능한 위젯"""
    spread_factor = spread / 100.0
    buy_rate = base_rate * (1 + spread_factor)
    sell_rate = base_rate * (1 - spread_factor)

    st.markdown(
        f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; padding:15px; border-radius:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:8px;">
                <b style="font-size:15px; color:#334155;">실시간 {currency_code} 환율 안내</b>
                <span style="font-size:11px; color:#64748b;">기준율 1 {currency_code} = <b>{base_rate:,.2f}원</b></span>
            </div>
            <div style="display:flex; justify-content:space-around; margin-top:12px; text-align:center;">
                <div style="flex:1; border-right:1px solid #f1f5f9;">
                    <span style="font-size:12px; color:#ef4444; font-weight:bold;">현찰 살 때 (환전)</span><br>
                    <span style="font-size:18px; font-weight:800; color:#dc2626;">{buy_rate:,.2f}원</span>
                </div>
                <div style="flex:1;">
                    <span style="font-size:12px; color:#3b82f6; font-weight:bold;">현찰 팔 때 (재환전)</span><br>
                    <span style="font-size:18px; font-weight:800; color:#2563eb;">{sell_rate:,.2f}원</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    with st.expander("🧮 직접 환율 계산기 열기", expanded=False):
        calc_mode = st.radio(
            "계산 모드",
            [f"원화(KRW) ➡️ {currency_code} (여행 갈 때)", f"{currency_code} ➡️ 원화(KRW) (돌아왔을 때)"],
            horizontal=True,
            key=f"mode_{currency_code}"
        )
        if "KRW ➡️" in calc_mode:
            krw_in = st.number_input("환전할 원화 금액(KRW)", min_value=1000, value=100000, step=10000, key=f"k_{currency_code}")
            st.success(f"👉 현찰 예상 수령액: **{krw_in / buy_rate:,.2f} {currency_code}**")
        else:
            foreign_in = st.number_input(f"재환전할 금액({currency_code})", min_value=1, value=100, step=10, key=f"f_{currency_code}")
            st.success(f"👉 원화 환산 예상 수령액: **{foreign_in * sell_rate:,.0f} KRW**")