#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger System
===================
@ComplianceOfficer & @SecuritySpecialist 협업 개발

감사 로그 시스템 - 모든 시스템 활동을 추적하고 기록
- 데이터 변경 이력
- 사용자 활동 로그
- 계산 실행 기록
- 오류 및 경고 로그

사용법:
    from scripts.audit_logger import AuditLogger

    logger = AuditLogger()
    logger.log_action('CALCULATION', 'Incentive calculation completed', {'month': 12, 'year': 2025})
"""

import os
import json
import hashlib
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class AuditLevel(Enum):
    """감사 로그 레벨"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"


class AuditCategory(Enum):
    """감사 로그 카테고리"""
    CALCULATION = "CALCULATION"      # 인센티브 계산
    DATA_CHANGE = "DATA_CHANGE"      # 데이터 변경
    DATA_ACCESS = "DATA_ACCESS"      # 데이터 접근
    CONFIG_CHANGE = "CONFIG_CHANGE"  # 설정 변경
    USER_ACTION = "USER_ACTION"      # 사용자 행동
    SYSTEM = "SYSTEM"                # 시스템 이벤트
    SECURITY = "SECURITY"            # 보안 관련
    ERROR = "ERROR"                  # 오류
    EXPORT = "EXPORT"                # 데이터 내보내기
    SYNC = "SYNC"                    # Google Drive 동기화


