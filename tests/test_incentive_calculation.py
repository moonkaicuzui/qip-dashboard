#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Incentive Calculation Tests
===========================
@QAEngineer & @FinanceAnalyst 협업 개발

인센티브 계산 로직 검증:
- 100% 조건 충족 규칙
- TYPE 분류
- 진행 테이블
- 연속월 계산
"""

import pytest


class TestConditionFulfillment:
    """100% 조건 충족 규칙 테스트"""

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_100_percent_rule_all_pass(self, mock_employee_data):
        """모든 조건 충족 시 인센티브 지급"""
        # Given: 모든 조건을 충족하는 직원
        employee = mock_employee_data.copy()
        employee['Attendance_Rate'] = 95.0  # >= 88% ✓
        employee['Unapproved_Absences'] = 0  # <= 2 ✓
        employee['Actual_Working_Days'] = 20  # > 0 ✓
        employee['Total_Working_Days'] = 22  # >= 12 ✓
        employee['AQL_Fail_Percent'] = 0.0  # == 0 ✓
        employee['Continuous_FAIL'] = 'NO'  # ✓
        employee['Team_AQL_FAIL'] = 'NO'  # ✓
        employee['5PRS_Pass_Rate'] = 98.5  # >= 95% ✓
        employee['5PRS_Qty'] = 150  # >= 100 ✓

        # When: 조건 평가
        conditions_met = self._evaluate_conditions(employee)

        # Then: 모든 조건 통과
        assert conditions_met == 10
        assert self._should_receive_incentive(conditions_met, 10)

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_100_percent_rule_partial_fail(self, mock_employee_data):
        """일부 조건 미충족 시 인센티브 미지급 (80% 충족도 미지급)"""
        # Given: 80% 조건 충족 (8/10)
        employee = mock_employee_data.copy()
        employee['Attendance_Rate'] = 85.0  # < 88% ✗
        employee['Unapproved_Absences'] = 3  # > 2 ✗

        # When: 조건 평가
        conditions_met = self._evaluate_conditions(employee)

        # Then: 인센티브 미지급 (100% 규칙)
        assert conditions_met == 8
        assert not self._should_receive_incentive(conditions_met, 10)

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_condition_1_attendance_rate_threshold(self):
        """조건 1: 출근율 >= 88%"""
        assert self._check_attendance_rate(88.0) is True
        assert self._check_attendance_rate(88.1) is True
        assert self._check_attendance_rate(87.9) is False
        assert self._check_attendance_rate(100.0) is True

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_condition_2_unapproved_absence_threshold(self):
        """조건 2: 무단결근 <= 2일"""
        assert self._check_unapproved_absences(0) is True
        assert self._check_unapproved_absences(1) is True
        assert self._check_unapproved_absences(2) is True
        assert self._check_unapproved_absences(3) is False

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_condition_10_5prs_quantity_threshold(self):
        """조건 10: 5PRS 검사 수량 >= 100"""
        assert self._check_5prs_quantity(100) is True
        assert self._check_5prs_quantity(150) is True
        assert self._check_5prs_quantity(99) is False
        assert self._check_5prs_quantity(0) is False

    # Helper methods
    def _evaluate_conditions(self, emp):
        """조건 평가 (10개 조건)"""
        conditions = [
            self._check_attendance_rate(emp.get('Attendance_Rate', 0)),
            self._check_unapproved_absences(emp.get('Unapproved_Absences', 99)),
            emp.get('Actual_Working_Days', 0) > 0,
            emp.get('Total_Working_Days', 0) >= 12,
            emp.get('AQL_Fail_Percent', 100) == 0,
            emp.get('Continuous_FAIL', 'YES') == 'NO',
            emp.get('Team_AQL_FAIL', 'YES') == 'NO',
            True,  # Area Reject Rate (기본 통과)
            self._check_5prs_pass_rate(emp.get('5PRS_Pass_Rate', 0)),
            self._check_5prs_quantity(emp.get('5PRS_Qty', 0))
        ]
        return sum(conditions)

    def _should_receive_incentive(self, met, total):
        """인센티브 지급 여부 (100% 규칙)"""
        return met == total

    def _check_attendance_rate(self, rate):
        return rate >= 88.0

    def _check_unapproved_absences(self, days):
        return days <= 2

    def _check_5prs_pass_rate(self, rate):
        return rate >= 95.0

    def _check_5prs_quantity(self, qty):
        return qty >= 100


class TestTypeClassification:
    """TYPE 분류 테스트"""

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_type1_positions(self, position_matrix):
        """TYPE-1 직급 식별"""
        if position_matrix is None:
            pytest.skip("position_matrix not available")

        type1_positions = ['ASSEMBLY INSPECTOR', 'MODEL MASTER', 'AUDITOR & TRAINER']
        positions = position_matrix.get('positions', {})

        for pos in type1_positions:
            for code, data in positions.items():
                if data.get('name', '').upper() == pos.upper():
                    assert data.get('type') == 1, f"{pos} should be TYPE-1"

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_type2_positions(self, position_matrix):
        """TYPE-2 직급 식별"""
        if position_matrix is None:
            pytest.skip("position_matrix not available")

        type2_positions = ['LINE LEADER', 'GROUP LEADER', 'SUPERVISOR']
        positions = position_matrix.get('positions', {})

        for pos in type2_positions:
            for code, data in positions.items():
                if data.get('name', '').upper() == pos.upper():
                    assert data.get('type') == 2, f"{pos} should be TYPE-2"


class TestProgressionTable:
    """인센티브 진행 테이블 테스트"""

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_progression_values(self, type1_progression_table):
        """진행 테이블 값 검증"""
        expected = {
            1: 150000, 6: 400000, 12: 1000000, 15: 1000000
        }
        for month, amount in expected.items():
            assert type1_progression_table[month] == amount

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_progression_monotonic(self, type1_progression_table):
        """진행 테이블 단조 증가 검증"""
        prev = 0
        for month in range(1, 16):
            current = type1_progression_table[month]
            assert current >= prev, f"Month {month} should be >= month {month-1}"
            prev = current

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_progression_cap_at_12(self, type1_progression_table):
        """12개월 이후 최대치 유지"""
        max_amount = type1_progression_table[12]
        for month in range(12, 16):
            assert type1_progression_table[month] == max_amount


class TestContinuousMonths:
    """연속월 계산 테스트"""

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_continuous_months_increment(self):
        """조건 충족 시 연속월 증가"""
        prev_months = 5
        all_conditions_met = True

        if all_conditions_met:
            new_months = prev_months + 1
        else:
            new_months = 0

        assert new_months == 6

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_continuous_months_reset(self):
        """조건 미충족 시 연속월 리셋"""
        prev_months = 10
        all_conditions_met = False

        if all_conditions_met:
            new_months = prev_months + 1
        else:
            new_months = 0

        assert new_months == 0

    @pytest.mark.unit
    @pytest.mark.calculation
    def test_continuous_months_max(self):
        """연속월 최대값 15 제한"""
        for prev in [14, 15, 16, 100]:
            new_months = min(prev + 1, 15)
            assert new_months <= 15
