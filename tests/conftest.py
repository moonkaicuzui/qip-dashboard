#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest Fixtures and Configuration
=================================
@QAEngineer 개발

공통 테스트 픽스처 및 설정
"""

import os
import sys
import json
import pytest
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root():
    """프로젝트 루트 경로"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def config_dir(project_root):
    """설정 파일 디렉토리"""
    return project_root / "config_files"


@pytest.fixture(scope="session")
def output_dir(project_root):
    """출력 파일 디렉토리"""
    return project_root / "output_files"


@pytest.fixture(scope="session")
def position_matrix(config_dir):
    """직급 조건 매트릭스 로드"""
    matrix_path = config_dir / "position_condition_matrix.json"
    if matrix_path.exists():
        with open(matrix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@pytest.fixture(scope="session")
def sample_month_config(config_dir):
    """샘플 월별 설정 로드 (최신 월)"""
    configs = list(config_dir.glob("config_*_2025.json"))
    if configs:
        latest = sorted(configs)[-1]
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@pytest.fixture(scope="session")
def sample_csv_data(output_dir):
    """샘플 CSV 데이터 로드 (최신 월)"""
    import pandas as pd
    csvs = list(output_dir.glob("output_QIP_incentive_*_Complete_V9.0_Complete.csv"))
    if csvs:
        latest = sorted(csvs)[-1]
        return pd.read_csv(latest)
    return None


@pytest.fixture
def audit_logger():
    """감사 로거 인스턴스 (테스트용)"""
    from scripts.audit_logger import AuditLogger
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        yield logger


@pytest.fixture
def mock_employee_data():
    """테스트용 직원 데이터"""
    return {
        'emp_no': '999999999',
        'Name': 'Test Employee',
        'Position': 'ASSEMBLY INSPECTOR',
        'Position_Code': 'A',
        'TYPE': 1,
        'Attendance_Rate': 95.0,
        'Unapproved_Absences': 0,
        'Actual_Working_Days': 20,
        'Total_Working_Days': 22,
        'AQL_Fail_Percent': 0.0,
        'Continuous_FAIL': 'NO',
        'Team_AQL_FAIL': 'NO',
        '5PRS_Pass_Rate': 98.5,
        '5PRS_Qty': 150,
        'Continuous_Months': 5,
        'November_Incentive': 350000
    }


@pytest.fixture
def type1_progression_table():
    """TYPE-1 인센티브 진행 테이블"""
    return {
        1: 150000, 2: 200000, 3: 250000, 4: 300000,
        5: 350000, 6: 400000, 7: 450000, 8: 500000,
        9: 600000, 10: 700000, 11: 800000, 12: 1000000,
        13: 1000000, 14: 1000000, 15: 1000000
    }


def pytest_configure(config):
    """pytest 설정 시 실행"""
    print(f"\n{'='*60}")
    print("🧪 QIP Dashboard Test Suite")
    print(f"{'='*60}")
    print(f"   Project: {PROJECT_ROOT.name}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


def pytest_collection_modifyitems(items):
    """테스트 수집 후 실행 순서 조정"""
    # unit 테스트를 먼저 실행
    unit_tests = []
    other_tests = []

    for item in items:
        if 'unit' in [marker.name for marker in item.iter_markers()]:
            unit_tests.append(item)
        else:
            other_tests.append(item)

    items[:] = unit_tests + other_tests
