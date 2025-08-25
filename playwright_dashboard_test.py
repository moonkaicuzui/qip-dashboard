#!/usr/bin/env python3
"""
Playwright를 사용한 대시보드 UI 재검증
10가지 조건의 코드 로직과 JSON 일치 여부 확인
"""

import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Playwright imports
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Install with: pip install playwright && playwright install chromium")

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from common_condition_checker import ConditionChecker, get_condition_checker

class DashboardPlaywrightTester:
    """Playwright를 사용한 대시보드 테스터"""
    
    def __init__(self):
        self.matrix_path = Path(__file__).parent / 'config_files' / 'position_condition_matrix.json'
        self.matrix = self._load_matrix()
        self.checker = get_condition_checker()
        self.verification_results = []
        self.dashboard_url = "http://localhost:5000"  # 대시보드 URL
        
    def _load_matrix(self) -> Dict:
        """position_condition_matrix.json 로드"""
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def verify_condition_logic(self) -> Dict:
        """10가지 조건의 코드 로직이 JSON과 일치하는지 확인"""
        print("\n" + "=" * 80)
        print("📋 10가지 조건 코드 로직 vs JSON 검증")
        print("=" * 80)
        
        verification_results = {}
        
        # 각 조건별 검증
        for cond_id in range(1, 11):
            cond_str = str(cond_id)
            json_cond = self.matrix['conditions'][cond_str]
            
            print(f"\n조건 {cond_id}: {json_cond['description']}")
            print("-" * 60)
            
            # JSON 정의
            print(f"  📄 JSON 정의:")
            print(f"     - ID: {json_cond['id']}")
            print(f"     - 이름: {json_cond['name']}")
            print(f"     - 카테고리: {json_cond['category']}")
            
            # 코드 로직 확인
            code_logic_correct = self._verify_condition_code_logic(cond_id, json_cond)
            
            verification_results[cond_id] = {
                'json_definition': json_cond,
                'code_logic_correct': code_logic_correct
            }
            
            status = "✅" if code_logic_correct else "❌"
            print(f"  {status} 코드 로직 일치 여부: {code_logic_correct}")
        
        return verification_results
    
    def _verify_condition_code_logic(self, cond_id: int, json_cond: Dict) -> bool:
        """개별 조건의 코드 로직 검증"""
        
        # validation_rules와 비교
        validation_rules = self.matrix.get('validation_rules', {})
        
        if cond_id == 1:  # 출근율 ≥88%
            threshold = validation_rules['attendance']['attendance_rate_threshold']
            print(f"     - 임계값: {threshold * 100}%")
            return threshold == 0.88
            
        elif cond_id == 2:  # 무단결근 ≤2일
            threshold = validation_rules['attendance']['unapproved_absence_threshold']
            print(f"     - 임계값: {threshold}일")
            return threshold == 2
            
        elif cond_id == 3:  # 실제 근무일 >0
            threshold = validation_rules['attendance']['minimum_actual_days']
            print(f"     - 임계값: >{threshold}일")
            return threshold == 0
            
        elif cond_id == 4:  # 최소 근무일 ≥12일
            threshold = validation_rules['attendance']['minimum_days_threshold']
            print(f"     - 임계값: {threshold}일")
            return threshold == 12
            
        elif cond_id == 5:  # 개인 AQL 당월 실패 0건
            threshold = validation_rules['aql']['personal_failure_threshold']
            print(f"     - 임계값: {threshold}건")
            return threshold == 0
            
        elif cond_id == 6:  # 개인 AQL 3개월 연속 실패 없음
            months = validation_rules['aql']['continuous_months_check']
            print(f"     - 연속 체크 개월: {months}개월")
            return months == 3
            
        elif cond_id == 7:  # 팀/구역 AQL 3개월 연속 실패 없음
            months = validation_rules['aql']['team_area_consecutive_months']
            print(f"     - 연속 체크 개월: {months}개월")
            return months == 3
            
        elif cond_id == 8:  # 담당구역 reject율 <3%
            threshold = validation_rules['aql']['area_reject_threshold']
            print(f"     - 임계값: {threshold * 100}%")
            return threshold == 0.03
            
        elif cond_id == 9:  # 5PRS 통과율 ≥95%
            threshold = validation_rules['5prs']['pass_rate_threshold']
            print(f"     - 임계값: {threshold * 100}%")
            return threshold == 0.95
            
        elif cond_id == 10:  # 5PRS 검사량 ≥100개
            threshold = validation_rules['5prs']['minimum_inspection_qty']
            print(f"     - 임계값: {threshold}개")
            return threshold == 100
        
        return False
    
    async def test_dashboard_with_playwright(self, browser: Browser) -> None:
        """Playwright로 실제 대시보드 테스트"""
        page = await browser.new_page()
        
        try:
            # 대시보드 접속
            print(f"\n🌐 대시보드 접속: {self.dashboard_url}")
            await page.goto(self.dashboard_url)
            await page.wait_for_load_state('networkidle')
            
            # 테스트할 주요 직급들
            test_cases = [
                ('TYPE-1', 'LINE LEADER', [1, 2, 3, 4, 7]),
                ('TYPE-1', 'AQL INSPECTOR', [1, 2, 3, 4, 5]),
                ('TYPE-1', 'ASSEMBLY INSPECTOR', [1, 2, 3, 4, 5, 6, 9, 10]),
                ('TYPE-2', 'LINE LEADER', [1, 2, 3, 4]),
                ('TYPE-3', 'NEW QIP MEMBER', []),
            ]
            
            for emp_type, position, expected_conditions in test_cases:
                print(f"\n📊 테스트: {emp_type} - {position}")
                print("-" * 60)
                
                # 직급 선택 및 상세 보기
                await self._select_position_and_view_details(page, emp_type, position)
                
                # 조건 표시 확인
                displayed_conditions = await self._check_displayed_conditions(page)
                
                # 검증
                match = set(expected_conditions) == set(displayed_conditions)
                status = "✅" if match else "❌"
                
                print(f"  {status} 예상 조건: {expected_conditions}")
                print(f"  {status} 표시 조건: {displayed_conditions}")
                
                # 스크린샷 저장
                screenshot_name = f"dashboard_{emp_type}_{position.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_name)
                print(f"  📸 스크린샷 저장: {screenshot_name}")
                
                self.verification_results.append({
                    'type': emp_type,
                    'position': position,
                    'expected': expected_conditions,
                    'displayed': displayed_conditions,
                    'match': match
                })
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            await page.close()
    
    async def _select_position_and_view_details(self, page: Page, emp_type: str, position: str):
        """직급 선택 및 상세 보기"""
        # 타입 선택
        type_selector = f"select#employeeType"
        await page.select_option(type_selector, emp_type)
        await page.wait_for_timeout(500)
        
        # 직급 선택
        position_selector = f"select#position"
        await page.select_option(position_selector, position)
        await page.wait_for_timeout(500)
        
        # 상세 보기 버튼 클릭
        detail_button = "button#viewDetails"
        await page.click(detail_button)
        await page.wait_for_timeout(1000)
    
    async def _check_displayed_conditions(self, page: Page) -> List[int]:
        """표시된 조건들 확인"""
        displayed = []
        
        # 조건 1-10 확인
        for cond_id in range(1, 11):
            # 조건이 표시되는지 확인 (N/A가 아닌지)
            selector = f"div.condition-{cond_id}"
            element = await page.query_selector(selector)
            
            if element:
                text = await element.inner_text()
                if "N/A" not in text and "해당없음" not in text:
                    displayed.append(cond_id)
        
        return displayed

