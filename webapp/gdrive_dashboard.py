#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 인센티브 대시보드 - Google Drive 자동 동기화 버전
모든 CSV 파일을 Google Drive에서 자동으로 읽어옴
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import io
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, List, Tuple
import time

# Google Drive 관련 imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    st.error("Google API 라이브러리가 필요합니다. requirements.txt를 확인하세요.")

# 페이지 설정
st.set_page_config(
    page_title="QIP 인센티브 대시보드 (Google Drive)",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/moonkaicuzui/qip-dashboard',
        'About': "# QIP 인센티브 대시보드\nGoogle Drive 자동 동기화 시스템"
    }
)

# CSS 스타일 (모바일 반응형)
st.markdown("""
<style>
    @media (max-width: 768px) {
        .main > div { padding: 0rem 0.5rem; }
        .stMetric > div { font-size: 0.8rem; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }

    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }

    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'drive_service' not in st.session_state:
    st.session_state.drive_service = None
if 'available_files' not in st.session_state:
    st.session_state.available_files = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}

# 번역 데이터
TRANSLATIONS = {
    'ko': {
        'title': 'QIP 인센티브 대시보드',
        'subtitle': 'Google Drive 자동 동기화',
        'total_employees': '총 직원',
        'received_incentive': '인센티브 수령',
        'total_incentive': '총 인센티브',
        'average_incentive': '평균 인센티브',
        'select_month': '월 선택',
        'refresh': '새로고침',
        'last_updated': '마지막 업데이트',
        'no_data': '데이터가 없습니다',
        'loading': '로딩 중...',
        'employee_search': '직원 검색',
        'dashboard': '대시보드',
        'detailed_analysis': '상세 분석'
    },
    'en': {
        'title': 'QIP Incentive Dashboard',
        'subtitle': 'Google Drive Auto Sync',
        'total_employees': 'Total Employees',
        'received_incentive': 'Received Incentive',
        'total_incentive': 'Total Incentive',
        'average_incentive': 'Average Incentive',
        'select_month': 'Select Month',
        'refresh': 'Refresh',
        'last_updated': 'Last Updated',
        'no_data': 'No data available',
        'loading': 'Loading...',
        'employee_search': 'Employee Search',
        'dashboard': 'Dashboard',
        'detailed_analysis': 'Detailed Analysis'
    },
    'vi': {
        'title': 'Bảng điều khiển khen thưởng QIP',
        'subtitle': 'Đồng bộ tự động Google Drive',
        'total_employees': 'Tổng nhân viên',
        'received_incentive': 'Nhận thưởng',
        'total_incentive': 'Tổng thưởng',
        'average_incentive': 'Thưởng trung bình',
        'select_month': 'Chọn tháng',
        'refresh': 'Làm mới',
        'last_updated': 'Cập nhật lần cuối',
        'no_data': 'Không có dữ liệu',
        'loading': 'Đang tải...',
        'employee_search': 'Tìm nhân viên',
        'dashboard': 'Bảng điều khiển',
        'detailed_analysis': 'Phân tích chi tiết'
    }
}

def get_text(key: str, lang: str = 'ko') -> str:
    """번역된 텍스트 가져오기"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['ko']).get(key, key)

@st.cache_resource
def init_google_drive_service():
    """Google Drive 서비스 초기화"""
    if not GOOGLE_API_AVAILABLE:
        return None

    try:
        # Streamlit Secrets에서 credentials 가져오기
        credentials_dict = st.secrets.get("gcp_service_account", None)

        if not credentials_dict:
            st.error("⚠️ Google Cloud 서비스 계정이 설정되지 않았습니다.")
            st.info("""
            **설정 방법:**
            1. Streamlit Cloud 대시보드에서 앱 설정 열기
            2. 'Secrets' 탭 클릭
            3. 아래 형식으로 서비스 계정 키 추가:
            ```toml
            [gcp_service_account]
            type = "service_account"
            project_id = "your-project-id"
            private_key_id = "your-key-id"
            private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
            client_email = "your-service-account@project.iam.gserviceaccount.com"
            client_id = "your-client-id"
            auth_uri = "https://accounts.google.com/o/oauth2/auth"
            token_uri = "https://oauth2.googleapis.com/token"
            auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
            client_x509_cert_url = "your-cert-url"
            ```
            """)
            return None

        # 서비스 계정 인증
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        # Drive API 서비스 생성
        service = build('drive', 'v3', credentials=credentials)
        return service

    except Exception as e:
        st.error(f"❌ Google Drive 연결 실패: {str(e)}")
        return None

def list_csv_files_in_drive(service, folder_id: str = None) -> List[Dict]:
    """Google Drive에서 모든 CSV 파일 목록 가져오기"""
    if not service:
        return []

    try:
        # 폴더 ID가 제공되면 해당 폴더에서만 검색
        if folder_id:
            query = f"'{folder_id}' in parents and mimeType='text/csv' and name contains 'QIP_incentive'"
        else:
            query = "mimeType='text/csv' and name contains 'QIP_incentive'"

        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, size)",
            orderBy='modifiedTime desc'
        ).execute()

        files = results.get('files', [])

        # 파일 정보 파싱
        parsed_files = []
        for file in files:
            # 파일명에서 월과 연도 추출
            match = re.search(r'output_QIP_incentive_(\w+)_(\d{4})', file['name'])
            if match:
                month_name = match.group(1)
                year = match.group(2)
                parsed_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'month': month_name,
                    'year': int(year),
                    'modified': file['modifiedTime'],
                    'size': file.get('size', 0),
                    'display_name': f"{year}년 {month_name.capitalize()}"
                })

        return parsed_files

    except Exception as e:
        st.error(f"파일 목록 가져오기 실패: {str(e)}")
        return []

