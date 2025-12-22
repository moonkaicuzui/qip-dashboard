#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anomaly Detection System
========================
@DataAnalyst & @QAEngineer 협업 개발

이상치 탐지 시스템:
- 통계적 이상치 탐지
- 비즈니스 규칙 위반 탐지
- 데이터 불일치 탐지
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AnomalyType(Enum):
    """이상치 유형"""
    STATISTICAL = "statistical"       # 통계적 이상치
    BUSINESS_RULE = "business_rule"   # 비즈니스 규칙 위반
    DATA_QUALITY = "data_quality"     # 데이터 품질 문제
    TREND = "trend"                   # 트렌드 이상


class Severity(Enum):
    """심각도"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Anomaly:
    """이상치 정보"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: Severity
    description: str
    affected_employee: Optional[str]
    affected_field: str
    expected_value: Optional[str]
    actual_value: str
    recommendation: str
    detected_at: str


class AnomalyDetector:
    """이상치 탐지기"""

    def __init__(self, output_dir: str = "output_files"):
        self.output_dir = Path(output_dir)
        self.anomalies: List[Anomaly] = []
        self.anomaly_counter = 0

    def _generate_anomaly_id(self) -> str:
        """이상치 ID 생성"""
        self.anomaly_counter += 1
        return f"ANM-{datetime.now().strftime('%Y%m%d')}-{self.anomaly_counter:04d}"

    def _add_anomaly(
        self,
        anomaly_type: AnomalyType,
        severity: Severity,
        description: str,
        field: str,
        actual: str,
        expected: Optional[str] = None,
        employee: Optional[str] = None,
        recommendation: str = ""
    ):
        """이상치 추가"""
        anomaly = Anomaly(
            anomaly_id=self._generate_anomaly_id(),
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            affected_employee=employee,
            affected_field=field,
            expected_value=expected,
            actual_value=actual,
            recommendation=recommendation,
            detected_at=datetime.now().isoformat()
        )
        self.anomalies.append(anomaly)
        return anomaly

    def detect_statistical_anomalies(self, df: pd.DataFrame, column: str) -> List[Anomaly]:
        """통계적 이상치 탐지 (IQR 방법)"""
        detected = []

        if column not in df.columns:
            return detected

        values = pd.to_numeric(df[column], errors='coerce').dropna()
        if len(values) < 10:
            return detected

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # 이상치 찾기
        outliers = df[(pd.to_numeric(df[column], errors='coerce') < lower_bound) |
                      (pd.to_numeric(df[column], errors='coerce') > upper_bound)]

        for idx, row in outliers.iterrows():
            emp_id = str(row.get('Employee No', row.get('emp_no', idx)))
            value = row[column]

            anomaly = self._add_anomaly(
                anomaly_type=AnomalyType.STATISTICAL,
                severity=Severity.MEDIUM,
                description=f"Statistical outlier detected in {column}",
                field=column,
                actual=str(value),
                expected=f"Range: {lower_bound:.0f} - {upper_bound:.0f}",
                employee=emp_id,
                recommendation="Review data accuracy and verify with source documents"
            )
            detected.append(anomaly)

        return detected

    def detect_business_rule_violations(self, df: pd.DataFrame) -> List[Anomaly]:
        """비즈니스 규칙 위반 탐지"""
        detected = []

        # 규칙 1: TYPE-3는 인센티브 0이어야 함
        type_col = 'TYPE' if 'TYPE' in df.columns else None
        incentive_col = None
        for col in df.columns:
            if 'final' in col.lower() and 'incentive' in col.lower():
                incentive_col = col
                break

        if type_col and incentive_col:
            type3_with_incentive = df[(df[type_col] == 3) &
                                      (pd.to_numeric(df[incentive_col], errors='coerce') > 0)]
            for idx, row in type3_with_incentive.iterrows():
                emp_id = str(row.get('Employee No', idx))
                anomaly = self._add_anomaly(
                    anomaly_type=AnomalyType.BUSINESS_RULE,
                    severity=Severity.CRITICAL,
                    description="TYPE-3 employee received incentive (should be 0)",
                    field=incentive_col,
                    actual=str(row[incentive_col]),
                    expected="0",
                    employee=emp_id,
                    recommendation="Investigate TYPE classification or reset incentive to 0"
                )
                detected.append(anomaly)

        # 규칙 2: 출근율 범위 검증 (0-100%)
        attendance_col = None
        for col in df.columns:
            if 'attendance' in col.lower() and 'rate' in col.lower():
                attendance_col = col
                break

        if attendance_col:
            invalid_rates = df[(pd.to_numeric(df[attendance_col], errors='coerce') < 0) |
                               (pd.to_numeric(df[attendance_col], errors='coerce') > 100)]
            for idx, row in invalid_rates.iterrows():
                emp_id = str(row.get('Employee No', idx))
                anomaly = self._add_anomaly(
                    anomaly_type=AnomalyType.BUSINESS_RULE,
                    severity=Severity.HIGH,
                    description="Invalid attendance rate (outside 0-100% range)",
                    field=attendance_col,
                    actual=str(row[attendance_col]),
                    expected="0-100%",
                    employee=emp_id,
                    recommendation="Check attendance data calculation"
                )
                detected.append(anomaly)

        # 규칙 3: 연속월 범위 검증 (0-15)
        continuous_col = 'Continuous_Months' if 'Continuous_Months' in df.columns else None
        if continuous_col:
            invalid_months = df[(pd.to_numeric(df[continuous_col], errors='coerce') < 0) |
                                (pd.to_numeric(df[continuous_col], errors='coerce') > 15)]
            for idx, row in invalid_months.iterrows():
                emp_id = str(row.get('Employee No', idx))
                anomaly = self._add_anomaly(
                    anomaly_type=AnomalyType.BUSINESS_RULE,
                    severity=Severity.HIGH,
                    description="Continuous months outside valid range",
                    field=continuous_col,
                    actual=str(row[continuous_col]),
                    expected="0-15",
                    employee=emp_id,
                    recommendation="Verify continuous months calculation"
                )
                detected.append(anomaly)

        return detected

    def detect_data_quality_issues(self, df: pd.DataFrame) -> List[Anomaly]:
        """데이터 품질 문제 탐지"""
        detected = []

        # 중복 직원 번호
        emp_col = 'Employee No' if 'Employee No' in df.columns else None
        if emp_col:
            duplicates = df[df.duplicated(subset=[emp_col], keep=False)]
            if len(duplicates) > 0:
                for emp_no in duplicates[emp_col].unique():
                    anomaly = self._add_anomaly(
                        anomaly_type=AnomalyType.DATA_QUALITY,
                        severity=Severity.CRITICAL,
                        description="Duplicate employee number found",
                        field=emp_col,
                        actual=str(emp_no),
                        expected="Unique",
                        employee=str(emp_no),
                        recommendation="Remove duplicate entries or correct employee numbers"
                    )
                    detected.append(anomaly)

        # 필수 필드 누락
        required_fields = ['Employee No', 'Full Name', 'Continuous_Months']
        for field in required_fields:
            if field in df.columns:
                missing = df[df[field].isna() | (df[field] == '')]
                if len(missing) > 0:
                    anomaly = self._add_anomaly(
                        anomaly_type=AnomalyType.DATA_QUALITY,
                        severity=Severity.MEDIUM,
                        description=f"Missing required field: {field}",
                        field=field,
                        actual=f"{len(missing)} missing values",
                        expected="All values present",
                        recommendation=f"Fill in missing {field} values"
                    )
                    detected.append(anomaly)

        return detected

    def run_full_detection(self, df: pd.DataFrame) -> Dict:
        """전체 이상치 탐지 실행"""
        self.anomalies = []
        self.anomaly_counter = 0

        # 각 유형별 탐지 실행
        stat_anomalies = []
        for col in ['Continuous_Months', 'Actual Working Days', 'Unapproved Absences']:
            if col in df.columns:
                stat_anomalies.extend(self.detect_statistical_anomalies(df, col))

        business_anomalies = self.detect_business_rule_violations(df)
        quality_anomalies = self.detect_data_quality_issues(df)

        # 심각도별 카운트
        severity_counts = {s.value: 0 for s in Severity}
        for a in self.anomalies:
            severity_counts[a.severity.value] += 1

        return {
            "total_anomalies": len(self.anomalies),
            "by_severity": severity_counts,
            "by_type": {
                "statistical": len(stat_anomalies),
                "business_rule": len(business_anomalies),
                "data_quality": len(quality_anomalies),
            },
            "anomalies": [
                {
                    "id": a.anomaly_id,
                    "type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "description": a.description,
                    "employee": a.affected_employee,
                    "field": a.affected_field,
                    "actual": a.actual_value,
                    "expected": a.expected_value,
                    "recommendation": a.recommendation,
                }
                for a in sorted(self.anomalies,
                               key=lambda x: list(Severity).index(x.severity))
            ],
            "detected_at": datetime.now().isoformat()
        }


