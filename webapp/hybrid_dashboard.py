#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QIP 인센티브 대시보드 - Hybrid 버전
Streamlit으로 데이터 처리 + HTML 모달 포함 대시보드 생성
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import base64
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="QIP 대시보드 Hybrid",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 QIP 인센티브 대시보드 - Hybrid 버전")
st.caption("Streamlit 데이터 처리 + Full HTML 대시보드 생성")

# 사이드바
with st.sidebar:
    st.header("설정")

    # 데이터 소스 선택
    data_source = st.radio(
        "데이터 소스",
        ["로컬 CSV", "Google Drive"]
    )

    # 월/연도 선택
    year = st.selectbox("연도", [2024, 2025, 2026], index=1)
    month = st.selectbox("월", range(1, 13), index=10)

    st.markdown("---")

    # 기능 선택
    st.subheader("대시보드 기능")
    include_modals = st.checkbox("모달 팝업 포함", value=True)
    include_animations = st.checkbox("애니메이션 효과", value=True)
    mobile_optimized = st.checkbox("모바일 최적화", value=True)

# 메인 컨텐츠
tab1, tab2, tab3 = st.tabs(["📊 Streamlit 대시보드", "🌐 HTML 생성", "📱 모바일 뷰"])

with tab1:
    st.header("Streamlit 기본 대시보드")

    # Streamlit으로 가능한 기능들
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 직원", "535", "+12")
    with col2:
        st.metric("인센티브 수령", "234", "43.7%")
    with col3:
        st.metric("총 인센티브", "₫123,456,789")
    with col4:
        st.metric("평균", "₫527,619")

    # Expandable sections (모달 대체)
    with st.expander("👤 직원 상세 정보", expanded=False):
        st.write("여기서 직원 정보를 볼 수 있습니다.")
        # 직원 테이블
        df_sample = pd.DataFrame({
            'ID': ['001', '002', '003'],
            'Name': ['Kim', 'Lee', 'Park'],
            'Incentive': [500000, 600000, 450000]
        })
        st.dataframe(df_sample)

    with st.expander("📈 조건별 분석", expanded=False):
        st.write("10가지 조건 달성률")
        # Progress bars로 조건 표시
        for i in range(1, 6):
            st.progress(np.random.random(), f"조건 {i}")

