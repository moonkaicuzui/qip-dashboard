#!/usr/bin/env python3
"""
10개 KPI 카드 종합 검증 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 10개 KPI 카드 종합 검증 테스트\n")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("\n📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # 요약 및 시스템 검증 탭 클릭
    print("📊 요약 및 시스템 검증 탭 열기...")
    page.click("#tabValidation")
    time.sleep(2)

    print("\n" + "=" * 70)
    print("KPI 카드 데이터 추출")
    print("=" * 70)

    try:
        # KPI 카드 정보 추출
        kpi_cards = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.kpi-card');
                return Array.from(cards).map(card => {
                    const title = card.querySelector('.kpi-label')?.textContent || '';
                    const value = card.querySelector('.kpi-value')?.textContent || '';
                    const modal = card.getAttribute('onclick');

                    return {
                        title: title.trim(),
                        value: value.trim(),
                        hasModal: modal !== null && modal.includes('showValidationModal')
                    };
                });
            }
        """)

        print(f"\n총 KPI 카드 수: {len(kpi_cards)}개\n")

        for i, card in enumerate(kpi_cards, 1):
            print(f"{i:2d}. {card['title']}")
            print(f"    값: {card['value']}")
            print(f"    모달: {'✅ 있음' if card['hasModal'] else '❌ 없음'}")
            print()

        # 각 KPI 카드 모달 테스트
        print("\n" + "=" * 70)
        print("KPI 카드 모달 테스트")
        print("=" * 70)

        modal_tests = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

        for i, card in enumerate(kpi_cards, 1):
            if not card['hasModal']:
                continue

            print(f"\n{i}. {card['title']} 모달 테스트...")

            try:
                # 모달 열기
                modal_selector = f"document.querySelectorAll('.kpi-card')[{i-1}]"
                page.evaluate(f"{modal_selector}.click()")
                time.sleep(1.5)

                # 모달 확인 (Bootstrap .modal.show 또는 inline display:block 모두 지원)
                modal_check = page.evaluate("""
                    () => {
                        // Bootstrap modal with .show class
                        let modal = document.querySelector('.modal.show');

                        // Fallback: modal with display:block (consecutiveAqlFailModal 등)
                        if (!modal) {
                            const modals = document.querySelectorAll('.modal');
                            for (const m of modals) {
                                if (m.style.display === 'block') {
                                    modal = m;
                                    break;
                                }
                            }
                        }

                        if (!modal) return { visible: false };

                        const title = modal.querySelector('.modal-title, h2, h3, h5')?.textContent || '';
                        const body = modal.querySelector('.modal-body');
                        const table = body?.querySelector('table') || modal.querySelector('table');
                        const rows = table?.querySelectorAll('tr');

                        return {
                            visible: true,
                            title: title.trim(),
                            hasTable: table !== null,
                            rowCount: rows ? rows.length : 0,
                            hasCodeIssue: (body?.innerText || modal.innerText || '').includes('${') || false
                        };
                    }
                """)

                if modal_check['visible']:
                    if modal_check['hasCodeIssue']:
                        print(f"   ❌ 모달에 코드 노출 발견 (${{...}})")
                        modal_tests['failed'] += 1
                        modal_tests['errors'].append(f"{card['title']}: 코드 노출")
                    else:
                        print(f"   ✅ 모달 정상 표시")
                        print(f"      - 제목: {modal_check['title'][:50]}...")
                        print(f"      - 테이블: {'있음' if modal_check['hasTable'] else '없음'}")
                        if modal_check['hasTable']:
                            print(f"      - 행 수: {modal_check['rowCount']}")
                        modal_tests['passed'] += 1
                else:
                    print(f"   ❌ 모달이 표시되지 않음")
                    modal_tests['failed'] += 1
                    modal_tests['errors'].append(f"{card['title']}: 모달 미표시")

                # 모달 닫기
                page.evaluate("""
                    () => {
                        const modal = document.querySelector('.modal.show');
                        if (modal) {
                            const closeBtn = modal.querySelector('.btn-close');
                            if (closeBtn) closeBtn.click();
                        }
                    }
                """)
                time.sleep(0.5)

            except Exception as e:
                print(f"   ❌ 테스트 오류: {e}")
                modal_tests['failed'] += 1
                modal_tests['errors'].append(f"{card['title']}: {str(e)[:50]}")

        # 언어 전환 테스트
        print("\n" + "=" * 70)
        print("언어 전환 테스트")
        print("=" * 70)

        languages = ['en', 'vi', 'ko']
        lang_test_results = {
            'passed': 0,
            'failed': 0
        }

        for lang in languages:
            print(f"\n🌐 {lang.upper()} 언어로 전환...")

            try:
                # 언어 버튼이 Validation 탭에서 보이는지 확인
                # 언어 버튼은 헤더에 있으므로 항상 접근 가능
                page.evaluate(f"() => document.querySelector('[data-lang=\"{lang}\"]')?.click()")
                time.sleep(1)

                # 현재 언어 확인
                current_lang = page.evaluate("() => window.currentLanguage || 'ko'")

                if current_lang == lang:
                    print(f"   ✅ 언어 전환 성공: {current_lang}")
                    lang_test_results['passed'] += 1
                else:
                    print(f"   ⚠️  언어 불일치: 예상={lang}, 실제={current_lang}")
                    lang_test_results['failed'] += 1

            except Exception as e:
                print(f"   ❌ 언어 전환 오류: {e}")
                lang_test_results['failed'] += 1

        # JavaScript 오류 확인
        print("\n" + "=" * 70)
        print("JavaScript 오류 확인")
        print("=" * 70)

        if page_errors:
            print(f"\n❌ JavaScript 오류 발견 ({len(page_errors)}개):")
            for err in page_errors[:5]:
                print(f"   - {err}")
        else:
            print("\n✅ JavaScript 오류 없음")

        # 최종 결과 요약
        print("\n" + "=" * 70)
        print("최종 결과 요약")
        print("=" * 70)

        print(f"\n📊 KPI 카드:")
        print(f"   - 총 카드 수: {len(kpi_cards)}개")
        print(f"   - 모달 있는 카드: {sum(1 for c in kpi_cards if c['hasModal'])}개")

        print(f"\n✅ 모달 테스트:")
        print(f"   - 통과: {modal_tests['passed']}개")
        print(f"   - 실패: {modal_tests['failed']}개")
        if modal_tests['errors']:
            print(f"   오류 목록:")
            for err in modal_tests['errors']:
                print(f"      - {err}")

        print(f"\n🌐 언어 전환 테스트:")
        print(f"   - 통과: {lang_test_results['passed']}/{len(languages)}")
        print(f"   - 실패: {lang_test_results['failed']}/{len(languages)}")

        print(f"\n🐛 JavaScript 오류:")
        print(f"   - 오류 수: {len(page_errors)}개")

        # 전체 성공 여부
        all_passed = (
            len(kpi_cards) == 10 and
            modal_tests['failed'] == 0 and
            lang_test_results['failed'] == 0 and
            len(page_errors) == 0
        )

        if all_passed:
            print("\n🎉 모든 테스트 통과!")
        else:
            print("\n⚠️  일부 테스트 실패")

    except Exception as e:
        print(f"\n❌ 테스트 실행 오류: {e}")
        import traceback
        traceback.print_exc()

    browser.close()

print("\n✅ 테스트 완료")