@st.cache_data(ttl=300)  # 5분 캐시
def download_csv_from_drive(_service, file_id: str, file_name: str) -> pd.DataFrame:
    """Google Drive에서 CSV 파일 다운로드 및 DataFrame으로 변환"""
    if not _service:
        return pd.DataFrame()

    try:
        # 파일 다운로드
        request = _service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # DataFrame으로 변환
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, encoding='utf-8-sig')

        # 숫자 컬럼 변환
        numeric_cols = ['Continuous_Months', 'Previous_Incentive', 'Final_Incentive']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    except Exception as e:
        st.error(f"파일 다운로드 실패: {str(e)}")
        return pd.DataFrame()

def create_metrics_row(df: pd.DataFrame, lang: str = 'ko'):
    """메트릭 행 생성"""
    if df.empty:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            get_text('total_employees', lang),
            f"{len(df):,}"
        )

    with col2:
        received = len(df[df['Final_Incentive'] > 0])
        percentage = (received / len(df) * 100) if len(df) > 0 else 0
        st.metric(
            get_text('received_incentive', lang),
            f"{received:,}",
            f"{percentage:.1f}%"
        )

    with col3:
        total = df['Final_Incentive'].sum()
        st.metric(
            get_text('total_incentive', lang),
            f"₫{total:,.0f}"
        )

    with col4:
        avg = df['Final_Incentive'].mean()
        st.metric(
            get_text('average_incentive', lang),
            f"₫{avg:,.0f}"
        )

def create_charts(df: pd.DataFrame, lang: str = 'ko'):
    """차트 생성"""
    if df.empty:
        return

    colors = ['#667eea', '#764ba2', '#f093fb', '#fda085', '#84fab0']

    col1, col2 = st.columns(2)

    with col1:
        # TYPE별 분포
        st.subheader("TYPE별 직원 분포")
        type_counts = df['TYPE'].value_counts()
        fig_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            color_discrete_sequence=colors,
            hole=0.3
        )
        fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 인센티브 분포
        st.subheader("인센티브 금액 분포")
        df_with_incentive = df[df['Final_Incentive'] > 0]
        if not df_with_incentive.empty:
            fig_hist = px.histogram(
                df_with_incentive,
                x='Final_Incentive',
                nbins=20,
                color_discrete_sequence=[colors[0]]
            )
            fig_hist.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title="인센티브 (₫)",
                yaxis_title="직원 수"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

