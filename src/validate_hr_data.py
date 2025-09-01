#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HR 데이터 검증 스크립트
인센티브 CSV 파일과 team_structure_updated.json 간의 데이터 불일치를 검증합니다.
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import warnings
warnings.filterwarnings('ignore')

class HRDataValidator:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.errors = []
        self.warnings = []
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 파일 경로 설정
        self.csv_path = os.path.join(self.base_path, 'input_files', f'{year}년 {month}월 인센티브 지급 세부 정보.csv')
        self.json_path = os.path.join(self.base_path, 'HR info', 'team_structure_updated.json')
        self.output_dir = os.path.join(self.base_path, 'error_review')
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 데이터 로드
        self.csv_data = None
        self.json_data = None
        
    def load_data(self):
        """CSV와 JSON 데이터를 로드합니다."""
        try:
            # CSV 데이터 로드
            print(f"📂 CSV 파일 로드 중: {self.csv_path}")
            self.csv_data = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            print(f"   ✅ {len(self.csv_data)}명의 직원 데이터 로드 완료")
            
            # JSON 데이터 로드
            print(f"📂 JSON 파일 로드 중: {self.json_path}")
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            print(f"   ✅ {len(self.json_data['positions'])}개의 position 정의 로드 완료")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ 파일을 찾을 수 없습니다: {e}")
            return False
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {e}")
            return False
    
    def validate_position_mapping(self):
        """Position 매핑을 검증합니다."""
        print("\n🔍 Position 매핑 검증 중...")
        
        # JSON에서 position 매핑 생성
        json_positions = {}
        for pos in self.json_data['positions']:
            key = (
                pos.get('position_1st', '').strip().upper(),
                pos.get('position_2nd', '').strip().upper(),
                pos.get('position_3rd', '').strip().upper()
            )
            json_positions[key] = {
                'final_code': pos.get('final_code', ''),
                'team_name': pos.get('team_name', ''),
                'role_category': pos.get('role_category', ''),
                'role_type': pos.get('role_type', '')
            }
        
        # CSV 데이터 검증
        mismatches = []
        for idx, row in self.csv_data.iterrows():
            csv_key = (
                str(row.get('QIP POSITION 1ST  NAME', '')).strip().upper(),
                str(row.get('QIP POSITION 2ND  NAME', '')).strip().upper(),
                str(row.get('QIP POSITION 3RD  NAME', '')).strip().upper()
            )
            
            employee_info = {
                'Employee No': row.get('Employee No', ''),
                'Full Name': row.get('Full Name', ''),
                'Position 1st': csv_key[0],
                'Position 2nd': csv_key[1],
                'Position 3rd': csv_key[2],
                'CSV_Final_Code': row.get('FINAL QIP POSITION NAME CODE', ''),
                'CSV_Role_Type': row.get('ROLE TYPE STD', ''),
                'Error_Type': '',
                'Expected_Values': '',
                'Actual_Values': '',
                'Reason of Review Required': ''
            }
            
            if csv_key not in json_positions:
                # Position이 JSON에 없는 경우
                employee_info['Error_Type'] = 'Position Not Found in JSON'
                employee_info['Expected_Values'] = 'Position definition in JSON'
                employee_info['Actual_Values'] = f"{csv_key[0]} / {csv_key[1]} / {csv_key[2]}"
                employee_info['Reason of Review Required'] = 'Position 조합이 team_structure_updated.json에 정의되지 않음. 신규 직책이거나 오타 가능성'
                mismatches.append(employee_info)
            else:
                # Position은 있지만 값이 다른 경우
                json_info = json_positions[csv_key]
                errors = []
                
                # Final Code 검증
                if str(row.get('FINAL QIP POSITION NAME CODE', '')).strip() != json_info['final_code']:
                    errors.append('Final Code Mismatch')
                    employee_info['Expected_Values'] = f"Final Code: {json_info['final_code']}"
                    employee_info['Actual_Values'] = f"Final Code: {row.get('FINAL QIP POSITION NAME CODE', '')}"
                    employee_info['Reason of Review Required'] = 'Final Code가 JSON 정의와 불일치. 코드 업데이트 필요'
                
                # Role Type 검증
                if str(row.get('ROLE TYPE STD', '')).strip() != json_info['role_type']:
                    errors.append('Role Type Mismatch')
                    if employee_info['Expected_Values']:
                        employee_info['Expected_Values'] += f", Role Type: {json_info['role_type']}"
                        employee_info['Actual_Values'] += f", Role Type: {row.get('ROLE TYPE STD', '')}"
                        if employee_info['Reason of Review Required']:
                            employee_info['Reason of Review Required'] += ' / Role Type(TYPE-1/2/3) 분류 불일치. 인센티브 계산에 영향'
                        else:
                            employee_info['Reason of Review Required'] = 'Role Type(TYPE-1/2/3) 분류 불일치. 인센티브 계산에 영향'
                    else:
                        employee_info['Expected_Values'] = f"Role Type: {json_info['role_type']}"
                        employee_info['Actual_Values'] = f"Role Type: {row.get('ROLE TYPE STD', '')}"
                        employee_info['Reason of Review Required'] = 'Role Type(TYPE-1/2/3) 분류 불일치. 인센티브 계산에 영향'
                
                if errors:
                    employee_info['Error_Type'] = ', '.join(errors)
                    mismatches.append(employee_info)
        
        print(f"   ✅ 검증 완료: {len(mismatches)}개의 불일치 발견")
        return mismatches
    
    def validate_role_type_consistency(self):
        """동일 position에 대한 Role Type 일관성을 검증합니다."""
        print("\n🔍 Role Type 일관성 검증 중...")
        
        position_types = {}
        inconsistencies = []
        
        for idx, row in self.csv_data.iterrows():
            position_1st = str(row.get('QIP POSITION 1ST  NAME', '')).strip().upper()
            role_type = str(row.get('ROLE TYPE STD', '')).strip()
            
            if position_1st not in position_types:
                position_types[position_1st] = set()
            
            position_types[position_1st].add(role_type)
        
        # 동일 position_1st에 여러 role_type이 있는 경우 찾기
        for position, types in position_types.items():
            if len(types) > 1:
                # 해당 position의 모든 직원 찾기
                affected_employees = self.csv_data[
                    self.csv_data['QIP POSITION 1ST  NAME'].str.strip().str.upper() == position
                ]
                
                for idx, row in affected_employees.iterrows():
                    inconsistencies.append({
                        'Employee No': row.get('Employee No', ''),
                        'Full Name': row.get('Full Name', ''),
                        'Position 1st': position,
                        'Current Role Type': row.get('ROLE TYPE STD', ''),
                        'All Role Types for Position': ', '.join(sorted(types)),
                        'Issue': 'Multiple Role Types for Same Position',
                        'Reason of Review Required': f'동일 직책({position})에 여러 TYPE({", ".join(sorted(types))})이 혼재. 통일 필요'
                    })
        
        print(f"   ✅ 검증 완료: {len(inconsistencies)}개의 일관성 문제 발견")
        return inconsistencies
    
    def validate_duplicate_codes(self):
        """중복 Final Code를 검증합니다."""
        print("\n🔍 중복 Final Code 검증 중...")
        
        code_positions = {}
        duplicates = []
        
        # JSON에서 Final Code별 position 수집
        for pos in self.json_data['positions']:
            code = pos.get('final_code', '')
            if code:
                if code not in code_positions:
                    code_positions[code] = []
                code_positions[code].append({
                    'position_1st': pos.get('position_1st', ''),
                    'position_2nd': pos.get('position_2nd', ''),
                    'position_3rd': pos.get('position_3rd', ''),
                    'team': pos.get('team_name', ''),
                    'role_type': pos.get('role_type', '')
                })
        
        # 중복 코드 찾기
        for code, positions in code_positions.items():
            if len(positions) > 1:
                for pos in positions:
                    duplicates.append({
                        'Final Code': code,
                        'Position 1st': pos['position_1st'],
                        'Position 2nd': pos['position_2nd'],
                        'Position 3rd': pos['position_3rd'],
                        'Team': pos['team'],
                        'Role Type': pos['role_type'],
                        'Issue': f'Code used by {len(positions)} positions',
                        'Reason of Review Required': f'Final Code({code})가 {len(positions)}개 직책에서 중복 사용. 고유 코드 재할당 필요'
                    })
        
        print(f"   ✅ 검증 완료: {len(duplicates)}개의 중복 코드 발견")
        return duplicates
    
    def save_to_excel(self, mismatches, inconsistencies, duplicates):
        """검증 결과를 Excel 파일로 저장합니다."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f'hr_data_validation_{self.year}_{self.month}_{timestamp}.xlsx')
        
        print(f"\n💾 Excel 파일 생성 중: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 1. Position 매핑 불일치
            if mismatches:
                df_mismatches = pd.DataFrame(mismatches)
                df_mismatches.to_excel(writer, sheet_name='Position Mismatches', index=False)
                
                # 스타일 적용
                worksheet = writer.sheets['Position Mismatches']
                self._apply_excel_style(worksheet, len(mismatches))
            
            # 2. Role Type 일관성 문제
            if inconsistencies:
                df_inconsistencies = pd.DataFrame(inconsistencies)
                df_inconsistencies.to_excel(writer, sheet_name='Role Type Inconsistencies', index=False)
                
                worksheet = writer.sheets['Role Type Inconsistencies']
                self._apply_excel_style(worksheet, len(inconsistencies))
            
            # 3. 중복 Final Code
            if duplicates:
                df_duplicates = pd.DataFrame(duplicates)
                df_duplicates.to_excel(writer, sheet_name='Duplicate Final Codes', index=False)
                
                worksheet = writer.sheets['Duplicate Final Codes']
                self._apply_excel_style(worksheet, len(duplicates))
            
            # 4. 요약 시트
            summary_data = {
                'Validation Type': [
                    'Position Mismatches',
                    'Role Type Inconsistencies',
                    'Duplicate Final Codes',
                    'Total Issues'
                ],
                'Count': [
                    len(mismatches),
                    len(inconsistencies),
                    len(duplicates),
                    len(mismatches) + len(inconsistencies) + len(duplicates)
                ],
                'Description': [
                    'CSV와 JSON 간 position 정보 불일치',
                    '동일 position에 여러 role type 존재',
                    '동일 final code가 여러 position에 사용',
                    '전체 발견된 문제 수'
                ],
                'Impact on Dashboard': [
                    '팀 배정 오류, Team Unidentified로 표시됨',
                    '인센티브 금액 계산 오류 가능성',
                    '데이터 매핑 혼란, 보고서 정확도 저하',
                    '대시보드 신뢰성 저하'
                ],
                'Recommended Action': [
                    'team_structure_updated.json에 누락된 position 추가',
                    '동일 직책의 Role Type 통일 (TYPE-1/2/3 중 선택)',
                    '각 position에 고유한 Final Code 재할당',
                    '데이터 정합성 검토 후 재실행'
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            worksheet = writer.sheets['Summary']
            self._apply_excel_style(worksheet, len(summary_data['Validation Type']))
        
        print(f"   ✅ Excel 파일 저장 완료")
        return output_file
    
    def _apply_excel_style(self, worksheet, row_count):
        """Excel 워크시트에 스타일을 적용합니다."""
        # 헤더 스타일
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        # 테두리 스타일
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 헤더 행 스타일 적용
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
        
        # 데이터 행 스타일 적용
        for row in worksheet.iter_rows(min_row=2, max_row=row_count+1):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='left', vertical='center')
        
        # 열 너비 자동 조정
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def run_validation(self):
        """전체 검증 프로세스를 실행합니다."""
        print(f"\n{'='*60}")
        print(f"HR 데이터 검증 시작 - {self.year}년 {self.month}월")
        print(f"{'='*60}")
        
        # 데이터 로드
        if not self.load_data():
            return False
        
        # 검증 수행
        mismatches = self.validate_position_mapping()
        inconsistencies = self.validate_role_type_consistency()
        duplicates = self.validate_duplicate_codes()
        
        # 결과 저장
        if mismatches or inconsistencies or duplicates:
            output_file = self.save_to_excel(mismatches, inconsistencies, duplicates)
            
            print(f"\n📊 검증 결과 요약:")
            print(f"   • Position 불일치: {len(mismatches)}건")
            print(f"   • Role Type 일관성 문제: {len(inconsistencies)}건")
            print(f"   • 중복 Final Code: {len(duplicates)}건")
            print(f"   • 총 문제: {len(mismatches) + len(inconsistencies) + len(duplicates)}건")
            print(f"\n📄 상세 결과는 다음 파일을 확인하세요:")
            print(f"   {output_file}")
            
            return True
        else:
            print(f"\n✅ 모든 데이터가 정상입니다. 불일치 사항이 없습니다.")
            return True

def main():
    """메인 실행 함수"""
    # 명령행 인자 처리
    if len(sys.argv) > 2:
        month = int(sys.argv[1])
        year = int(sys.argv[2])
    else:
        # 기본값: 현재 월
        from datetime import datetime
        now = datetime.now()
        month = now.month
        year = now.year
    
    # 검증 실행
    validator = HRDataValidator(month, year)
    success = validator.run_validation()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()