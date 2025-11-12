#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 인센티브 대시보드 - Streamlit Web App
실시간 데이터 분석 및 모바일 반응형 지원
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import glob
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, List
import base64
import sys

# Add parent directory to path for imports (if needed)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 페이지 설정 - 반드시 맨 처음에 실행
st.set_page_config(
    page_title="QIP 인센티브 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': None,
        'About': "# QIP 인센티브 대시보드\n실시간 인센티브 분석 시스템"
    }
)

# CSS 스타일 적용 (모바일 반응형)
st.markdown("""
<style>
    /* 모바일 반응형 스타일 */
    @media (max-width: 768px) {
        .main > div {
            padding: 0rem 0.5rem;
        }
        .stMetric > div {
            font-size: 0.8rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.2rem !important;
        }
        h3 {
            font-size: 1rem !important;
        }
    }

    /* 메트릭 카드 스타일 */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }

    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        transition: transform 0.2s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# 번역 데이터 로드
@st.cache_data
def load_translations():
    """번역 파일 로드"""
    translations_file = 'config_files/dashboard_translations.json'
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 기본값
        return {
            "languages": {"ko": "한국어", "en": "English", "vi": "Tiếng Việt"},
            "headers": {
                "title": {
                    "ko": "QIP 인센티브 대시보드",
                    "en": "QIP Incentive Dashboard",
                    "vi": "Bảng điều khiển khen thưởng QIP"
                }
            }
        }

# 데이터 로드
@st.cache_data
def load_data(month: int, year: int) -> pd.DataFrame:
    """인센티브 데이터 로드"""
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']

    month_str = month_names[month - 1] if 1 <= month <= 12 else 'september'

    # CSV 파일 패턴
    patterns = [
        f"output_files/output_QIP_incentive_{month_str}_{year}_Complete_V8.02_Complete.csv",
        f"output_QIP_incentive_{month_str}_{year}_Complete_V8.02_Complete.csv",
    ]

    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            try:
                df = pd.read_csv(files[0], encoding='utf-8-sig')
                # 숫자 컬럼 변환
                numeric_cols = ['Continuous_Months', 'Previous_Incentive', 'Final_Incentive']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                return df
            except Exception as e:
                st.error(f"데이터 로드 오류: {e}")
                return pd.DataFrame()

    return pd.DataFrame()

def create_summary_metrics(df: pd.DataFrame, lang: str = 'ko') -> None:
    """요약 메트릭 표시"""
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    col1, col2, col3, col4 = st.columns(4)

    labels = {
        'ko': ['총 직원', '인센티브 수령', '총 인센티브', '평균 인센티브'],
        'en': ['Total Employees', 'Received Incentive', 'Total Incentive', 'Average Incentive'],
        'vi': ['Tổng nhân viên', 'Nhận thưởng', 'Tổng thưởng', 'Thưởng trung bình']
    }

    current_labels = labels.get(lang, labels['ko'])

    with col1:
        st.metric(current_labels[0], f"{len(df):,}")

    with col2:
        received = len(df[df['Final_Incentive'] > 0])
        percentage = (received / len(df) * 100) if len(df) > 0 else 0
        st.metric(current_labels[1], f"{received:,}", f"{percentage:.1f}%")

    with col3:
        total = df['Final_Incentive'].sum()
        st.metric(current_labels[2], f"₫{total:,.0f}")

    with col4:
        avg = df['Final_Incentive'].mean()
        st.metric(current_labels[3], f"₫{avg:,.0f}")

def create_charts(df: pd.DataFrame, lang: str = 'ko') -> None:
    """차트 생성"""
    if df.empty:
        return

    # 색상 테마
    colors = ['#667eea', '#764ba2', '#f093fb', '#fda085', '#84fab0']

    # 2개 컬럼으로 차트 배치
    col1, col2 = st.columns(2)

    with col1:
        # TYPE별 분포 파이 차트
        st.subheader("TYPE별 직원 분포" if lang == 'ko' else "Employee Distribution by TYPE")
        type_counts = df['TYPE'].value_counts()
        fig_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            color_discrete_sequence=colors
        )
        fig_pie.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 인센티브 분포 히스토그램
        st.subheader("인센티브 금액 분포" if lang == 'ko' else "Incentive Amount Distribution")
        df_with_incentive = df[df['Final_Incentive'] > 0]
        fig_hist = px.histogram(
            df_with_incentive,
            x='Final_Incentive',
            nbins=20,
            color_discrete_sequence=[colors[0]]
        )
        fig_hist.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="인센티브 (₫)" if lang == 'ko' else "Incentive (₫)",
            yaxis_title="직원 수" if lang == 'ko' else "Employee Count"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Position별 평균 인센티브 (가로 막대 차트)
    st.subheader("직급별 평균 인센티브" if lang == 'ko' else "Average Incentive by Position")
    position_avg = df.groupby('Position')['Final_Incentive'].mean().sort_values(ascending=True).tail(10)

    fig_bar = px.bar(
        x=position_avg.values,
        y=position_avg.index,
        orientation='h',
        color_discrete_sequence=[colors[1]]
    )
    fig_bar.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="평균 인센티브 (₫)" if lang == 'ko' else "Average Incentive (₫)",
        yaxis_title="직급" if lang == 'ko' else "Position"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

def show_employee_details(df: pd.DataFrame, lang: str = 'ko') -> None:
    """직원 상세 정보 표시"""
    st.subheader("직원 상세 정보 검색" if lang == 'ko' else "Employee Details Search")

    # 검색 옵션
    col1, col2 = st.columns([1, 3])

    with col1:
        search_type = st.selectbox(
            "검색 방식" if lang == 'ko' else "Search Type",
            ["이름" if lang == 'ko' else "Name",
             "ID",
             "부서" if lang == 'ko' else "Department"]
        )

    with col2:
        if search_type in ["이름", "Name"]:
            search_value = st.text_input("직원 이름 입력" if lang == 'ko' else "Enter Employee Name")
            if search_value:
                mask = df['Name'].str.contains(search_value, case=False, na=False)
        elif search_type == "ID":
            search_value = st.text_input("직원 ID 입력" if lang == 'ko' else "Enter Employee ID")
            if search_value:
                mask = df['ID'].astype(str).str.contains(search_value, na=False)
        else:
            departments = df['Section'].unique()
            search_value = st.selectbox("부서 선택" if lang == 'ko' else "Select Department", departments)
            mask = df['Section'] == search_value

    if search_value:
        filtered_df = df[mask]

        if not filtered_df.empty:
            # 주요 컬럼만 표시
            display_cols = ['ID', 'Name', 'Position', 'Section', 'TYPE',
                          'Continuous_Months', 'Final_Incentive']

            st.dataframe(
                filtered_df[display_cols].style.format({
                    'Final_Incentive': '₫{:,.0f}',
                    'Continuous_Months': '{:.0f}'
                }),
                use_container_width=True
            )

            # 다운로드 버튼
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드" if lang == 'ko' else "📥 Download CSV",
                data=csv,
                file_name=f"employee_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("검색 결과가 없습니다." if lang == 'ko' else "No results found.")

def main():
    """메인 함수"""
    # 번역 데이터 로드
    translations = load_translations()

    # 사이드바
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100?text=QIP+Dashboard", use_column_width=True)
        st.markdown("---")

        # 언어 선택
        lang_options = {'한국어': 'ko', 'English': 'en', 'Tiếng Việt': 'vi'}
        selected_lang_name = st.selectbox("🌐 언어 / Language", list(lang_options.keys()))
        lang = lang_options[selected_lang_name]

        st.markdown("---")

        # 날짜 선택
        current_date = datetime.now()
        year = st.selectbox("📅 연도", range(2024, 2027), index=1)
        month = st.selectbox("📅 월", range(1, 13), index=current_date.month - 1)

        # 데이터 새로고침 버튼
        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")

        # 정보 표시
        st.info(
            "💡 이 대시보드는 실시간으로 업데이트됩니다.\n"
            "📱 모바일에서도 완벽하게 작동합니다."
            if lang == 'ko' else
            "💡 This dashboard updates in real-time.\n"
            "📱 Works perfectly on mobile devices."
        )

    # 메인 컨텐츠
    title_text = translations.get('headers', {}).get('title', {}).get(lang, 'QIP Incentive Dashboard')
    st.title(f"📊 {title_text}")
    st.markdown(f"### {year}년 {month}월 인센티브 현황" if lang == 'ko' else f"### {year} {month} Incentive Status")

    # 데이터 로드
    with st.spinner("데이터 로딩 중..." if lang == 'ko' else "Loading data..."):
        df = load_data(month, year)

    if not df.empty:
        # 탭 생성
        tab1, tab2, tab3 = st.tabs([
            "📈 대시보드" if lang == 'ko' else "📈 Dashboard",
            "👥 직원 검색" if lang == 'ko' else "👥 Employee Search",
            "📊 상세 분석" if lang == 'ko' else "📊 Detailed Analysis"
        ])

        with tab1:
            # 요약 메트릭
            create_summary_metrics(df, lang)
            st.markdown("---")

            # 차트
            create_charts(df, lang)

        with tab2:
            show_employee_details(df, lang)

        with tab3:
            st.subheader("조건별 달성률" if lang == 'ko' else "Condition Achievement Rate")

            # 10개 조건 분석
            condition_cols = [col for col in df.columns if col.startswith('Condition_')]
            if condition_cols:
                condition_stats = []
                for col in condition_cols:
                    yes_count = (df[col] == 'YES').sum()
                    total = len(df)
                    percentage = (yes_count / total * 100) if total > 0 else 0
                    condition_stats.append({
                        'Condition': col.replace('_', ' '),
                        'Achieved': yes_count,
                        'Total': total,
                        'Rate': f"{percentage:.1f}%"
                    })

                stats_df = pd.DataFrame(condition_stats)
                st.dataframe(stats_df, use_container_width=True)

                # 조건별 달성률 차트
                fig = px.bar(
                    stats_df,
                    x='Condition',
                    y='Achieved',
                    text='Rate',
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    margin=dict(l=0, r=0, t=30, b=100)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(
            f"⚠️ {year}년 {month}월 데이터를 찾을 수 없습니다."
            if lang == 'ko' else
            f"⚠️ No data found for {year}/{month}"
        )

        st.info(
            "데이터 파일이 output_files 폴더에 있는지 확인하세요."
            if lang == 'ko' else
            "Please check if data files exist in output_files folder."
        )

if __name__ == "__main__":
    main()