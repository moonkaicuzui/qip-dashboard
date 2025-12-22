#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Validation Tests
=====================
@QAEngineer & @DataAnalyst 협업 개발

데이터 검증 테스트:
- CSV 데이터 무결성
- 필수 컬럼 존재
- 값 범위 검증
- 데이터 일관성
"""

import pytest
import pandas as pd
from pathlib import Path


class TestDataIntegrity:
    """데이터 무결성 테스트"""

    @pytest.mark.integration
    @pytest.mark.validation
    def test_csv_has_required_columns(self, sample_csv_data):
        """필수 컬럼 존재 확인"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        # 실제 CSV 컬럼명 사용
        required_columns = [
            'Employee No', 'Full Name', 'Continuous_Months',
            'Total Working Days', 'Actual Working Days'
        ]

        for col in required_columns:
            assert col in sample_csv_data.columns or \
                   any(col.lower() in c.lower() for c in sample_csv_data.columns), \
                   f"Missing required column: {col}"

    @pytest.mark.integration
    @pytest.mark.validation
    def test_no_negative_incentives(self, sample_csv_data):
        """인센티브 음수 없음"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        incentive_cols = [c for c in sample_csv_data.columns if 'incentive' in c.lower()]
        for col in incentive_cols:
            values = sample_csv_data[col].dropna()
            assert (values >= 0).all(), f"Negative values in {col}"

    @pytest.mark.integration
    @pytest.mark.validation
    def test_type_values_valid(self, sample_csv_data):
        """TYPE 값 유효성 (1, 2, 3)"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        type_col = 'TYPE' if 'TYPE' in sample_csv_data.columns else None
        if type_col is None:
            pytest.skip("TYPE column not found")

        valid_types = {1, 2, 3}
        actual_types = set(sample_csv_data[type_col].dropna().astype(int).unique())
        assert actual_types.issubset(valid_types), \
            f"Invalid TYPE values: {actual_types - valid_types}"


class TestValueRanges:
    """값 범위 검증"""

    @pytest.mark.integration
    @pytest.mark.validation
    def test_attendance_rate_range(self, sample_csv_data):
        """출근율 0-100% 범위"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        rate_col = [c for c in sample_csv_data.columns if 'attendance' in c.lower() and 'rate' in c.lower()]
        if not rate_col:
            pytest.skip("Attendance rate column not found")

        values = sample_csv_data[rate_col[0]].dropna()
        assert (values >= 0).all() and (values <= 100).all(), \
            "Attendance rate out of range [0, 100]"

    @pytest.mark.integration
    @pytest.mark.validation
    def test_continuous_months_range(self, sample_csv_data):
        """연속월 0-15 범위"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        months_col = [c for c in sample_csv_data.columns if 'continuous' in c.lower() and 'month' in c.lower()]
        if not months_col:
            pytest.skip("Continuous months column not found")

        # 문자열을 숫자로 변환 (문자열 데이터 처리)
        import pandas as pd
        values = pd.to_numeric(sample_csv_data[months_col[0]], errors='coerce').dropna()
        assert (values >= 0).all() and (values <= 15).all(), \
            "Continuous months out of range [0, 15]"

    @pytest.mark.integration
    @pytest.mark.validation
    def test_5prs_pass_rate_range(self, sample_csv_data):
        """5PRS 합격률 0-100% 범위"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        rate_col = [c for c in sample_csv_data.columns if '5prs' in c.lower() and 'rate' in c.lower()]
        if not rate_col:
            pytest.skip("5PRS pass rate column not found")

        values = sample_csv_data[rate_col[0]].dropna()
        assert (values >= 0).all() and (values <= 100).all(), \
            "5PRS pass rate out of range [0, 100]"


class TestDataConsistency:
    """데이터 일관성 테스트"""

    @pytest.mark.integration
    @pytest.mark.validation
    def test_type3_zero_incentive(self, sample_csv_data):
        """TYPE-3는 항상 0 VND"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        if 'TYPE' not in sample_csv_data.columns:
            pytest.skip("TYPE column not found")

        incentive_cols = [c for c in sample_csv_data.columns
                         if 'incentive' in c.lower() and 'previous' not in c.lower()]

        type3_employees = sample_csv_data[sample_csv_data['TYPE'] == 3]

        for col in incentive_cols[:1]:  # 최신 인센티브 컬럼만
            values = type3_employees[col].dropna()
            assert (values == 0).all(), \
                f"TYPE-3 employees should have 0 incentive in {col}"

    @pytest.mark.integration
    @pytest.mark.validation
    def test_employee_no_unique(self, sample_csv_data):
        """직원 번호 고유성"""
        if sample_csv_data is None:
            pytest.skip("No CSV data available")

        emp_col = [c for c in sample_csv_data.columns if 'emp' in c.lower() and 'no' in c.lower()]
        if not emp_col:
            pytest.skip("Employee number column not found")

        emp_numbers = sample_csv_data[emp_col[0]].dropna()
        assert emp_numbers.is_unique, "Duplicate employee numbers found"


class TestPositionMatrix:
    """직급 매트릭스 검증"""

    @pytest.mark.unit
    @pytest.mark.validation
    def test_matrix_structure(self, position_matrix):
        """매트릭스 구조 검증"""
        if position_matrix is None:
            pytest.skip("Position matrix not available")

        # 실제 구조에 맞게 수정 (position_matrix 사용)
        required_keys = ['position_matrix', 'conditions', 'incentive_progression']
        for key in required_keys:
            assert key in position_matrix, f"Missing key: {key}"

    @pytest.mark.unit
    @pytest.mark.validation
    def test_conditions_defined(self, position_matrix):
        """10개 조건 정의 확인"""
        if position_matrix is None:
            pytest.skip("Position matrix not available")

        conditions = position_matrix.get('conditions', {})
        # 최소 10개 조건 정의
        assert len(conditions) >= 10, f"Expected 10 conditions, found {len(conditions)}"

    @pytest.mark.unit
    @pytest.mark.validation
    def test_progression_table_complete(self, position_matrix):
        """진행 테이블 완성도"""
        if position_matrix is None:
            pytest.skip("Position matrix not available")

        # 실제 구조: incentive_progression.TYPE_1_PROGRESSIVE.progression_table
        progression = position_matrix.get('incentive_progression', {})
        type1_prog = progression.get('TYPE_1_PROGRESSIVE', {})
        table = type1_prog.get('progression_table', {})

        # 1-12개월 모두 정의 (15개월까지는 12개월 값 유지)
        for month in range(1, 13):
            assert str(month) in table or month in table, \
                f"Month {month} missing from progression table"
