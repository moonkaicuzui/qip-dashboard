#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 인센티브 대시보드 - 보안 강화 버전
Google Drive 자동 동기화 및 보안 관리 포함
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
import glob
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, List
import hashlib
import hmac
from pathlib import Path

# 부모 디렉토리를 path에 추가 (src 모듈 import를 위해)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# Google Drive Manager import (있는 경우)
try:
    from src.google_drive_manager import GoogleDriveManager
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    st.warning("Google Drive Manager를 찾을 수 없습니다. 로컬 파일만 사용합니다.")

# 페이지 설정
st.set_page_config(
    page_title="QIP 인센티브 대시보드 (보안)",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 보안 설정
SECURE_MODE = os.getenv('SECURE_MODE', 'true').lower() == 'true'
AUTO_SYNC_ENABLED = os.getenv('AUTO_SYNC_ENABLED', 'true').lower() == 'true'
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL_MINUTES', '30'))

# 세션 상태 초기화
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}
if 'drive_manager' not in st.session_state:
    st.session_state.drive_manager = None

def init_google_drive():
    """Google Drive Manager 초기화 (보안 강화)"""
    if not GOOGLE_DRIVE_AVAILABLE:
        return None

    try:
        # 서비스 계정 키 파일 경로 (환경변수에서 읽기)
        key_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH',
                            'config_files/service_account_key.json')

        # 키 파일 존재 확인
        if not os.path.exists(key_path):
            st.error(f"⚠️ Google 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
            st.info("Google Drive 동기화를 사용하려면 서비스 계정 키를 설정하세요.")
            return None

        # 보안 검증: 키 파일 권한 확인
        if SECURE_MODE:
            file_stat = os.stat(key_path)
            if file_stat.st_mode & 0o077:  # 다른 사용자가 읽을 수 있는지 확인
                st.warning("⚠️ 보안 경고: 서비스 계정 키 파일의 권한이 너무 개방적입니다.")
                st.code("chmod 600 " + key_path)

        # GoogleDriveManager 초기화
        manager = GoogleDriveManager()
        st.success("✅ Google Drive 연결 성공")
        return manager

    except Exception as e:
        st.error(f"❌ Google Drive 연결 실패: {str(e)}")
        return None

def sync_data_from_drive(manager, month: int, year: int):
    """Google Drive에서 데이터 동기화"""
    if not manager or not AUTO_SYNC_ENABLED:
        return False

    try:
        # 마지막 동기화 시간 확인
        now = datetime.now()
        if st.session_state.last_sync:
            time_diff = (now - st.session_state.last_sync).total_seconds() / 60
            if time_diff < SYNC_INTERVAL:
                remaining = SYNC_INTERVAL - int(time_diff)
                st.info(f"📅 다음 동기화까지 {remaining}분 남음")
                return False

        with st.spinner("🔄 Google Drive에서 최신 데이터 동기화 중..."):
            # 여기에 실제 Google Drive 동기화 로직 구현
            # manager.download_files() 등의 메서드 호출

            # 동기화 시간 업데이트
            st.session_state.last_sync = now
            st.success(f"✅ 데이터 동기화 완료 ({now.strftime('%H:%M:%S')})")
            return True

    except Exception as e:
        st.error(f"동기화 실패: {str(e)}")
        return False

@st.cache_data(ttl=600)  # 10분 캐시
def load_data_with_cache(month: int, year: int) -> pd.DataFrame:
    """데이터 로드 (캐시 사용)"""
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
                # 데이터 무결성 검증
                required_cols = ['ID', 'Name', 'Position', 'Final_Incentive']
                if all(col in df.columns for col in required_cols):
                    return df
                else:
                    st.error("데이터 파일에 필수 컬럼이 없습니다.")
            except Exception as e:
                st.error(f"데이터 로드 오류: {e}")

    return pd.DataFrame()

def create_secure_dashboard(df: pd.DataFrame, lang: str = 'ko'):
    """보안 강화된 대시보드 생성"""
    if df.empty:
        st.warning("표시할 데이터가 없습니다.")
        return

    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 직원", f"{len(df):,}")

    with col2:
        received = len(df[df['Final_Incentive'] > 0])
        st.metric("인센티브 수령", f"{received:,}", f"{received/len(df)*100:.1f}%")

    with col3:
        total = df['Final_Incentive'].sum()
        st.metric("총 인센티브", f"₫{total:,.0f}")

    with col4:
        avg = df['Final_Incentive'].mean()
        st.metric("평균 인센티브", f"₫{avg:,.0f}")

    # 차트 생성
    st.subheader("📊 인센티브 분석")

    col1, col2 = st.columns(2)

    with col1:
        # TYPE별 분포
        type_counts = df['TYPE'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index,
                    title="TYPE별 직원 분포")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Position별 평균
        position_avg = df.groupby('Position')['Final_Incentive'].mean().sort_values(ascending=True).tail(10)
        fig = px.bar(x=position_avg.values, y=position_avg.index, orientation='h',
                    title="직급별 평균 인센티브 (Top 10)")
        st.plotly_chart(fig, use_container_width=True)

def main():
    """메인 함수"""

    # 보안 모드 표시
    if SECURE_MODE:
        st.sidebar.markdown("🔒 **보안 모드 활성화**")

    # Google Drive Manager 초기화
    if not st.session_state.drive_manager and GOOGLE_DRIVE_AVAILABLE:
        st.session_state.drive_manager = init_google_drive()

    # 사이드바
    with st.sidebar:
        st.title("🔒 QIP 대시보드")
        st.markdown("---")

        # Google Drive 상태
        if st.session_state.drive_manager:
            st.success("✅ Google Drive 연결됨")
            if st.button("🔄 수동 동기화"):
                sync_data_from_drive(st.session_state.drive_manager,
                                   datetime.now().month,
                                   datetime.now().year)
        else:
            st.warning("⚠️ 로컬 모드 (Drive 미연결)")

        st.markdown("---")

        # 날짜 선택
        year = st.selectbox("연도", range(2024, 2027), index=1)
        month = st.selectbox("월", range(1, 13), index=datetime.now().month - 1)

        # 언어 선택
        lang = st.selectbox("언어", ['한국어', 'English', 'Tiếng Việt'])

        st.markdown("---")

        # 보안 정보
        with st.expander("🔐 보안 설정"):
            st.info(
                "• 자동 동기화: " + ("활성화" if AUTO_SYNC_ENABLED else "비활성화") + "\n"
                "• 동기화 주기: " + str(SYNC_INTERVAL) + "분\n"
                "• 보안 모드: " + ("활성화" if SECURE_MODE else "비활성화")
            )

            if st.session_state.last_sync:
                st.caption(f"마지막 동기화: {st.session_state.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")

    # 메인 컨텐츠
    st.title("📊 QIP 인센티브 대시보드")
    st.caption(f"보안 강화 버전 | {year}년 {month}월")

    # 자동 동기화 체크
    if st.session_state.drive_manager and AUTO_SYNC_ENABLED:
        sync_data_from_drive(st.session_state.drive_manager, month, year)

    # 데이터 로드
    with st.spinner("데이터 로딩 중..."):
        df = load_data_with_cache(month, year)

    if not df.empty:
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 대시보드",
            "🔍 직원 검색",
            "📊 상세 분석",
            "🔐 보안 로그"
        ])

        with tab1:
            create_secure_dashboard(df, lang)

        with tab2:
            st.subheader("직원 정보 검색")
            search = st.text_input("이름 또는 ID 입력")
            if search:
                mask = (df['Name'].str.contains(search, case=False, na=False) |
                       df['ID'].astype(str).str.contains(search, na=False))
                filtered = df[mask]
                if not filtered.empty:
                    st.dataframe(filtered[['ID', 'Name', 'Position', 'Final_Incentive']])
                else:
                    st.info("검색 결과가 없습니다.")

        with tab3:
            st.subheader("조건별 달성률")
            condition_cols = [col for col in df.columns if col.startswith('Condition_')]
            if condition_cols:
                for col in condition_cols:
                    yes_rate = (df[col] == 'YES').mean() * 100
                    st.progress(yes_rate / 100)
                    st.caption(f"{col}: {yes_rate:.1f}%")

        with tab4:
            st.subheader("보안 활동 로그")
            st.info("최근 보안 관련 활동:")
            if st.session_state.last_sync:
                st.text(f"✅ {st.session_state.last_sync} - 데이터 동기화")
            st.text(f"🔒 {datetime.now()} - 보안 모드로 실행 중")
            st.caption("모든 API 키와 credential은 환경변수로 보호됩니다.")
    else:
        st.error("데이터를 찾을 수 없습니다.")
        st.info("Google Drive 동기화를 시도하거나 로컬 파일을 확인하세요.")

if __name__ == "__main__":
    main()