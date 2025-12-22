#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Role-Based Access Control (RBAC) Manager
=========================================
@SecuritySpecialist & @ComplianceOfficer 협업 개발

역할 기반 접근 제어 시스템:
- 사용자 역할 정의
- 권한 관리
- 접근 제어 규칙
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import json
from pathlib import Path


class Role(Enum):
    """사용자 역할"""
    ADMIN = "admin"                # 전체 관리자
    HR_MANAGER = "hr_manager"      # HR 관리자
    FINANCE = "finance"            # 재무팀
    SUPERVISOR = "supervisor"      # 수퍼바이저
    LINE_LEADER = "line_leader"    # 라인 리더
    VIEWER = "viewer"              # 조회 전용


class Permission(Enum):
    """권한 유형"""
    # 데이터 조회
    VIEW_ALL_EMPLOYEES = "view_all_employees"
    VIEW_TEAM_ONLY = "view_team_only"
    VIEW_INCENTIVE_DETAILS = "view_incentive_details"
    VIEW_SALARY_INFO = "view_salary_info"

    # 데이터 수정
    EDIT_CONDITIONS = "edit_conditions"
    EDIT_EMPLOYEE_DATA = "edit_employee_data"
    APPROVE_INCENTIVES = "approve_incentives"

    # 보고서
    EXPORT_DATA = "export_data"
    GENERATE_REPORTS = "generate_reports"

    # 시스템
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    SYSTEM_CONFIG = "system_config"


@dataclass
class User:
    """사용자 정보"""
    user_id: str
    name: str
    role: Role
    department: str
    team: Optional[str] = None
    building: Optional[str] = None
    custom_permissions: Optional[Set[Permission]] = None


