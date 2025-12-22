#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger Tests
==================
@QAEngineer & @SecuritySpecialist 협업 개발

감사 로그 시스템 검증:
- 로그 생성 및 저장
- 카테고리별 로깅
- 로그 조회 및 필터링
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import tempfile
import sys

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.audit_logger import (
    AuditLogger, AuditLevel, AuditCategory,
    get_audit_logger, log_action
)


class TestAuditLoggerBasic:
    """기본 로깅 기능 테스트"""

    @pytest.mark.unit
    def test_logger_initialization(self, audit_logger):
        """로거 초기화"""
        assert audit_logger is not None
        assert audit_logger.session_id is not None
        assert len(audit_logger.session_id) == 16

    @pytest.mark.unit
    def test_log_action_returns_id(self, audit_logger):
        """로그 액션이 ID 반환"""
        log_id = audit_logger.log_action(
            AuditCategory.SYSTEM,
            "Test action",
            {"test": True}
        )
        assert log_id is not None
        assert len(log_id) == 12

    @pytest.mark.unit
    def test_log_saved_to_file(self, audit_logger):
        """로그가 파일에 저장됨"""
        audit_logger.log_action(
            AuditCategory.CALCULATION,
            "Test calculation"
        )

        assert audit_logger.current_log_file.exists()
        with open(audit_logger.current_log_file, 'r') as f:
            logs = json.load(f)
        assert len(logs) >= 1


class TestAuditCategories:
    """카테고리별 로깅 테스트"""

    @pytest.mark.unit
    def test_log_calculation(self, audit_logger):
        """인센티브 계산 로그"""
        log_id = audit_logger.log_calculation(
            month=12,
            year=2025,
            total_employees=415,
            recipients=350,
            total_amount=140000000,
            duration_seconds=45.2
        )
        assert log_id is not None

    @pytest.mark.unit
    def test_log_data_change(self, audit_logger):
        """데이터 변경 로그"""
        log_id = audit_logger.log_data_change(
            file_path="test.csv",
            change_type="UPDATE",
            records_changed=100
        )
        assert log_id is not None

    @pytest.mark.unit
    def test_log_sync(self, audit_logger):
        """동기화 로그"""
        log_id = audit_logger.log_sync(
            source="Google Drive",
            files_synced=5,
            success=True
        )
        assert log_id is not None

    @pytest.mark.unit
    def test_log_error(self, audit_logger):
        """오류 로그"""
        log_id = audit_logger.log_error(
            error_type="ValidationError",
            error_message="Invalid data format",
            context={"field": "date"}
        )
        assert log_id is not None

    @pytest.mark.unit
    def test_log_security_event(self, audit_logger):
        """보안 이벤트 로그"""
        log_id = audit_logger.log_security_event(
            event_type="LOGIN_ATTEMPT",
            description="Failed login attempt"
        )
        assert log_id is not None


class TestLogRetrieval:
    """로그 조회 테스트"""

    @pytest.mark.unit
    def test_get_logs_default(self, audit_logger):
        """기본 로그 조회"""
        # 로그 생성
        audit_logger.log_action(AuditCategory.SYSTEM, "Test 1")
        audit_logger.log_action(AuditCategory.CALCULATION, "Test 2")

        logs = audit_logger.get_logs()
        assert len(logs) >= 2

    @pytest.mark.unit
    def test_get_logs_by_category(self, audit_logger):
        """카테고리별 로그 조회"""
        audit_logger.log_action(AuditCategory.SYSTEM, "System log")
        audit_logger.log_action(AuditCategory.SECURITY, "Security log")

        system_logs = audit_logger.get_logs(category=AuditCategory.SYSTEM)
        assert all(log['category'] == 'SYSTEM' for log in system_logs)

    @pytest.mark.unit
    def test_get_logs_by_level(self, audit_logger):
        """레벨별 로그 조회"""
        audit_logger.log_action(
            AuditCategory.ERROR,
            "Error log",
            level=AuditLevel.ERROR
        )

        error_logs = audit_logger.get_logs(level=AuditLevel.ERROR)
        assert all(log['level'] == 'ERROR' for log in error_logs)


class TestLogSummary:
    """로그 요약 테스트"""

    @pytest.mark.unit
    def test_generate_summary(self, audit_logger):
        """일별 요약 생성"""
        audit_logger.log_action(AuditCategory.SYSTEM, "Test 1")
        audit_logger.log_action(AuditCategory.CALCULATION, "Test 2")
        audit_logger.log_error("TestError", "Test error")

        summary = audit_logger.generate_summary()

        assert 'date' in summary
        assert 'total_events' in summary
        assert 'by_category' in summary
        assert 'by_level' in summary
        assert summary['total_events'] >= 3


class TestGlobalLogger:
    """글로벌 로거 테스트"""

    @pytest.mark.unit
    def test_get_audit_logger_singleton(self):
        """싱글톤 패턴 검증"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 글로벌 로거 리셋
            import scripts.audit_logger as al
            al._global_logger = None

            logger1 = get_audit_logger()
            logger2 = get_audit_logger()

            assert logger1 is logger2

    @pytest.mark.unit
    def test_log_action_convenience(self):
        """간편 로깅 함수"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import scripts.audit_logger as al
            al._global_logger = AuditLogger(log_dir=tmpdir)

            log_id = log_action('CALCULATION', 'Test action')
            assert log_id is not None
