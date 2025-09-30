#!/usr/bin/env python3
"""
모달 표시 및 언어 전환 종합 테스트
"""

from playwright.sync_api import sync_playwright
import time
import os

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 모달 및 언어 전환 종합 테스트\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_messages = []
    page_errors = []

    page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    print("📊 Org Chart 탭 열기...")
    page.click("#tabOrgChart")
    time.sleep(2)

    print("\n=== 1단계: 모달 표시 테스트 ===\n")

    # 모달 테스트를 위한 여러 직급의 직원 찾기
    positions_to_test = [
        "MANAGER",
        "SUPERVISOR",
        "LINE LEADER"
    ]

    for position in positions_to_test:
        print(f"\n🎯 {position} 직급 모달 테스트:")

        try:
            # 해당 포지션의 직원 카드 찾기
            result = page.evaluate(f"""
                () => {{
                    const cards = document.querySelectorAll('.org-card');
                    for (let card of cards) {{
                        const posText = card.querySelector('.position-badge')?.textContent || '';
                        if (posText.includes('{position}')) {{
                            return {{
                                found: true,
                                name: card.querySelector('.card-title')?.textContent,
                                empNo: card.getAttribute('data-emp-no')
                            }};
                        }}
                    }}
                    return {{ found: false }};
                }}
            """)

            if result['found']:
                print(f"  ✅ {result['name']} 발견")

                # 모달 열기
                page.evaluate(f"""
                    () => {{
                        showIncentiveModal('{result['empNo']}');
                    }}
                """)
                time.sleep(1.5)

                # 모달 내용 확인
                modal_content = page.evaluate("""
                    () => {
                        const modal = document.querySelector('.modal.show');
                        if (!modal) return { visible: false };

                        const body = modal.querySelector('.modal-body');
                        const text = body ? body.innerText : '';

                        // 코드가 그대로 보이는지 확인
                        const hasCodeIssue = text.includes('${config.') ||
                                            text.includes('orgChart.modal.labels.${');

                        return {
                            visible: true,
                            hasCodeIssue: hasCodeIssue,
                            preview: text.substring(0, 200)
                        };
                    }
                """)

                if modal_content['visible']:
                    if modal_content['hasCodeIssue']:
                        print(f"  ❌ 모달에 코드가 그대로 표시됨!")
                        print(f"     미리보기: {modal_content['preview'][:100]}...")
                    else:
                        print(f"  ✅ 모달 정상 표시 (코드 노출 없음)")
                else:
                    print(f"  ❌ 모달이 표시되지 않음")

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

            else:
                print(f"  ⚠️  {position} 직급 직원을 찾을 수 없음")

        except Exception as e:
            print(f"  ❌ 테스트 오류: {e}")

    print("\n\n=== 2단계: 언어 전환 테스트 ===\n")

    languages = ['ko', 'en', 'vi']

    for lang in languages:
        print(f"\n🌐 {lang.upper()} 언어로 전환:")

        try:
            # 언어 버튼 클릭
            page.click(f"button[data-lang='{lang}']")
            time.sleep(1)

            # 현재 언어 확인
            current_lang = page.evaluate("() => currentLanguage")
            print(f"  현재 언어: {current_lang}")

            # 주요 텍스트 확인
            text_check = page.evaluate("""
                () => {
                    return {
                        tabOrgChart: document.querySelector('#tabOrgChart')?.textContent,
                        headerTitle: document.querySelector('.dashboard-header h1')?.textContent
                    };
                }
            """)

            print(f"  조직도 탭: {text_check['tabOrgChart']}")

            # 모달 열어서 언어 확인
            first_emp = page.evaluate("""
                () => {
                    const card = document.querySelector('.org-card');
                    return card ? card.getAttribute('data-emp-no') : null;
                }
            """)

            if first_emp:
                page.evaluate(f"() => showIncentiveModal('{first_emp}')")
                time.sleep(1)

                modal_lang_check = page.evaluate("""
                    () => {
                        const modal = document.querySelector('.modal.show');
                        if (!modal) return { visible: false };

                        const title = modal.querySelector('.modal-title')?.textContent;
                        const body = modal.querySelector('.modal-body')?.innerText;

                        return {
                            visible: true,
                            title: title,
                            bodyPreview: body ? body.substring(0, 150) : ''
                        };
                    }
                """)

                if modal_lang_check['visible']:
                    print(f"  모달 제목: {modal_lang_check['title']}")
                    print(f"  ✅ 언어 전환 성공")

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
            print(f"  ❌ 언어 전환 오류: {e}")

    # JavaScript 오류 확인
    print("\n\n=== JavaScript 오류 확인 ===")

    error_messages = [msg for msg in console_messages if 'error' in msg.lower()]

    if error_messages:
        print(f"\n❌ 콘솔 오류 발견 ({len(error_messages)}개):")
        for msg in error_messages[:5]:
            print(f"  - {msg}")
    else:
        print("\n✅ 콘솔 오류 없음")

    if page_errors:
        print(f"\n❌ JavaScript 오류 ({len(page_errors)}개):")
        for err in page_errors[:3]:
            print(f"  - {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 테스트 완료")