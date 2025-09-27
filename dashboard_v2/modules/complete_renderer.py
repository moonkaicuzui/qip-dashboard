#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard V2 - Complete Template Renderer
Version 5와 100% 동일한 HTML 렌더링
"""

import json
import os
import numpy as np
from pathlib import Path
from datetime import datetime
from .incentive_calculator import IncentiveCalculator


class CompleteRenderer:
    """Version 5와 완전히 동일한 HTML 렌더러"""

    def __init__(self):
        self.template_path = Path(__file__).parent.parent / 'templates' / 'complete.html'
        self.css_path = Path(__file__).parent.parent / 'static' / 'css' / 'complete_dashboard.css'
        self.js_path = Path(__file__).parent.parent / 'static' / 'js' / 'dashboard_complete.js'

    def _convert_nan_to_js(self, obj):
        """Convert pandas/numpy NaN to JavaScript-compatible NaN string"""
        if isinstance(obj, dict):
            return {k: self._convert_nan_to_js(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_nan_to_js(item) for item in obj]
        elif isinstance(obj, float) and (np.isnan(obj) if not isinstance(obj, bool) else False):
            return "NaN"  # Will be converted to actual NaN in JavaScript
        else:
            return obj

    def render_complete_dashboard(self, month, year):
        """Version 5와 완전히 동일한 대시보드 생성"""

        # 데이터 처리
        calculator = IncentiveCalculator(month, year)
        data = calculator.process_all_data()

        # 현재 시간
        now = datetime.now()
        generation_day = now.day
        is_final_report = generation_day >= 25
        month_num = calculator.month_num

        # CSS 로드
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # JavaScript 로드
        with open(self.js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # JSON 데이터 준비 (NaN 값을 JavaScript용으로 변환)
        # employees를 배열로 확인 (이미 list 형태)
        employees_data = self._convert_nan_to_js(data['employees']) if isinstance(data['employees'], list) else []
        translations_data = self._convert_nan_to_js(data['translations'])
        condition_matrix_data = self._convert_nan_to_js(data.get('condition_matrix', {}))
        excel_data = self._convert_nan_to_js(data.get('excel_dashboard_data', {}))

        # JSON 문자열로 변환
        employees_json = json.dumps(employees_data, ensure_ascii=False)
        translations_json = json.dumps(translations_data, ensure_ascii=False)
        condition_matrix_json = json.dumps(condition_matrix_data, ensure_ascii=False)
        excel_data_json = json.dumps(excel_data, ensure_ascii=False)

        # NaN 문자열을 실제 JavaScript NaN으로 변환
        employees_json = employees_json.replace('"NaN"', 'NaN')
        excel_data_json = excel_data_json.replace('"NaN"', 'NaN')

        # HTML 생성 (Version 5와 완전히 동일한 구조)
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QIP 인센티브 계산 결과 - {year}년 {month_num}월</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <!-- Dashboard Selector -->
            <div class="dashboard-selector">
                <select class="form-select form-select-sm" style="width: 200px;" id="dashboardSelector">
                    <option value="incentive">💰 Incentive Dashboard</option>
                    <option value="management">📊 Management Dashboard</option>
                    <option value="statistics">📈 Statistics Dashboard</option>
                </select>
            </div>
            <!-- Language Selector -->
            <div class="language-selector">
                <select class="form-select form-select-sm" id="languageSelect" onchange="changeLanguage(this.value)">
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                    <option value="vi">Tiếng Việt</option>
                </select>
            </div>

            <h1 id="mainTitle">QIP 인센티브 계산 결과 <span class="version-badge">v6.01</span></h1>
            <p id="mainSubtitle" data-year="{year}" data-month="{month_num}">{year}년 {month_num}월 인센티브 지급 현황</p>
            <p id="generationDate" style="color: white; font-size: 0.9em; margin-top: 10px; opacity: 0.9;"
               data-year="{now.year}" data-month="{now.month}" data-day="{now.day}"
               data-hour="{now.hour}" data-minute="{now.minute:02d}">
                보고서 생성일: {now.strftime('%Y년 %m월 %d일 %H:%M')}
            </p>
            <div id="dataPeriodSection" style="color: white; font-size: 0.85em; margin-top: 15px; opacity: 0.85; line-height: 1.6;">
                <p id="dataPeriodTitle" style="margin: 5px 0; font-weight: bold;">📊 사용 데이터 기간:</p>
                <p id="dataPeriodIncentive" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 인센티브 데이터: {year}년 {month_num:02d}월 01일 ~ 30일</p>
                <p id="dataPeriodAttendance" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 출근 데이터: {year}년 {month_num:02d}월 01일 ~ 23일</p>
                <p id="dataPeriodAQL" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• AQL 데이터: {year}년 {month_num:02d}월 01일 ~ 30일</p>
                <p id="dataPeriod5PRS" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 5PRS 데이터: {year}년 {month_num:02d}월 03일 ~ 23일</p>
                <p id="dataPeriodBasic" style="margin: 3px 0; padding-left: 20px;" data-year="{year}" data-month="{month_num:02d}">• 기본 인력 데이터: {year}년 {month_num:02d}월 기준</p>
            </div>
        </div>

        <!-- Report Type Banner -->
        <div class="report-type-banner">
            <div style="display: flex; align-items: center;">
                <span class="icon">{"✅" if is_final_report else "⚠️"}</span>
                <div class="message">
                    <div class="title">{"최종 보고서" if is_final_report else "중간 점검용 리포트"}</div>
                    <div class="description">
                        {"이 보고서는 월말 최종 보고서입니다. 모든 인센티브 조건이 정상적으로 적용됩니다." if is_final_report else "이 리포트는 중간 점검용입니다. 일부 조건이 아직 확정되지 않았을 수 있습니다."}
                    </div>
                </div>
            </div>
            <div>
                <span style="font-size: 0.85rem; opacity: 0.9;">생성일: {generation_day}일</span>
            </div>
        </div>

        <div class="content p-4">
            <!-- Summary Cards -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalEmployeesLabel">전체 직원</h6>
                        <h2 id="totalEmployeesValue">{data['stats']['totalEmployees']}<span class="unit" id="totalEmployeesUnit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paidEmployeesLabel">수령 직원</h6>
                        <h2 id="paidEmployeesValue">{data['stats']['paidEmployees']}<span class="unit" id="paidEmployeesUnit">명</span></h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="paymentRateLabel">지급률</h6>
                        <h2 id="paymentRateValue">{data['stats']['paymentRate']}%</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-card">
                        <h6 class="text-muted" id="totalAmountLabel">총 지급액</h6>
                        <h2 id="totalAmountValue">{data['stats']['totalAmount']:,} VND</h2>
                    </div>
                </div>
            </div>

            <!-- Tab Menu -->
            <div class="tabs">
                <div class="tab active" data-tab="summary" onclick="showTab('summary')" id="tabSummary">요약</div>
                <div class="tab" data-tab="position" onclick="showTab('position')" id="tabPosition">직급별 상세</div>
                <div class="tab" data-tab="detail" onclick="showTab('detail')" id="tabIndividual">개인별 상세</div>
                <div class="tab" data-tab="criteria" onclick="showTab('criteria')" id="tabCriteria">인센티브 기준</div>
                <div class="tab" data-tab="orgchart" onclick="showTab('orgchart')" id="tabOrgChart">조직도</div>
                <div class="tab" data-tab="validation" onclick="showTab('validation')" id="tabValidation">요약 및 시스템 검증</div>
            </div>

            <!-- Tab Content -->
            <div id="summary" class="tab-content active">
                <h3 id="summaryTabTitle">Type별 요약</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th rowspan="2" id="summaryTypeHeader">Type</th>
                            <th rowspan="2" id="summaryTotalHeader">전체 인원</th>
                            <th rowspan="2" id="summaryEligibleHeader">지급 대상</th>
                            <th rowspan="2" id="summaryPaymentRateHeader">지급률</th>
                            <th rowspan="2" id="summaryTotalAmountHeader">총 지급액</th>
                            <th colspan="2" class="avg-header" id="summaryAvgAmountHeader">평균 지급액</th>
                        </tr>
                        <tr>
                            <th class="sub-header" id="summaryAvgEligibleHeader">수령인원 기준</th>
                            <th class="sub-header" id="summaryAvgTotalHeader">총원 기준</th>
                        </tr>
                    </thead>
                    <tbody id="typeSummaryBody">
                        <!-- JavaScript로 동적으로 채워질 예정 -->
                    </tbody>
                </table>
            </div>

            <div id="position" class="tab-content">
                <h3 id="positionTabTitle">직급별 인센티브 현황</h3>
                <div id="positionContent">
                    <!-- JavaScript로 동적으로 채워질 예정 -->
                </div>
            </div>

            <div id="detail" class="tab-content">
                <h3 id="detailTabTitle">개인별 상세</h3>
                <div class="filter-section mb-3">
                    <div class="row">
                        <div class="col-md-4">
                            <input type="text" class="form-control" id="searchInput" placeholder="이름 또는 사번으로 검색...">
                        </div>
                        <div class="col-md-2">
                            <select class="form-select" id="typeFilter">
                                <option value="">전체 TYPE</option>
                                <option value="TYPE-1">TYPE-1</option>
                                <option value="TYPE-2">TYPE-2</option>
                                <option value="TYPE-3">TYPE-3</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <select class="form-select" id="paymentFilter">
                                <option value="">전체</option>
                                <option value="paid">수령자만</option>
                                <option value="unpaid">미수령자만</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div id="detailTable">
                    <!-- JavaScript로 동적으로 채워질 예정 -->
                </div>
            </div>

            <div id="criteria" class="tab-content">
                <h3 id="criteriaTabTitle">인센티브 지급 기준</h3>
                <div id="criteriaContent">
                    <!-- JavaScript로 동적으로 채워질 예정 -->
                </div>
            </div>

            <div id="orgchart" class="tab-content">
                <h3 id="orgChartTabTitle">조직도</h3>
                <div id="orgChartContent">
                    <!-- JavaScript로 동적으로 채워질 예정 -->
                </div>
            </div>

            <div id="validation" class="tab-content">
                <h3 id="validationTabTitle">시스템 검증</h3>
                <div id="validationContent">
                    <!-- JavaScript로 동적으로 채워질 예정 -->
                </div>
            </div>
        </div>
    </div>

    <!-- Modals Container -->
    <div id="modalsContainer"></div>

    <script>
        // Global data variables
        window.employeeData = {employees_json};
        const employeeData = window.employeeData;
        const translations = {translations_json};
        const positionMatrix = {condition_matrix_json};
        window.excelDashboardData = {excel_data_json};
        const excelDashboardData = window.excelDashboardData;

        let currentLanguage = 'ko';
        const dashboardMonth = '{month}';
        const dashboardYear = {year};

        // Dashboard Data for compatibility
        window.dashboardData = {{
            employees: {employees_json},
            stats: {json.dumps(data['stats'], ensure_ascii=False)},
            config: {{
                month: "{month}",
                year: {year},
                workingDays: {data['config']['workingDays']},
                currentLang: 'ko'
            }}
        }};

{js_content}
    </script>
</body>
</html>"""

        return html

    def save_dashboard(self, month, year, output_path=None):
        """대시보드를 파일로 저장"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / 'output_files' / f'Dashboard_V6_Complete_{year}_{month}.html'

        html = self.render_complete_dashboard(month, year)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        file_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"✅ Complete dashboard saved to: {output_path}")
        print(f"📊 File size: {file_size:.2f} MB")

        return output_path


def main():
    """테스트용 메인 함수"""
    renderer = CompleteRenderer()
    renderer.save_dashboard('september', 2025)


if __name__ == "__main__":
    main()