def main():
    """메인 함수"""

    # Google Drive 서비스 초기화
    if not st.session_state.drive_service:
        with st.spinner("Google Drive 연결 중..."):
            st.session_state.drive_service = init_google_drive_service()

    # 사이드바
    with st.sidebar:
        st.title("☁️ Google Drive 동기화")

        # 언어 선택
        lang_options = {'한국어': 'ko', 'English': 'en', 'Tiếng Việt': 'vi'}
        selected_lang = st.selectbox("🌐 언어", list(lang_options.keys()))
        lang = lang_options[selected_lang]

        st.markdown("---")

        # Google Drive 상태
        if st.session_state.drive_service:
            st.success("✅ Google Drive 연결됨")

            # 폴더 ID 입력 (선택사항)
            folder_id = st.text_input(
                "📁 Drive 폴더 ID (선택)",
                value=st.secrets.get("drive_folder_id", ""),
                help="특정 폴더의 파일만 보려면 폴더 ID를 입력하세요"
            )

            # 새로고침 버튼
            if st.button(f"🔄 {get_text('refresh', lang)}", use_container_width=True):
                st.session_state.available_files = []
                st.cache_data.clear()
                st.rerun()

            # 자동 새로고침
            auto_refresh = st.checkbox("자동 새로고침 (30초)", value=False)
            if auto_refresh:
                time.sleep(30)
                st.rerun()

        else:
            st.error("❌ Google Drive 미연결")
            st.info("""
            **연결 방법:**
            1. 앱 Settings 열기
            2. Secrets 탭에서 서비스 계정 추가
            3. 앱 재시작
            """)

        st.markdown("---")

        # 파일 목록 가져오기
        if st.session_state.drive_service:
            if not st.session_state.available_files:
                with st.spinner("파일 목록 로딩..."):
                    st.session_state.available_files = list_csv_files_in_drive(
                        st.session_state.drive_service,
                        folder_id if folder_id else None
                    )
                    st.session_state.last_refresh = datetime.now()

            # 사용 가능한 월 표시
            if st.session_state.available_files:
                st.info(f"📊 {len(st.session_state.available_files)}개 파일 발견")

                # 월 선택
                file_options = {
                    f"{f['year']}년 {f['month'].capitalize()}": f
                    for f in st.session_state.available_files
                }

                if file_options:
                    selected_month = st.selectbox(
                        get_text('select_month', lang),
                        list(file_options.keys())
                    )
                    selected_file = file_options[selected_month]
                else:
                    selected_file = None
            else:
                st.warning("CSV 파일을 찾을 수 없습니다")
                selected_file = None

        # 마지막 업데이트 시간
        if st.session_state.last_refresh:
            st.caption(
                f"{get_text('last_updated', lang)}: "
                f"{st.session_state.last_refresh.strftime('%H:%M:%S')}"
            )

    # 메인 컨텐츠
    st.title(f"☁️ {get_text('title', lang)}")
    st.caption(get_text('subtitle', lang))

    # 데이터 로드 및 표시
    if st.session_state.drive_service and selected_file:
        # 캐시 키
        cache_key = f"{selected_file['id']}_{selected_file['modified']}"

        # 데이터 로드
        if cache_key not in st.session_state.cached_data:
            with st.spinner(f"{get_text('loading', lang)}..."):
                df = download_csv_from_drive(
                    st.session_state.drive_service,
                    selected_file['id'],
                    selected_file['name']
                )
                st.session_state.cached_data[cache_key] = df
        else:
            df = st.session_state.cached_data[cache_key]

        if not df.empty:
            # 선택된 파일 정보
            st.info(f"📄 {selected_file['name']} ({selected_file['size']:,} bytes)")

            # 탭 생성
            tab1, tab2, tab3 = st.tabs([
                f"📈 {get_text('dashboard', lang)}",
                f"🔍 {get_text('employee_search', lang)}",
                f"📊 {get_text('detailed_analysis', lang)}"
            ])

            with tab1:
                # 메트릭
                create_metrics_row(df, lang)
                st.markdown("---")

                # 차트
                create_charts(df, lang)

            with tab2:
                # 직원 검색
                st.subheader(get_text('employee_search', lang))

                col1, col2 = st.columns([1, 3])
                with col1:
                    search_type = st.selectbox(
                        "검색 방식",
                        ["이름", "ID", "부서"]
                    )

                with col2:
                    if search_type == "이름":
                        search_value = st.text_input("직원 이름")
                        if search_value:
                            mask = df['Name'].str.contains(search_value, case=False, na=False)
                            filtered = df[mask]
                    elif search_type == "ID":
                        search_value = st.text_input("직원 ID")
                        if search_value:
                            mask = df['ID'].astype(str).str.contains(search_value, na=False)
                            filtered = df[mask]
                    else:
                        sections = df['Section'].unique()
                        search_value = st.selectbox("부서 선택", sections)
                        filtered = df[df['Section'] == search_value]

                if 'filtered' in locals() and not filtered.empty:
                    display_cols = ['ID', 'Name', 'Position', 'Section', 'TYPE',
                                  'Continuous_Months', 'Final_Incentive']
                    st.dataframe(
                        filtered[display_cols].style.format({
                            'Final_Incentive': '₫{:,.0f}',
                            'Continuous_Months': '{:.0f}'
                        }),
                        use_container_width=True
                    )

                    # 다운로드 버튼
                    csv = filtered.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name=f"employee_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with tab3:
                # 상세 분석
                st.subheader(get_text('detailed_analysis', lang))

                # Position별 통계
                st.write("### 직급별 통계")
                position_stats = df.groupby('Position').agg({
                    'ID': 'count',
                    'Final_Incentive': ['mean', 'sum', 'std']
                }).round(0)
                position_stats.columns = ['인원수', '평균 인센티브', '총 인센티브', '표준편차']
                st.dataframe(position_stats.sort_values('총 인센티브', ascending=False))

                # TYPE별 통계
                st.write("### TYPE별 통계")
                type_stats = df.groupby('TYPE').agg({
                    'ID': 'count',
                    'Final_Incentive': ['mean', 'sum'],
                    'Continuous_Months': 'mean'
                }).round(0)
                type_stats.columns = ['인원수', '평균 인센티브', '총 인센티브', '평균 연속 개월']
                st.dataframe(type_stats)

                # 조건 달성률
                st.write("### 조건별 달성률")
                condition_cols = [col for col in df.columns if col.startswith('Condition_')]
                if condition_cols:
                    condition_stats = []
                    for col in condition_cols:
                        yes_count = (df[col] == 'YES').sum()
                        percentage = (yes_count / len(df) * 100)
                        condition_stats.append({
                            'Condition': col.replace('_', ' '),
                            'YES': yes_count,
                            'NO': len(df) - yes_count,
                            'Rate': f"{percentage:.1f}%"
                        })

                    stats_df = pd.DataFrame(condition_stats)
                    fig = px.bar(
                        stats_df,
                        x='Condition',
                        y='YES',
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
            st.warning(get_text('no_data', lang))

    elif not st.session_state.drive_service:
        # Google Drive 설정 안내
        st.error("⚠️ Google Drive가 연결되지 않았습니다")

        with st.expander("🔧 설정 방법 보기"):
            st.markdown("""
            ### Google Drive 연동 설정 방법:

            1. **Google Cloud Console에서 서비스 계정 생성**
               - [console.cloud.google.com](https://console.cloud.google.com) 접속
               - 새 프로젝트 생성 또는 기존 프로젝트 선택
               - APIs & Services → Credentials
               - Create Credentials → Service Account

            2. **Google Drive API 활성화**
               - APIs & Services → Library
               - "Google Drive API" 검색
               - Enable 클릭

            3. **서비스 계정 키 생성**
               - Service Account 상세 페이지
               - Keys 탭 → Add Key → JSON
               - JSON 파일 다운로드

            4. **Streamlit Secrets 설정**
               - Streamlit Cloud 대시보드
               - 앱 Settings → Secrets
               - JSON 내용을 TOML 형식으로 변환하여 추가

            5. **Google Drive 폴더 공유**
               - CSV 파일이 있는 Drive 폴더
               - 서비스 계정 이메일과 공유 (Viewer 권한)
            """)

if __name__ == "__main__":
    main()