#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Playwright를 사용한 대시보드 기능 완전성 검증
원본과 모듈형 대시보드의 모든 기능을 비교 검증
"""

import asyncio
import os
from pathlib import Path


async def test_dashboard_features():
    """대시보드의 모든 기능을 테스트"""

    # Playwright 초기화
    print("\n" + "="*70)
    print("  🎭 Playwright 대시보드 기능 검증 시작")
    print("="*70 + "\n")

    # HTML 파일 경로
    dashboard_file = Path("output_files/Incentive_Dashboard_2025_09_Version_6.html").absolute()

    if not dashboard_file.exists():
        print("❌ 대시보드 파일을 찾을 수 없습니다. 먼저 생성해주세요.")
        return False

    file_url = f"file://{dashboard_file}"

    # 테스트 결과 저장
    test_results = {
        "tabs": {},
        "language": {},
        "search": {},
        "modals": {},
        "charts": {},
        "interactions": {}
    }

    try:
        # 브라우저 열기
        await mcp_playwright_browser_navigate(url=file_url)
        print(f"✅ 대시보드 열기: {file_url}")

        # 잠시 대기 (페이지 로드)
        await mcp_playwright_browser_wait_for(time=2)

        # 1. 탭 테스트
        print("\n📑 탭 기능 테스트:")
        tabs = ["summary", "position", "individual", "conditions", "orgchart"]

        for tab in tabs:
            # 스냅샷으로 탭 버튼 찾기
            snapshot = await mcp_playwright_browser_snapshot()

            # 탭 클릭 시도
            tab_found = False
            for element in snapshot:
                if tab in element.get('text', '').lower() or tab in element.get('id', '').lower():
                    try:
                        await mcp_playwright_browser_click(
                            element=f"{tab} tab",
                            ref=element['ref']
                        )
                        await mcp_playwright_browser_wait_for(time=0.5)
                        tab_found = True
                        test_results["tabs"][tab] = True
                        print(f"  ✅ {tab} 탭: 작동")
                        break
                    except:
                        pass

            if not tab_found:
                test_results["tabs"][tab] = False
                print(f"  ❌ {tab} 탭: 찾을 수 없음")

        # 2. 언어 변경 테스트
        print("\n🌐 언어 변경 테스트:")
        languages = ["한국어", "English", "Tiếng Việt"]

        for lang in languages:
            snapshot = await mcp_playwright_browser_snapshot()
            lang_found = False

            for element in snapshot:
                if lang in element.get('text', ''):
                    try:
                        await mcp_playwright_browser_click(
                            element=f"Language button: {lang}",
                            ref=element['ref']
                        )
                        await mcp_playwright_browser_wait_for(time=0.5)

                        # 언어 변경 확인
                        new_snapshot = await mcp_playwright_browser_snapshot()
                        lang_found = True
                        test_results["language"][lang] = True
                        print(f"  ✅ {lang}: 변경 가능")
                        break
                    except:
                        pass

            if not lang_found:
                test_results["language"][lang] = False
                print(f"  ❌ {lang}: 버튼 없음")

        # 3. Individual 탭 검색 테스트
        print("\n🔍 검색 및 필터 테스트:")

        # Individual 탭으로 이동
        snapshot = await mcp_playwright_browser_snapshot()
        for element in snapshot:
            if 'individual' in element.get('text', '').lower() or 'individual' in element.get('id', '').lower():
                try:
                    await mcp_playwright_browser_click(
                        element="Individual tab",
                        ref=element['ref']
                    )
                    await mcp_playwright_browser_wait_for(time=1)
                    break
                except:
                    pass

        # 검색창 찾기
        snapshot = await mcp_playwright_browser_snapshot()
        search_found = False
        for element in snapshot:
            if element.get('type') == 'textbox' and 'search' in element.get('id', '').lower():
                try:
                    await mcp_playwright_browser_type(
                        element="Search input",
                        ref=element['ref'],
                        text="617"
                    )
                    await mcp_playwright_browser_wait_for(time=0.5)
                    search_found = True
                    test_results["search"]["input"] = True
                    print("  ✅ 검색창: 작동")
                    break
                except:
                    pass

        if not search_found:
            test_results["search"]["input"] = False
            print("  ❌ 검색창: 찾을 수 없음")

        # 필터 선택 테스트
        snapshot = await mcp_playwright_browser_snapshot()
        filter_found = False
        for element in snapshot:
            if element.get('type') == 'combobox' and 'filter' in element.get('id', '').lower():
                try:
                    await mcp_playwright_browser_select_option(
                        element="Filter select",
                        ref=element['ref'],
                        values=["paid"]
                    )
                    await mcp_playwright_browser_wait_for(time=0.5)
                    filter_found = True
                    test_results["search"]["filter"] = True
                    print("  ✅ 필터: 작동")
                    break
                except:
                    pass

        if not filter_found:
            test_results["search"]["filter"] = False
            print("  ❌ 필터: 찾을 수 없음")

        # 4. 모달 테스트
        print("\n🪟 모달 테스트:")

        # 직원 상세 버튼 찾기
        snapshot = await mcp_playwright_browser_snapshot()
        modal_button_found = False

        for element in snapshot:
            # info-circle 아이콘이나 버튼 찾기
            if 'button' in element.get('type', '').lower() and element.get('ref'):
                try:
                    await mcp_playwright_browser_click(
                        element="Employee detail button",
                        ref=element['ref']
                    )
                    await mcp_playwright_browser_wait_for(time=1)

                    # 모달이 열렸는지 확인
                    new_snapshot = await mcp_playwright_browser_snapshot()
                    modal_opened = any('modal' in str(el).lower() for el in new_snapshot)

                    if modal_opened:
                        modal_button_found = True
                        test_results["modals"]["employee"] = True
                        print("  ✅ 직원 상세 모달: 작동")

                        # 모달 닫기
                        for el in new_snapshot:
                            if 'close' in el.get('text', '').lower() or '닫기' in el.get('text', ''):
                                try:
                                    await mcp_playwright_browser_click(
                                        element="Close modal",
                                        ref=el['ref']
                                    )
                                    break
                                except:
                                    pass
                        break
                except:
                    pass

        if not modal_button_found:
            test_results["modals"]["employee"] = False
            print("  ❌ 직원 상세 모달: 테스트 실패")

        # 5. 차트 존재 확인
        print("\n📊 차트 렌더링 테스트:")

        # Summary 탭으로 돌아가기
        snapshot = await mcp_playwright_browser_snapshot()
        for element in snapshot:
            if 'summary' in element.get('text', '').lower() or 'summary' in element.get('id', '').lower():
                try:
                    await mcp_playwright_browser_click(
                        element="Summary tab",
                        ref=element['ref']
                    )
                    await mcp_playwright_browser_wait_for(time=1)
                    break
                except:
                    pass

        # JavaScript로 차트 존재 확인
        chart_check = await mcp_playwright_browser_evaluate(
            function="() => { return document.querySelectorAll('canvas').length > 0; }"
        )

        if chart_check:
            test_results["charts"]["rendered"] = True
            print("  ✅ 차트: 렌더링됨")
        else:
            test_results["charts"]["rendered"] = False
            print("  ❌ 차트: 렌더링 안됨")

        # 6. 통계 카드 확인
        print("\n📈 통계 카드 테스트:")

        stats_check = await mcp_playwright_browser_evaluate(
            function="() => { return document.querySelectorAll('.stat-card').length; }"
        )

        if stats_check and stats_check > 0:
            test_results["interactions"]["stats"] = True
            print(f"  ✅ 통계 카드: {stats_check}개 발견")
        else:
            test_results["interactions"]["stats"] = False
            print("  ❌ 통계 카드: 찾을 수 없음")

        # 7. 데이터 테이블 확인
        print("\n📋 데이터 테이블 테스트:")

        # Position 탭으로 이동
        snapshot = await mcp_playwright_browser_snapshot()
        for element in snapshot:
            if 'position' in element.get('text', '').lower() or 'position' in element.get('id', '').lower():
                try:
                    await mcp_playwright_browser_click(
                        element="Position tab",
                        ref=element['ref']
                    )
                    await mcp_playwright_browser_wait_for(time=1)
                    break
                except:
                    pass

        table_check = await mcp_playwright_browser_evaluate(
            function="() => { return document.querySelectorAll('table tbody tr').length; }"
        )

        if table_check and table_check > 0:
            test_results["interactions"]["tables"] = True
            print(f"  ✅ 데이터 테이블: {table_check}개 행 발견")
        else:
            test_results["interactions"]["tables"] = False
            print("  ❌ 데이터 테이블: 데이터 없음")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        return False

    finally:
        # 브라우저 닫기
        try:
            await mcp_playwright_browser_close()
        except:
            pass

    # 결과 요약
    print("\n" + "="*70)
    print("  📊 테스트 결과 요약")
    print("="*70)

    total_tests = 0
    passed_tests = 0

    for category, results in test_results.items():
        if results:
            print(f"\n{category.upper()}:")
            for test, passed in results.items():
                total_tests += 1
                if passed:
                    passed_tests += 1
                    print(f"  ✅ {test}")
                else:
                    print(f"  ❌ {test}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\n전체 테스트: {total_tests}개")
    print(f"성공: {passed_tests}개")
    print(f"실패: {total_tests - passed_tests}개")
    print(f"성공률: {success_rate:.1f}%")

    if success_rate >= 90:
        print("\n✅ 대시보드가 원본과 동일한 기능을 제공합니다!")
    elif success_rate >= 70:
        print("\n⚠️ 일부 기능이 누락되었습니다.")
    else:
        print("\n❌ 많은 기능이 작동하지 않습니다.")

    print("="*70 + "\n")

    return test_results


# MCP Playwright 함수들 (실제로는 MCP를 통해 호출됨)
async def mcp_playwright_browser_navigate(url):
    """브라우저 열기"""
    # 실제로는 MCP의 playwright 서버를 통해 호출
    pass

async def mcp_playwright_browser_snapshot():
    """페이지 스냅샷"""
    pass

async def mcp_playwright_browser_click(element, ref):
    """요소 클릭"""
    pass

async def mcp_playwright_browser_type(element, ref, text):
    """텍스트 입력"""
    pass

async def mcp_playwright_browser_select_option(element, ref, values):
    """옵션 선택"""
    pass

async def mcp_playwright_browser_wait_for(time):
    """대기"""
    pass

async def mcp_playwright_browser_evaluate(function):
    """JavaScript 실행"""
    pass

async def mcp_playwright_browser_close():
    """브라우저 닫기"""
    pass


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_dashboard_features())