class RBACManager:
    """역할 기반 접근 제어 관리자"""

    # 역할별 기본 권한 매핑
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.ADMIN: {
            Permission.VIEW_ALL_EMPLOYEES,
            Permission.VIEW_INCENTIVE_DETAILS,
            Permission.VIEW_SALARY_INFO,
            Permission.EDIT_CONDITIONS,
            Permission.EDIT_EMPLOYEE_DATA,
            Permission.APPROVE_INCENTIVES,
            Permission.EXPORT_DATA,
            Permission.GENERATE_REPORTS,
            Permission.MANAGE_USERS,
            Permission.VIEW_AUDIT_LOGS,
            Permission.SYSTEM_CONFIG,
        },
        Role.HR_MANAGER: {
            Permission.VIEW_ALL_EMPLOYEES,
            Permission.VIEW_INCENTIVE_DETAILS,
            Permission.VIEW_SALARY_INFO,
            Permission.EDIT_EMPLOYEE_DATA,
            Permission.APPROVE_INCENTIVES,
            Permission.EXPORT_DATA,
            Permission.GENERATE_REPORTS,
            Permission.VIEW_AUDIT_LOGS,
        },
        Role.FINANCE: {
            Permission.VIEW_ALL_EMPLOYEES,
            Permission.VIEW_INCENTIVE_DETAILS,
            Permission.VIEW_SALARY_INFO,
            Permission.EXPORT_DATA,
            Permission.GENERATE_REPORTS,
        },
        Role.SUPERVISOR: {
            Permission.VIEW_ALL_EMPLOYEES,
            Permission.VIEW_INCENTIVE_DETAILS,
            Permission.EXPORT_DATA,
        },
        Role.LINE_LEADER: {
            Permission.VIEW_TEAM_ONLY,
            Permission.VIEW_INCENTIVE_DETAILS,
        },
        Role.VIEWER: {
            Permission.VIEW_TEAM_ONLY,
        },
    }

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.config_path = Path("config_files/rbac_config.json")

    def add_user(self, user: User) -> bool:
        """사용자 추가"""
        self.users[user.user_id] = user
        return True

    def get_user(self, user_id: str) -> Optional[User]:
        """사용자 조회"""
        return self.users.get(user_id)

    def get_permissions(self, user: User) -> Set[Permission]:
        """사용자 권한 조회"""
        base_permissions = self.ROLE_PERMISSIONS.get(user.role, set())
        if user.custom_permissions:
            return base_permissions | user.custom_permissions
        return base_permissions

    def has_permission(self, user: User, permission: Permission) -> bool:
        """권한 확인"""
        permissions = self.get_permissions(user)
        return permission in permissions

    def can_view_employee(self, user: User, employee_data: dict) -> bool:
        """직원 데이터 조회 가능 여부"""
        permissions = self.get_permissions(user)

        # 전체 조회 권한
        if Permission.VIEW_ALL_EMPLOYEES in permissions:
            return True

        # 팀만 조회 권한
        if Permission.VIEW_TEAM_ONLY in permissions:
            # 같은 팀/빌딩인지 확인
            if user.team and employee_data.get('team') == user.team:
                return True
            if user.building and employee_data.get('building') == user.building:
                return True

        return False

    def filter_employees_by_access(
        self,
        user: User,
        employees: List[dict]
    ) -> List[dict]:
        """접근 권한에 따라 직원 목록 필터링"""
        return [emp for emp in employees if self.can_view_employee(user, emp)]

    def filter_sensitive_fields(
        self,
        user: User,
        data: dict
    ) -> dict:
        """권한에 따라 민감 필드 필터링"""
        permissions = self.get_permissions(user)
        filtered = data.copy()

        # 급여 정보 마스킹
        if Permission.VIEW_SALARY_INFO not in permissions:
            salary_fields = ['salary', 'base_pay', 'bonus']
            for field in salary_fields:
                if field in filtered:
                    filtered[field] = '***'

        # 인센티브 상세 마스킹
        if Permission.VIEW_INCENTIVE_DETAILS not in permissions:
            incentive_fields = ['incentive_breakdown', 'calculation_details']
            for field in incentive_fields:
                if field in filtered:
                    filtered[field] = '***'

        return filtered

    def get_access_summary(self, user: User) -> dict:
        """사용자 접근 권한 요약"""
        permissions = self.get_permissions(user)
        return {
            'user_id': user.user_id,
            'name': user.name,
            'role': user.role.value,
            'department': user.department,
            'permissions': [p.value for p in permissions],
            'can_view_all': Permission.VIEW_ALL_EMPLOYEES in permissions,
            'can_export': Permission.EXPORT_DATA in permissions,
            'can_edit': Permission.EDIT_EMPLOYEE_DATA in permissions,
            'is_admin': user.role == Role.ADMIN,
        }

    def save_config(self):
        """설정 저장"""
        config = {
            'users': {
                uid: {
                    'name': u.name,
                    'role': u.role.value,
                    'department': u.department,
                    'team': u.team,
                    'building': u.building,
                }
                for uid, u in self.users.items()
            },
            'role_permissions': {
                role.value: [p.value for p in perms]
                for role, perms in self.ROLE_PERMISSIONS.items()
            }
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_config(self):
        """설정 로드"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 사용자 로드 로직
                for uid, data in config.get('users', {}).items():
                    role = Role(data['role'])
                    user = User(
                        user_id=uid,
                        name=data['name'],
                        role=role,
                        department=data['department'],
                        team=data.get('team'),
                        building=data.get('building'),
                    )
                    self.add_user(user)


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 RBAC Manager Test")
    print("=" * 60)

    manager = RBACManager()

    # 테스트 사용자 생성
    admin = User(
        user_id="admin001",
        name="Admin User",
        role=Role.ADMIN,
        department="IT"
    )

    line_leader = User(
        user_id="ll001",
        name="Line Leader",
        role=Role.LINE_LEADER,
        department="Production",
        team="Team A",
        building="B1"
    )

    manager.add_user(admin)
    manager.add_user(line_leader)

    # 권한 테스트
    print(f"\nAdmin permissions:")
    for perm in manager.get_permissions(admin):
        print(f"  ✅ {perm.value}")

    print(f"\nLine Leader permissions:")
    for perm in manager.get_permissions(line_leader):
        print(f"  ✅ {perm.value}")

    print("\n✅ RBAC Manager Test Complete!")