if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Anomaly Detection System")
    print("=" * 60)

    detector = AnomalyDetector()

    # 샘플 데이터로 테스트
    sample_data = pd.DataFrame({
        'Employee No': ['001', '002', '003', '004', '005', '001'],  # 중복 있음
        'Full Name': ['Kim', 'Lee', 'Park', '', 'Choi', 'Kim2'],    # 빈값 있음
        'TYPE': [1, 2, 3, 1, 1, 1],
        'Final Incentive amount': [150000, 200000, 50000, 300000, 0, 150000],  # TYPE-3 위반
        'Continuous_Months': [5, 3, 0, 20, 2, 5],  # 범위 초과
        '출근율_Attendance_Rate_Percent': [95, 88, 75, 110, 85, 95],  # 범위 초과
    })

    results = detector.run_full_detection(sample_data)

    print(f"\n📊 Detection Results:")
    print(f"   Total anomalies: {results['total_anomalies']}")
    print(f"   By severity: {results['by_severity']}")
    print(f"   By type: {results['by_type']}")

    if results['anomalies']:
        print(f"\n🚨 Top anomalies:")
        for a in results['anomalies'][:5]:
            print(f"   [{a['severity']}] {a['description']}")
            print(f"       Employee: {a['employee']}, Field: {a['field']}")

    print("\n✅ Anomaly Detection Test Complete!")