with tab2:
    st.header("🌐 Full HTML 대시보드 생성")

    def generate_full_html_dashboard(data, include_modals=True, include_animations=True):
        """완전한 HTML 대시보드 생성 (모달 포함)"""

        html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 대시보드</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .modal-content {
            border-radius: 15px;
        }

        .btn-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            transition: all 0.3s;
        }

        .btn-gradient:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        @media (max-width: 768px) {
            .dashboard-container {
                padding: 10px;
            }

            .metric-card {
                margin-bottom: 15px;
            }
        }

        /* 애니메이션 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-in {
            animation: fadeIn 0.5s ease-out;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- 헤더 -->
        <div class="text-center text-white mb-5 animate-in">
            <h1 class="display-4 fw-bold">QIP 인센티브 대시보드</h1>
            <p class="lead">{year}년 {month}월 현황</p>
        </div>

        <!-- 메트릭 카드 -->
        <div class="row mb-4">
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="metric-card animate-in">
                    <h6 class="text-muted">총 직원</h6>
                    <h3 class="fw-bold">535</h3>
                    <small class="text-success">+12 from last month</small>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="metric-card animate-in" style="animation-delay: 0.1s">
                    <h6 class="text-muted">인센티브 수령</h6>
                    <h3 class="fw-bold">234</h3>
                    <small class="text-info">43.7%</small>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="metric-card animate-in" style="animation-delay: 0.2s">
                    <h6 class="text-muted">총 인센티브</h6>
                    <h3 class="fw-bold">₫123.5M</h3>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="metric-card animate-in" style="animation-delay: 0.3s">
                    <h6 class="text-muted">평균</h6>
                    <h3 class="fw-bold">₫527K</h3>
                </div>
            </div>
        </div>

        <!-- 차트 섹션 -->
        <div class="row mb-4">
            <div class="col-md-6 mb-3">
                <div class="metric-card animate-in">
                    <h5 class="mb-3">TYPE별 분포</h5>
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="metric-card animate-in">
                    <h5 class="mb-3">월별 트렌드</h5>
                    <canvas id="lineChart"></canvas>
                </div>
            </div>
        </div>

        <!-- 버튼 그룹 -->
        <div class="text-center mb-4">
            <button class="btn btn-gradient mx-2" data-bs-toggle="modal" data-bs-target="#employeeModal">
                👤 직원 상세
            </button>
            <button class="btn btn-gradient mx-2" data-bs-toggle="modal" data-bs-target="#conditionModal">
                📊 조건 분석
            </button>
            <button class="btn btn-gradient mx-2" data-bs-toggle="modal" data-bs-target="#settingsModal">
                ⚙️ 설정
            </button>
        </div>

        <!-- 직원 상세 모달 -->
        <div class="modal fade" id="employeeModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">직원 상세 정보</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="text" class="form-control mb-3" placeholder="직원 검색...">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>이름</th>
                                    <th>부서</th>
                                    <th>TYPE</th>
                                    <th>인센티브</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>001</td>
                                    <td>Kim</td>
                                    <td>QC</td>
                                    <td>TYPE-1</td>
                                    <td>₫500,000</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 조건 분석 모달 -->
        <div class="modal fade" id="conditionModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">10가지 조건 달성률</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <canvas id="conditionChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- 설정 모달 -->
        <div class="modal fade" id="settingsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">설정</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">언어 선택</label>
                            <select class="form-select">
                                <option>한국어</option>
                                <option>English</option>
                                <option>Tiếng Việt</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">테마</label>
                            <select class="form-select">
                                <option>라이트</option>
                                <option>다크</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // 차트 초기화
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: ['TYPE-1', 'TYPE-2', 'TYPE-3'],
                datasets: [{
                    data: [45, 30, 25],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb']
                }]
            }
        });

        const lineCtx = document.getElementById('lineChart').getContext('2d');
        new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                datasets: [{
                    label: '인센티브 총액',
                    data: [120, 132, 101, 134, 90, 130],
                    borderColor: '#667eea',
                    tension: 0.4
                }]
            }
        });
    </script>
</body>
</html>"""

        return html_template.format(year=year, month=month)

    # HTML 생성 옵션
    st.info("📝 아래 버튼을 클릭하면 모달과 애니메이션이 포함된 완전한 HTML 대시보드를 생성합니다.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎨 HTML 대시보드 생성", type="primary", use_container_width=True):
            html_content = generate_full_html_dashboard(
                None,
                include_modals=include_modals,
                include_animations=include_animations
            )

            # HTML 다운로드 버튼
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="dashboard_{year}_{month}.html">📥 HTML 파일 다운로드</a>'
            st.markdown(href, unsafe_allow_html=True)

            st.success("✅ HTML 대시보드가 생성되었습니다!")

    with col2:
        if st.button("👁️ 미리보기", use_container_width=True):
            html_content = generate_full_html_dashboard(None)
            # iframe으로 미리보기
            st.components.v1.html(html_content, height=600, scrolling=True)

with tab3:
    st.header("📱 모바일 최적화 뷰")

    st.info("""
    ### 모바일 접속 방법:

    1. **로컬 네트워크**: 같은 와이파이에서 접속
       - URL: `http://192.168.x.x:8501`

    2. **Streamlit Cloud**: 인터넷에서 접속
       - URL: `https://your-app.streamlit.app`

    3. **HTML 다운로드**: 오프라인에서도 사용 가능
       - 생성된 HTML 파일을 모바일로 전송
       - 브라우저에서 직접 열기
    """)

    # QR 코드 생성 (로컬 접속용)
    if st.button("📱 QR 코드 생성"):
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        url = f"http://{local_ip}:8501"

        st.code(url)
        st.info("위 주소를 모바일 브라우저에 입력하세요")

# 푸터
st.markdown("---")
st.caption("💡 Hybrid 방식: Streamlit의 데이터 처리 능력 + HTML의 완전한 UI 기능")