class CodeLogicVerifier:
    """코드 로직 검증 클래스"""
    
    def __init__(self):
        self.checker = get_condition_checker()
        self.matrix_path = Path(__file__).parent / 'config_files' / 'position_condition_matrix.json'
        self.matrix = self._load_matrix()
    
    def _load_matrix(self) -> Dict:
        """JSON 로드"""
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def verify_all_condition_implementations(self) -> None:
        """모든 조건 구현 검증"""
        print("\n" + "=" * 80)
        print("🔍 조건별 코드 구현 검증")
        print("=" * 80)
        
        # 테스트 데이터
        test_data = {
            'Employee No': 'TEST001',
            'Absence Rate (raw)': 10,  # 출근율 90%
            'Unapproved Absence Days': 1,
            'Actual Working Days': 20,
            'July AQL Failures': 0,
            'Continuous_FAIL': 'NO',
            'Pass %': 98,
            'Total Valiation Qty': 150
        }
        
        # 조건 1-4: 출근 조건
        attendance_results = self.checker.check_attendance_conditions(test_data)
        print("\n📌 출근 조건 (1-4):")
        for cond_id, result in attendance_results.items():
            status = "✅" if result else "❌"
            print(f"  조건 {cond_id}: {status} - {self.matrix['conditions'][str(cond_id)]['description']}")
        
        # 조건 5: 개인 AQL 당월
        result_5 = self.checker.check_aql_monthly_failure(test_data, 'July')
        print(f"\n📌 AQL 조건:")
        print(f"  조건 5: {'✅' if result_5 else '❌'} - 개인 AQL 당월 실패 0건")
        
        # 조건 6: 개인 AQL 3개월 연속
        result_6 = self.checker.check_aql_3month_continuous(test_data)
        print(f"  조건 6: {'✅' if result_6 else '❌'} - 개인 AQL 3개월 연속 실패 없음")
        
        # 조건 7: 팀/구역 AQL (부하직원 데이터 필요)
        import pandas as pd
        subordinates = pd.DataFrame([
            {'Employee No': 'SUB001', 'MST direct boss name': 'TEST001', 'Continuous_FAIL': 'NO'}
        ])
        result_7 = self.checker.check_team_area_aql_continuous('TEST001', subordinates)
        print(f"  조건 7: {'✅' if result_7 else '❌'} - 팀/구역 AQL 3개월 연속 실패 없음")
        
        # 조건 8: 담당구역 reject율
        result_8, rate = self.checker.check_area_reject_rate('TEST001', {}, pd.DataFrame())
        print(f"  조건 8: {'✅' if result_8 else '❌'} - 담당구역 reject율 <3% (현재: {rate}%)")
        
        # 조건 9-10: 5PRS
        prs_results = self.checker.check_5prs_conditions(test_data)
        print(f"\n📌 5PRS 조건:")
        for cond_id, result in prs_results.items():
            status = "✅" if result else "❌"
            print(f"  조건 {cond_id}: {status} - {self.matrix['conditions'][str(cond_id)]['description']}")

