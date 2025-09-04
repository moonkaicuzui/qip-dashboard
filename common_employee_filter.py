#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공통 직원 필터링 모듈
인센티브 대시보드와 매니지먼트 대시보드에서 동일한 기준으로 직원 필터링

이 모듈은 단일 진실의 원천(Single Source of Truth)으로
모든 대시보드에서 일관된 직원 카운팅을 보장합니다.
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Tuple


class EmployeeFilter:
    """
    직원 필터링을 위한 공통 클래스
    모든 대시보드에서 동일한 로직 사용
    """
    
    @staticmethod
    def filter_active_employees(df: pd.DataFrame, 
                              target_month: int, 
                              target_year: int,
                              include_future: bool = False) -> pd.DataFrame:
        """
        활성 직원만 필터링하는 핵심 로직
        
        Args:
            df: 원본 데이터프레임
            target_month: 대상 월 (1-12)
            target_year: 대상 년도
            include_future: 미래 입사자 포함 여부 (기본값: False)
            
        Returns:
            필터링된 데이터프레임
            
        필터링 기준:
        1. Employee No가 있는 직원만 (필수)
        2. target_month 이전 퇴사자 제외
        3. include_future=False인 경우 target_month 이후 입사자 제외
        """
        if df.empty:
            return df
            
        # 복사본 생성하여 원본 데이터 보호
        df_copy = df.copy()
        
        # 1단계: Employee No가 있는 실제 직원만 선택
        print(f"  [필터] 전체 레코드: {len(df_copy)}개")
        valid_employees = df_copy[df_copy['Employee No'].notna()]
        print(f"  [필터] Employee No 있는 직원: {len(valid_employees)}개")
        
        if valid_employees.empty:
            return valid_employees
        
        # 2단계: 날짜 파싱 확인
        if 'Stop working Date' in valid_employees.columns:
            if valid_employees['Stop working Date'].dtype == 'object':
                valid_employees.loc[:, 'Stop working Date'] = pd.to_datetime(
                    valid_employees['Stop working Date'], errors='coerce'
                )
        
        if 'Entrance Date' in valid_employees.columns:
            if valid_employees['Entrance Date'].dtype == 'object':
                valid_employees.loc[:, 'Entrance Date'] = pd.to_datetime(
                    valid_employees['Entrance Date'], errors='coerce'
                )
        
        # 3단계: 계산 월 기준일 설정
        calc_month_start = pd.Timestamp(target_year, target_month, 1)
        
        # 다음 월의 첫날 계산 (월말 처리)
        if target_month == 12:
            calc_month_end = pd.Timestamp(target_year + 1, 1, 1)
        else:
            calc_month_end = pd.Timestamp(target_year, target_month + 1, 1)
        
        # 4단계: 퇴사자 필터링
        if 'Stop working Date' in valid_employees.columns:
            # 활성 직원: 퇴사일이 없거나 계산 월 이후 퇴사자
            before_filter_count = len(valid_employees)
            active_employees = valid_employees[
                (valid_employees['Stop working Date'].isna()) |  # 퇴사일 없는 직원
                (valid_employees['Stop working Date'] >= calc_month_start)  # 계산 월 이후 퇴사자
            ]
            print(f"  [필터] 퇴사자 제외 후: {len(active_employees)}개 ({before_filter_count - len(active_employees)}명 제외)")
        else:
            active_employees = valid_employees
        
        # 5단계: 미래 입사자 필터링 (옵션)
        if not include_future and 'Entrance Date' in active_employees.columns:
            before_filter_count = len(active_employees)
            active_employees = active_employees[
                (active_employees['Entrance Date'].isna()) |  # 입사일 없는 직원 (기존 직원)
                (active_employees['Entrance Date'] < calc_month_end)  # 계산 월 이전/당월 입사자
            ]
            print(f"  [필터] 미래 입사자 제외 후: {len(active_employees)}개 ({before_filter_count - len(active_employees)}명 제외)")
        
        print(f"  [필터] 최종 활성 직원: {len(active_employees)}명")
        return active_employees
    
    @staticmethod
    def get_team_statistics(df: pd.DataFrame,
                           target_month: int,
                           target_year: int,
                           team_column: str = 'Team') -> Dict[str, Dict[str, Any]]:
        """
        팀별 통계 계산 (공통 로직)
        
        Args:
            df: 필터링된 데이터프레임
            target_month: 대상 월
            target_year: 대상 년도
            team_column: 팀 컬럼명
            
        Returns:
            팀별 통계 딕셔너리
        """
        if df.empty or team_column not in df.columns:
            return {}
        
        team_stats = {}
        
        # 팀별 그룹화
        for team in df[team_column].unique():
            if pd.isna(team):
                continue
                
            team_df = df[df[team_column] == team]
            
            # 기본 통계
            stats = {
                'total': len(team_df),
                'attendance_rate': 0.0,
                'absence_rate': 0.0,
                'new_hires': 0,
                'resignations': 0,
                'full_attendance_count': 0,
                'full_attendance_rate': 0.0
            }
            
            # 출근율 계산
            if 'Actual Working Days' in team_df.columns and 'Total Working Days' in team_df.columns:
                actual_sum = team_df['Actual Working Days'].sum()
                total_sum = team_df['Total Working Days'].sum()
                if total_sum > 0:
                    stats['attendance_rate'] = round(actual_sum / total_sum * 100, 2)
                    stats['absence_rate'] = round(100 - stats['attendance_rate'], 2)
            
            # 신규 입사자 (해당 월 입사)
            if 'Entrance Date' in team_df.columns:
                calc_month_start = pd.Timestamp(target_year, target_month, 1)
                if target_month == 12:
                    calc_month_end = pd.Timestamp(target_year + 1, 1, 1)
                else:
                    calc_month_end = pd.Timestamp(target_year, target_month + 1, 1)
                
                new_hires = team_df[
                    (team_df['Entrance Date'] >= calc_month_start) & 
                    (team_df['Entrance Date'] < calc_month_end)
                ]
                stats['new_hires'] = len(new_hires)
            
            # 퇴사자 (해당 월 퇴사)
            if 'Stop working Date' in team_df.columns:
                calc_month_start = pd.Timestamp(target_year, target_month, 1)
                if target_month == 12:
                    calc_month_end = pd.Timestamp(target_year + 1, 1, 1)
                else:
                    calc_month_end = pd.Timestamp(target_year, target_month + 1, 1)
                
                resignations = team_df[
                    (team_df['Stop working Date'] >= calc_month_start) & 
                    (team_df['Stop working Date'] < calc_month_end)
                ]
                stats['resignations'] = len(resignations)
            
            # 만근자 수 (Actual = Total인 직원)
            if 'Actual Working Days' in team_df.columns and 'Total Working Days' in team_df.columns:
                full_attendance = team_df[
                    team_df['Actual Working Days'] == team_df['Total Working Days']
                ]
                stats['full_attendance_count'] = len(full_attendance)
                if len(team_df) > 0:
                    stats['full_attendance_rate'] = round(len(full_attendance) / len(team_df) * 100, 2)
            
            team_stats[team] = stats
        
        return team_stats
    
    @staticmethod
    def get_summary_statistics(df: pd.DataFrame,
                              target_month: int,
                              target_year: int) -> Dict[str, Any]:
        """
        전체 요약 통계 계산
        
        Args:
            df: 필터링된 데이터프레임
            target_month: 대상 월
            target_year: 대상 년도
            
        Returns:
            요약 통계 딕셔너리
        """
        if df.empty:
            return {
                'total_employees': 0,
                'attendance_rate': 0.0,
                'absence_rate': 0.0,
                'new_hires': 0,
                'resignations': 0,
                'full_attendance_count': 0,
                'full_attendance_rate': 0.0
            }
        
        summary = {
            'total_employees': len(df),
            'attendance_rate': 0.0,
            'absence_rate': 0.0,
            'new_hires': 0,
            'resignations': 0,
            'full_attendance_count': 0,
            'full_attendance_rate': 0.0
        }
        
        # 출근율 계산
        if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
            actual_sum = df['Actual Working Days'].sum()
            total_sum = df['Total Working Days'].sum()
            if total_sum > 0:
                summary['attendance_rate'] = round(actual_sum / total_sum * 100, 2)
                summary['absence_rate'] = round(100 - summary['attendance_rate'], 2)
        
        # 월 기준일 계산
        calc_month_start = pd.Timestamp(target_year, target_month, 1)
        if target_month == 12:
            calc_month_end = pd.Timestamp(target_year + 1, 1, 1)
        else:
            calc_month_end = pd.Timestamp(target_year, target_month + 1, 1)
        
        # 신규 입사자
        if 'Entrance Date' in df.columns:
            new_hires = df[
                (df['Entrance Date'] >= calc_month_start) & 
                (df['Entrance Date'] < calc_month_end)
            ]
            summary['new_hires'] = len(new_hires)
        
        # 퇴사자
        if 'Stop working Date' in df.columns:
            resignations = df[
                (df['Stop working Date'] >= calc_month_start) & 
                (df['Stop working Date'] < calc_month_end)
            ]
            summary['resignations'] = len(resignations)
        
        # 만근자
        if 'Actual Working Days' in df.columns and 'Total Working Days' in df.columns:
            full_attendance = df[
                df['Actual Working Days'] == df['Total Working Days']
            ]
            summary['full_attendance_count'] = len(full_attendance)
            if len(df) > 0:
                summary['full_attendance_rate'] = round(len(full_attendance) / len(df) * 100, 2)
        
        return summary
    
    @staticmethod
    def get_type_statistics(df: pd.DataFrame) -> Tuple[int, int, int]:
        """
        TYPE별 인원 계산 (TYPE-1, TYPE-2, TYPE-3)
        
        Args:
            df: 필터링된 데이터프레임
            
        Returns:
            (type1_count, type2_count, type3_count)
        """
        type1_count = 0
        type2_count = 0
        type3_count = 0
        
        # TYPE 또는 ROLE TYPE STD 컬럼 확인
        type_column = None
        if 'TYPE' in df.columns:
            type_column = 'TYPE'
        elif 'ROLE TYPE STD' in df.columns:
            type_column = 'ROLE TYPE STD'
        
        if type_column:
            type1_count = len(df[df[type_column] == 'TYPE-1'])
            type2_count = len(df[df[type_column] == 'TYPE-2'])
            type3_count = len(df[df[type_column] == 'TYPE-3'])
        
        return type1_count, type2_count, type3_count


# 테스트 코드
if __name__ == "__main__":
    print("공통 직원 필터링 모듈 로드 완료")
    print("=" * 60)
    print("제공 기능:")
    print("  - filter_active_employees: 활성 직원 필터링")
    print("  - get_team_statistics: 팀별 통계 계산")
    print("  - get_summary_statistics: 전체 요약 통계")
    print("  - get_type_statistics: TYPE별 인원 계산")
    print("=" * 60)