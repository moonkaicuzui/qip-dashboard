#!/usr/bin/env python3
"""
모달 템플릿 리터럴 빠른 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 모달 템플릿 리터럴 빠른 테스트\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    page.click("#tabOrgChart")
    time.sleep(2)

    print("\n📊 모달 테스트:\n")

    # 직원 카드 수 확인
    card_count = page.evaluate("() => document.querySelectorAll('.org-card').length")
    print(f"  발견된 직원 카드: {card_count}개\n")

    if card_count > 0:
        # 첫 번째 직원의 모달 열기
        try:
            first_emp = page.evaluate("""
                () => {
                    const card = document.querySelector('.org-card');
                    return card ? {
                        empNo: card.getAttribute('data-emp-no'),
                        name: card.querySelector('.card-title')?.textContent,
                        position: card.querySelector('.position-badge')?.textContent
                    } : null;
                }
            """)

            print(f"  first_emp 결과: {first_emp}\n")

            if first_emp:
                print(f"  테스트 대상: {first_emp['name']} ({first_emp['position']})")

                # 모달 열기
                page.evaluate(f"() => showIncentiveModal('{first_emp['empNo']}')")
                time.sleep(1)

                # 모달 내용 확인
                modal_check = page.evaluate("""
                    () => {
                        const modal = document.querySelector('.modal.show');
                        if (!modal) return { visible: false };

                        const body = modal.querySelector('.modal-body');
                        const text = body ? body.innerText : '';

                        // 코드가 그대로 보이는지 확인
                        const issues = [];
                        if (text.includes('${config.')) issues.push('${config.*}');
                        if (text.includes('orgChart.modal.labels.${')) issues.push('orgChart.modal.labels.${*}');

                        return {
                            visible: true,
                            hasCodeIssue: issues.length > 0,
                            issues: issues.slice(0, 3),
                            preview: text.substring(0, 300)
                        };
                    }
                """)

                if modal_check['visible']:
                    if modal_check['hasCodeIssue']:
                        print(f"\n  ❌ 모달에 코드가 그대로 표시됨!")
                        print(f"  문제 패턴:")
                        for issue in modal_check['issues']:
                            print(f"    - {issue}")
                        print(f"\n  모달 내용 미리보기:")
                        print(f"  {modal_check['preview']}")
                    else:
                        print(f"  ✅ 모달 정상 표시 (템플릿 리터럴 코드 노출 없음)")
                        print(f"\n  모달 내용 미리보기:")
                        preview_lines = modal_check['preview'].split('\n')[:5]
                        for line in preview_lines:
                            if line.strip():
                                print(f"    {line.strip()}")
                else:
                    print(f"  ❌ 모달이 표시되지 않음")
            else:
                print("  ❌ 직원 정보를 가져올 수 없음")

        except Exception as e:
            print(f"  ❌ 테스트 오류: {e}")
    else:
        print("  ❌ 직원 카드를 찾을 수 없습니다")

    if page_errors:
        print(f"\n❌ JavaScript 오류: {len(page_errors)}개")
        for err in page_errors[:3]:
            print(f"   - {err}")
    else:
        print(f"\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 테스트 완료")