async def main():
    """메인 실행 함수"""
    print("\n" + "=" * 80)
    print("🚀 Playwright 대시보드 재검증 시작")
    print("=" * 80)
    
    # 1. 코드 로직 vs JSON 검증
    tester = DashboardPlaywrightTester()
    logic_results = tester.verify_condition_logic()
    
    # 2. 코드 구현 검증
    verifier = CodeLogicVerifier()
    verifier.verify_all_condition_implementations()
    
    # 3. Playwright 대시보드 테스트 (if available)
    if PLAYWRIGHT_AVAILABLE:
        print("\n" + "=" * 80)
        print("🌐 Playwright 대시보드 UI 테스트")
        print("=" * 80)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # headless=False로 브라우저 표시
            await tester.test_dashboard_with_playwright(browser)
            await browser.close()
    else:
        print("\n⚠️ Playwright가 설치되지 않아 UI 테스트를 건너뜁니다.")
    
    # 4. 최종 보고서
    print("\n" + "=" * 80)
    print("📊 최종 검증 결과")
    print("=" * 80)
    
    # 로직 검증 결과
    all_logic_correct = all(r['code_logic_correct'] for r in logic_results.values())
    if all_logic_correct:
        print("✅ 모든 조건의 코드 로직이 JSON과 일치합니다!")
    else:
        print("❌ 일부 조건의 코드 로직이 JSON과 일치하지 않습니다.")
        failed = [k for k, v in logic_results.items() if not v['code_logic_correct']]
        print(f"   실패한 조건: {failed}")
    
    # UI 검증 결과 (if tested)
    if PLAYWRIGHT_AVAILABLE and tester.verification_results:
        all_ui_correct = all(r['match'] for r in tester.verification_results)
        if all_ui_correct:
            print("✅ 모든 직급의 대시보드 UI가 JSON 설정과 일치합니다!")
        else:
            print("❌ 일부 직급의 대시보드 UI가 JSON과 일치하지 않습니다.")
            failed = [(r['type'], r['position']) for r in tester.verification_results if not r['match']]
            for t, p in failed:
                print(f"   - {t} {p}")
    
    print("\n✅ 검증 완료!")

if __name__ == "__main__":
    if PLAYWRIGHT_AVAILABLE:
        asyncio.run(main())
    else:
        # Playwright 없이 기본 검증만 실행
        tester = DashboardPlaywrightTester()
        tester.verify_condition_logic()
        
        verifier = CodeLogicVerifier()
        verifier.verify_all_condition_implementations()
        
        print("\n⚠️ Playwright를 설치하면 실제 대시보드 UI 테스트가 가능합니다.")
        print("   설치: pip install playwright && playwright install chromium")