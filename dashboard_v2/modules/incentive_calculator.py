#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard V2 - Incentive Calculation Module
Version 5의 모든 인센티브 계산 로직을 모듈화
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IncentiveCalculator:
    """인센티브 계산 엔진 - Version 5의 모든 로직 포함"""

    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.month_num = self._get_month_number(month)
        self.working_days = 13  # 기본값, 실제 데이터에서 로드

        # 파일 경로 설정
        self.base_path = Path(__file__).parent.parent.parent
        self.input_path = self.base_path / 'input_files'
        self.output_path = self.base_path / 'output_files'
        self.config_path = self.base_path / 'config_files'

        # 데이터 저장소
        self.df_incentive = None
        self.df_basic = None
        self.condition_matrix = None
        self.area_mapping = None
        self.translations = None
        self.excel_dashboard_data = None

    def _get_month_number(self, month_str):
        """월 이름을 숫자로 변환"""
        months = {
            'january': 1, 'february': 2, 'march': 3,
            'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9,
            'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_str.lower(), 0)

    def load_translations(self):
        """번역 파일 로드"""
        translation_file = self.config_path / 'dashboard_translations.json'
        if translation_file.exists():
            with open(translation_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
                logger.info(f"✅ 번역 파일 로드 완료: {translation_file}")
        else:
            logger.warning(f"⚠️ 번역 파일이 없습니다: {translation_file}")
            self.translations = {}
        return self.translations

    def load_condition_matrix(self):
        """조건 매트릭스 로드"""
        matrix_file = self.config_path / 'position_condition_matrix.json'
        if matrix_file.exists():
            with open(matrix_file, 'r', encoding='utf-8') as f:
                self.condition_matrix = json.load(f)
                logger.info("✅ 조건 매트릭스 로드 완료")
        else:
            logger.error(f"❌ 조건 매트릭스 파일이 없습니다: {matrix_file}")
            self.condition_matrix = {}
        return self.condition_matrix

    def load_area_mapping(self):
        """구역 매핑 파일 로드"""
        area_file = self.input_path / 'area_mapping.json'
        if area_file.exists():
            with open(area_file, 'r', encoding='utf-8') as f:
                self.area_mapping = json.load(f)
                logger.info("✅ 구역 매핑 로드 완료")
        else:
            logger.warning("⚠️ 구역 매핑 파일이 없습니다")
            self.area_mapping = {}
        return self.area_mapping

    def load_incentive_data(self, generate_prev=True):
        """인센티브 데이터 로드 - Version 5와 동일한 로직"""
        # CSV 파일 경로
        csv_file = self.output_path / f'output_QIP_incentive_{self.month}_{self.year}_최종완성버전_v6.0_Complete_enhanced.csv'

        if not csv_file.exists():
            # 대체 파일 경로들
            alternative_files = [
                self.output_path / f'output_QIP_incentive_{self.month}_{self.year}_최종완성버전_v6.0_Complete.csv',
                self.output_path / f'output_QIP_incentive_{self.month}_{self.year}_최종완성버전_v5.0_Complete.csv',
                self.output_path / f'output_QIP_incentive_{self.month}_{self.year}_enhanced.csv',
                self.output_path / f'output_QIP_incentive_{self.month}_{self.year}.csv'
            ]

            for alt_file in alternative_files:
                if alt_file.exists():
                    csv_file = alt_file
                    break

        if csv_file.exists():
            # CSV 파일 로드
            self.df_incentive = pd.read_csv(csv_file, encoding='utf-8-sig')

            # 컬럼명 정규화
            if 'Employee No' in self.df_incentive.columns:
                self.df_incentive['employee_no'] = self.df_incentive['Employee No'].astype(str)
            if 'Full Name' in self.df_incentive.columns:
                self.df_incentive['name'] = self.df_incentive['Full Name']
            if 'QIP POSITION 1ST  NAME' in self.df_incentive.columns:
                self.df_incentive['position'] = self.df_incentive['QIP POSITION 1ST  NAME']

            # 인센티브 컬럼 매핑
            month_incentive_col = f'{self.month}_incentive'
            if month_incentive_col in self.df_incentive.columns:
                self.df_incentive['current_incentive'] = self.df_incentive[month_incentive_col]
            elif 'September Incentive' in self.df_incentive.columns:
                self.df_incentive['current_incentive'] = self.df_incentive['September Incentive']

            logger.info(f"✅ 인센티브 데이터 로드: {csv_file}")
            logger.info(f"   - 총 {len(self.df_incentive)}명의 직원 데이터 로드")

            # Previous_Incentive 컬럼 확인
            if 'Previous_Incentive' in self.df_incentive.columns:
                logger.info("✅ Excel의 Previous_Incentive 컬럼 사용")

            return self.df_incentive
        else:
            logger.error(f"❌ 인센티브 파일을 찾을 수 없습니다: {csv_file}")
            return pd.DataFrame()

    def load_basic_manpower_data(self):
        """Basic manpower 데이터 로드"""
        basic_file = self.input_path / f'basic manpower data {self.month}.csv'

        if basic_file.exists():
            try:
                self.df_basic = pd.read_csv(basic_file, encoding='utf-8-sig')
                # 데이터 정리
                self.df_basic = self.df_basic.dropna(subset=['Employee No', 'Full Name'], how='all')
                self.df_basic = self.df_basic[self.df_basic['Employee No'].notna()]

                # Employee No 정규화
                self.df_basic['Employee No'] = self.df_basic['Employee No'].apply(
                    lambda x: str(int(float(x))) if pd.notna(x) and x != '' else ''
                )

                logger.info(f"✅ Basic manpower 데이터 로드 완료: {len(self.df_basic)} 직원")
                return self.df_basic
            except Exception as e:
                logger.error(f"❌ Basic manpower 데이터 로드 실패: {e}")
                return pd.DataFrame()
        else:
            logger.warning(f"⚠️ Basic manpower 파일이 없습니다: {basic_file}")
            return pd.DataFrame()

    def load_excel_dashboard_data(self):
        """Excel 대시보드 데이터 로드"""
        json_file = self.output_path / 'dashboard_data_from_excel.json'

        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                self.excel_dashboard_data = json.load(f)
                logger.info("✅ Excel 기반 대시보드 데이터 로드")

                # 실제 총 근무일수 확인
                if self.excel_dashboard_data and 'attendance' in self.excel_dashboard_data:
                    actual_working_days = self.excel_dashboard_data['attendance'].get('total_working_days', 13)
                    logger.info(f"📊 실제 총 근무일수 (출근 데이터 기반): {actual_working_days}일")
                    self.working_days = actual_working_days
        else:
            logger.warning(f"⚠️ Excel 대시보드 데이터 파일이 없습니다: {json_file}")
            self.excel_dashboard_data = {}

        return self.excel_dashboard_data

    def calculate_statistics(self):
        """통계 계산"""
        if self.df_incentive is None or self.df_incentive.empty:
            return {
                'totalEmployees': 0,
                'paidEmployees': 0,
                'paymentRate': 0,
                'totalAmount': 0
            }

        # 활성 직원만 필터링
        df_active = self.df_incentive.copy()

        # 통계 계산
        total_employees = len(df_active)

        # 인센티브를 받는 직원 계산
        paid_employees = 0
        total_amount = 0

        if 'current_incentive' in df_active.columns:
            # 인센티브 값 파싱
            df_active['incentive_amount'] = df_active['current_incentive'].apply(self._parse_incentive)
            paid_employees = len(df_active[df_active['incentive_amount'] > 0])
            total_amount = df_active['incentive_amount'].sum()

        payment_rate = (paid_employees / total_employees * 100) if total_employees > 0 else 0

        stats = {
            'totalEmployees': total_employees,
            'paidEmployees': paid_employees,
            'paymentRate': round(payment_rate, 1),
            'totalAmount': int(total_amount)
        }

        logger.info(f"📊 통계 계산 완료:")
        logger.info(f"   - 전체 직원: {total_employees}명")
        logger.info(f"   - 지급 대상: {paid_employees}명")
        logger.info(f"   - 지급률: {payment_rate:.1f}%")
        logger.info(f"   - 총 지급액: {total_amount:,.0f} VND")

        return stats

    def _parse_incentive(self, value):
        """인센티브 값 파싱"""
        if pd.isna(value) or value == '' or value == '0':
            return 0
        try:
            # 문자열인 경우 숫자만 추출
            if isinstance(value, str):
                value = value.replace(',', '').replace(' ', '').replace('VND', '')
            return float(value)
        except:
            return 0

    def get_applicable_conditions(self, position, type_name):
        """해당 포지션에 적용되는 조건 목록 반환"""
        if not self.condition_matrix:
            return []

        # TYPE별 조건 매핑
        type_conditions = self.condition_matrix.get('type_conditions', {})
        condition_ids = type_conditions.get(type_name, [])

        # 조건 정의 가져오기
        conditions_def = self.condition_matrix.get('conditions', {})
        applicable = []

        for cond_id in condition_ids:
            cond_def = conditions_def.get(str(cond_id), {})
            if cond_def:
                applicable.append({
                    'id': cond_id,
                    'name': cond_def.get('name_ko', ''),
                    'field': cond_def.get('field', ''),
                    'operator': cond_def.get('operator', ''),
                    'value': cond_def.get('value', ''),
                    'is_special': cond_def.get('is_special', False)
                })

        return applicable

    def evaluate_conditions(self, emp_data):
        """직원의 모든 조건 평가"""
        if not self.condition_matrix:
            return []

        position = emp_data.get('position', '')
        type_name = emp_data.get('type', '')

        # 적용 가능한 조건 목록 가져오기
        applicable_conditions = self.get_applicable_conditions(position, type_name)
        results = []

        for condition in applicable_conditions:
            # 각 조건 평가
            is_met = self._evaluate_single_condition(emp_data, condition)
            results.append({
                'id': condition['id'],
                'name': condition['name'],
                'is_met': is_met,
                'actual': emp_data.get(condition['field'], 'N/A')
            })

        return results

    def _evaluate_single_condition(self, emp_data, condition):
        """단일 조건 평가"""
        field = condition['field']
        operator = condition['operator']
        threshold = condition['value']

        # 실제 값 가져오기
        actual = emp_data.get(field)

        if actual is None or actual == 'N/A':
            return False

        try:
            # 연산자별 평가
            if operator == '>=':
                return float(actual) >= float(threshold)
            elif operator == '<=':
                return float(actual) <= float(threshold)
            elif operator == '>':
                return float(actual) > float(threshold)
            elif operator == '<':
                return float(actual) < float(threshold)
            elif operator == '==':
                return str(actual) == str(threshold)
            elif operator == '!=':
                return str(actual) != str(threshold)
            else:
                return False
        except:
            return False

    def process_all_data(self):
        """모든 데이터 처리 및 통합"""
        # 1. 데이터 로드
        self.load_translations()
        self.load_condition_matrix()
        self.load_area_mapping()
        self.load_incentive_data()
        self.load_basic_manpower_data()
        self.load_excel_dashboard_data()

        # 2. 데이터 병합
        if self.df_incentive is not None and self.df_basic is not None and not self.df_basic.empty:
            # Basic 데이터와 병합하여 boss 정보 추가
            # 컬럼명 확인 및 매핑
            boss_id_col = None
            boss_name_col = None

            # 가능한 컬럼명 변형 확인
            for col in self.df_basic.columns:
                if 'boss' in col.lower() and 'name' in col.lower() and 'direct' in col.lower():
                    boss_name_col = col
                elif 'manager' in col.lower() and 'name' in col.lower():
                    boss_name_col = col
                elif 'boss' in col.lower() and ('id' in col.lower() or 'no' in col.lower()):
                    boss_id_col = col
                elif 'manager' in col.lower() and ('id' in col.lower() or 'no' in col.lower()):
                    boss_id_col = col

            # 실제 존재하는 컬럼만 선택
            merge_columns = ['Employee No']
            if boss_id_col:
                merge_columns.append(boss_id_col)
            if boss_name_col:
                merge_columns.append(boss_name_col)

            if len(merge_columns) > 1:  # Employee No 외에 다른 컬럼이 있을 경우만 병합
                self.df_incentive = pd.merge(
                    self.df_incentive,
                    self.df_basic[merge_columns],
                    left_on='employee_no',
                    right_on='Employee No',
                    how='left',
                    suffixes=('', '_basic')
                )

                # boss_id와 boss_name 설정
                if boss_id_col:
                    self.df_incentive['boss_id'] = self.df_incentive[boss_id_col].fillna('')
                else:
                    self.df_incentive['boss_id'] = ''

                if boss_name_col:
                    self.df_incentive['boss_name'] = self.df_incentive[boss_name_col].fillna('')
                else:
                    self.df_incentive['boss_name'] = ''
            else:
                # Boss 정보가 없는 경우 빈 값으로 설정
                self.df_incentive['boss_id'] = ''
                self.df_incentive['boss_name'] = ''

        # 3. 조건 평가
        if self.df_incentive is not None and not self.df_incentive.empty:
            condition_results = []
            for idx, row in self.df_incentive.iterrows():
                emp_conditions = self.evaluate_conditions(row.to_dict())
                condition_results.append(emp_conditions)

            self.df_incentive['condition_results'] = condition_results

        # 4. 통계 계산
        stats = self.calculate_statistics()

        # 5. employees 데이터에 필요한 필드 추가
        employees_data = self.df_incentive.to_dict('records') if self.df_incentive is not None else []

        # type, position, name, emp_no 등의 필드 매핑
        for emp in employees_data:
            # type 필드 매핑 (ROLE TYPE STD -> type)
            if 'type' not in emp and 'ROLE TYPE STD' in emp:
                emp['type'] = emp['ROLE TYPE STD']

            # position 필드 매핑
            if 'position' not in emp and 'FINAL QIP POSITION NAME CODE' in emp:
                emp['position'] = emp['FINAL QIP POSITION NAME CODE']

            # name 필드 매핑
            if 'name' not in emp and 'Full Name' in emp:
                emp['name'] = emp['Full Name']

            # emp_no 필드 매핑
            if 'emp_no' not in emp and 'Employee No' in emp:
                emp['emp_no'] = str(emp['Employee No']).zfill(9) if emp['Employee No'] else ''

        return {
            'employees': employees_data,
            'stats': stats,
            'translations': self.translations,
            'condition_matrix': self.condition_matrix,
            'excel_dashboard_data': self.excel_dashboard_data,
            'config': {
                'month': self.month,
                'year': self.year,
                'workingDays': self.working_days
            }
        }


def main():
    """테스트용 메인 함수"""
    calculator = IncentiveCalculator('september', 2025)
    data = calculator.process_all_data()

    print(f"✅ 데이터 처리 완료:")
    print(f"   - 직원 수: {len(data['employees'])}")
    print(f"   - 통계: {data['stats']}")


if __name__ == "__main__":
    main()