class AuditLogger:
    """
    감사 로그 관리 클래스

    모든 시스템 활동을 JSON 형식으로 기록
    """

    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.hostname = platform.node()
        self.username = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))

        # 현재 날짜 기반 로그 파일
        self.current_log_file = self._get_log_file_path()

        # 세션 시작 로그
        self.log_action(
            AuditCategory.SYSTEM,
            "Audit session started",
            {"session_id": self.session_id},
            AuditLevel.INFO
        )

    def _generate_session_id(self) -> str:
        """고유 세션 ID 생성"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{timestamp}-{os.getpid()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    def _get_log_file_path(self) -> Path:
        """현재 날짜 기반 로그 파일 경로"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{date_str}.json"

    def _load_existing_logs(self) -> List[Dict]:
        """기존 로그 파일 로드"""
        if self.current_log_file.exists():
            try:
                with open(self.current_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_logs(self, logs: List[Dict]):
        """로그 파일 저장"""
        with open(self.current_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2, default=str)

    def log_action(
        self,
        category: AuditCategory,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        affected_records: Optional[int] = None
    ) -> str:
        """
        감사 로그 기록

        Args:
            category: 로그 카테고리
            action: 수행된 작업 설명
            details: 상세 정보 (선택)
            level: 로그 레벨
            affected_records: 영향받은 레코드 수 (선택)

        Returns:
            생성된 로그 ID
        """
        log_id = hashlib.sha256(
            f"{datetime.now().isoformat()}-{action}".encode()
        ).hexdigest()[:12]

        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": category.value if isinstance(category, AuditCategory) else str(category),
            "level": level.value if isinstance(level, AuditLevel) else str(level),
            "action": action,
            "details": details or {},
            "affected_records": affected_records,
            "environment": {
                "hostname": self.hostname,
                "username": self.username,
                "working_dir": str(Path.cwd())
            }
        }

        # 로그 추가
        logs = self._load_existing_logs()
        logs.append(log_entry)
        self._save_logs(logs)

        # 콘솔 출력 (INFO 이상)
        if level in [AuditLevel.WARNING, AuditLevel.ERROR, AuditLevel.CRITICAL, AuditLevel.SECURITY]:
            print(f"[{level.value}] {category.value}: {action}")

        return log_id

    def log_calculation(
        self,
        month: int,
        year: int,
        total_employees: int,
        recipients: int,
        total_amount: float,
        duration_seconds: float
    ) -> str:
        """인센티브 계산 로그"""
        return self.log_action(
            AuditCategory.CALCULATION,
            f"Incentive calculation completed for {month}/{year}",
            {
                "month": month,
                "year": year,
                "total_employees": total_employees,
                "recipients": recipients,
                "total_amount": total_amount,
                "duration_seconds": round(duration_seconds, 2)
            },
            AuditLevel.INFO,
            affected_records=total_employees
        )

    def log_data_change(
        self,
        file_path: str,
        change_type: str,
        before_hash: Optional[str] = None,
        after_hash: Optional[str] = None,
        records_changed: Optional[int] = None
    ) -> str:
        """데이터 변경 로그"""
        return self.log_action(
            AuditCategory.DATA_CHANGE,
            f"Data {change_type}: {Path(file_path).name}",
            {
                "file_path": file_path,
                "change_type": change_type,
                "before_hash": before_hash,
                "after_hash": after_hash
            },
            AuditLevel.INFO,
            affected_records=records_changed
        )

    def log_config_change(
        self,
        config_file: str,
        changed_keys: List[str],
        changed_by: str = "system"
    ) -> str:
        """설정 변경 로그"""
        return self.log_action(
            AuditCategory.CONFIG_CHANGE,
            f"Configuration updated: {Path(config_file).name}",
            {
                "config_file": config_file,
                "changed_keys": changed_keys,
                "changed_by": changed_by
            },
            AuditLevel.WARNING
        )

    def log_export(
        self,
        export_type: str,
        file_path: str,
        record_count: int
    ) -> str:
        """데이터 내보내기 로그"""
        return self.log_action(
            AuditCategory.EXPORT,
            f"Data exported: {export_type}",
            {
                "export_type": export_type,
                "file_path": file_path,
                "record_count": record_count
            },
            AuditLevel.INFO,
            affected_records=record_count
        )

    def log_sync(
        self,
        source: str,
        files_synced: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> str:
        """동기화 로그"""
        level = AuditLevel.INFO if success else AuditLevel.ERROR
        return self.log_action(
            AuditCategory.SYNC,
            f"Sync {'completed' if success else 'failed'}: {source}",
            {
                "source": source,
                "files_synced": files_synced,
                "success": success,
                "error_message": error_message
            },
            level,
            affected_records=files_synced
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """오류 로그"""
        return self.log_action(
            AuditCategory.ERROR,
            f"Error occurred: {error_type}",
            {
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
                "context": context or {}
            },
            AuditLevel.ERROR
        )

    def log_security_event(
        self,
        event_type: str,
        description: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """보안 이벤트 로그"""
        return self.log_action(
            AuditCategory.SECURITY,
            f"Security event: {event_type}",
            {
                "event_type": event_type,
                "description": description,
                "ip_address": ip_address,
                "user_agent": user_agent
            },
            AuditLevel.SECURITY
        )

    def get_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[AuditCategory] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        로그 조회

        Args:
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            category: 필터링할 카테고리
            level: 필터링할 레벨
            limit: 최대 반환 개수

        Returns:
            필터링된 로그 목록
        """
        all_logs = []

        # 날짜 범위의 모든 로그 파일 로드
        for log_file in sorted(self.log_dir.glob("audit_*.json"), reverse=True):
            try:
                file_date = log_file.stem.replace("audit_", "")

                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue

                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    all_logs.extend(logs)

            except (json.JSONDecodeError, IOError):
                continue

        # 필터링
        filtered_logs = all_logs

        if category:
            cat_value = category.value if isinstance(category, AuditCategory) else str(category)
            filtered_logs = [l for l in filtered_logs if l.get('category') == cat_value]

        if level:
            lvl_value = level.value if isinstance(level, AuditLevel) else str(level)
            filtered_logs = [l for l in filtered_logs if l.get('level') == lvl_value]

        # 최신순 정렬 및 제한
        filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return filtered_logs[:limit]

    def generate_summary(self, date: Optional[str] = None) -> Dict:
        """
        일별 감사 로그 요약 생성

        Args:
            date: 요약할 날짜 (YYYY-MM-DD), None이면 오늘

        Returns:
            요약 통계
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        logs = self.get_logs(start_date=date, end_date=date, limit=10000)

        summary = {
            "date": date,
            "total_events": len(logs),
            "by_category": {},
            "by_level": {},
            "errors": [],
            "security_events": []
        }

        for log in logs:
            cat = log.get('category', 'UNKNOWN')
            lvl = log.get('level', 'UNKNOWN')

            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
            summary['by_level'][lvl] = summary['by_level'].get(lvl, 0) + 1

            if lvl in ['ERROR', 'CRITICAL']:
                summary['errors'].append({
                    'timestamp': log.get('timestamp'),
                    'action': log.get('action'),
                    'details': log.get('details')
                })

            if cat == 'SECURITY':
                summary['security_events'].append({
                    'timestamp': log.get('timestamp'),
                    'action': log.get('action'),
                    'details': log.get('details')
                })

        return summary


# 글로벌 로거 인스턴스
_global_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """글로벌 감사 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AuditLogger()
    return _global_logger


def log_action(category: str, action: str, details: Optional[Dict] = None) -> str:
    """간편 로깅 함수"""
    logger = get_audit_logger()
    try:
        cat = AuditCategory[category.upper()]
    except KeyError:
        cat = AuditCategory.SYSTEM
    return logger.log_action(cat, action, details)


if __name__ == '__main__':
    # 테스트
    print("=" * 60)
    print("🔍 Audit Logger Test")
    print("=" * 60)

    logger = AuditLogger()

    # 테스트 로그 생성
    logger.log_action(AuditCategory.SYSTEM, "Test log entry", {"test": True})
    logger.log_calculation(12, 2025, 415, 350, 140000000, 45.2)
    logger.log_data_change("output_files/test.csv", "CREATE", records_changed=100)
    logger.log_config_change("config_files/config.json", ["working_days", "file_paths"])
    logger.log_export("CSV", "output_files/export.csv", 500)
    logger.log_sync("Google Drive", 5, True)
    logger.log_error("ValidationError", "Invalid data format", context={"field": "date"})

    # 요약 출력
    summary = logger.generate_summary()
    print(f"\n📊 Today's Summary:")
    print(f"   Total events: {summary['total_events']}")
    print(f"   By category: {summary['by_category']}")
    print(f"   By level: {summary['by_level']}")

    print("\n✅ Audit Logger Test Complete!")
    print(f"📁 Log file: {logger.current_log_file}")
