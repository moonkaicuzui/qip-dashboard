#!/usr/bin/env python3
"""
대시보드 완전 수정 스크립트
- TYPE 테이블 데이터 생성 로직 추가
- 언어 전환 문제 해결
- 영어/한국어 혼재 문제 수정
"""

import re
import json

def fix_dashboard():
    print("🔧 대시보드 완전 수정 시작...")

    # 1. integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 영어/한국어 혼재 문제 수정
    replacements = [
        # 헤더 텍스트 수정
        ('QIP incentive calculation 결과', 'QIP 인센티브 계산 결과'),
        ('TOTAL 직원', '전체 직원'),
        ('TOTAL 지급액', '총 지급액'),
        ('total 직원', '전체 직원'),
        ('total 인원', '전체 인원'),
        ('total 지급액', '총 지급액'),
        ('final report', '최종 보고서'),
        ('이 report는 month말 final report입니다', '이 보고서는 월말 최종 보고서입니다'),
        ('모든 incentive 조건이 정상적으로 apply됩니다', '모든 인센티브 조건이 정상적으로 적용됩니다'),
        ('creationth:', '생성일:'),
        ('수령률', '지급률'),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    # 3. TYPE 테이블 생성 함수 추가
    type_table_function = """
    // TYPE 테이블 생성 함수
    function generateTypeTable() {
        console.log('Generating TYPE table...');

        const typeSummaryBody = document.getElementById('typeSummaryBody');
        if (!typeSummaryBody) {
            console.error('typeSummaryBody element not found');
            return;
        }

        // 데이터가 없으면 employeeData를 사용
        if (!window.employeeData || window.employeeData.length === 0) {
            console.log('No employee data available for TYPE table');
            typeSummaryBody.innerHTML = '<tr><td colspan="7" class="text-center">데이터 없음</td></tr>';
            return;
        }

        // TYPE별 집계
        const typeStats = {
            'TYPE-1': { total: 0, eligible: 0, amount: 0 },
            'TYPE-2': { total: 0, eligible: 0, amount: 0 },
            'TYPE-3': { total: 0, eligible: 0, amount: 0 }
        };

        window.employeeData.forEach(emp => {
            const empType = emp['type'] || emp['ROLE TYPE STD'] || 'TYPE-2';
            const incentiveAmount = parseFloat(emp['Incentive Amount (VND)']) || 0;

            if (typeStats[empType]) {
                typeStats[empType].total++;
                if (incentiveAmount > 0) {
                    typeStats[empType].eligible++;
                    typeStats[empType].amount += incentiveAmount;
                }
            }
        });

        // 테이블 생성
        let tableHTML = '';
        let totalAll = 0, eligibleAll = 0, amountAll = 0;

        ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
            const stats = typeStats[type];
            const paymentRate = stats.total > 0 ? ((stats.eligible / stats.total) * 100).toFixed(1) : '0.0';
            const avgEligible = stats.eligible > 0 ? Math.round(stats.amount / stats.eligible) : 0;
            const avgTotal = stats.total > 0 ? Math.round(stats.amount / stats.total) : 0;

            totalAll += stats.total;
            eligibleAll += stats.eligible;
            amountAll += stats.amount;

            const typeClass = type === 'TYPE-1' ? 'type-1' : (type === 'TYPE-2' ? 'type-2' : 'type-3');

            tableHTML += `
                <tr>
                    <td><span class="badge bg-${typeClass === 'type-1' ? 'primary' : typeClass === 'type-2' ? 'warning' : 'success'}">${type}</span></td>
                    <td>${stats.total}명</td>
                    <td>${stats.eligible}명</td>
                    <td>${paymentRate}%</td>
                    <td>${stats.amount.toLocaleString()} VND</td>
                    <td>${avgEligible.toLocaleString()} VND</td>
                    <td>${avgTotal.toLocaleString()} VND</td>
                </tr>
            `;
        });

        // 합계 행 추가
        const totalPaymentRate = totalAll > 0 ? ((eligibleAll / totalAll) * 100).toFixed(1) : '0.0';
        const totalAvgEligible = eligibleAll > 0 ? Math.round(amountAll / eligibleAll) : 0;
        const totalAvgTotal = totalAll > 0 ? Math.round(amountAll / totalAll) : 0;

        tableHTML += `
            <tr class="table-info fw-bold">
                <td>Total</td>
                <td>${totalAll}명</td>
                <td>${eligibleAll}명</td>
                <td>${totalPaymentRate}%</td>
                <td>${amountAll.toLocaleString()} VND</td>
                <td>${totalAvgEligible.toLocaleString()} VND</td>
                <td>${totalAvgTotal.toLocaleString()} VND</td>
            </tr>
        `;

        typeSummaryBody.innerHTML = tableHTML;
        console.log('TYPE table generated successfully');
    }
"""

    # 4. DOMContentLoaded에 generateTypeTable 호출 추가
    dom_loaded_pattern = r"(document\.addEventListener\('DOMContentLoaded', function\(\) \{[^}]*)"

    # generateTypeTable 호출이 없으면 추가
    if 'generateTypeTable()' not in content:
        # DOMContentLoaded 내부에 추가
        dom_loaded_replacement = r"\1\n        // Generate TYPE table\n        generateTypeTable();\n"
        content = re.sub(dom_loaded_pattern, dom_loaded_replacement, content, count=1)

    # 5. TYPE 테이블 생성 함수를 JavaScript 섹션에 추가
    # </script> 태그 직전에 추가
    script_end_pos = content.rfind('</script>')
    if script_end_pos != -1 and 'function generateTypeTable()' not in content:
        content = content[:script_end_pos] + type_table_function + '\n' + content[script_end_pos:]

    # 6. 전역 함수 노출 추가
    global_expose = """
        // 전역 함수로 노출 (필수)
        window.generateTypeTable = generateTypeTable;
        window.showTab = showTab;
        window.changeLanguage = changeLanguage;
        window.openPositionModal = openPositionModal;
        window.generateEmployeeTable = generateEmployeeTable;
        window.generatePositionTables = generatePositionTables;
        window.openNonWorkingModal = openNonWorkingModal;
        window.showAttendanceBelow88Details = showAttendanceBelow88Details;
        window.showContinuousFailureDetails = showContinuousFailureDetails;
        window.showExcludedEmployees = showExcludedEmployees;
    """

    # 전역 함수 노출이 없으면 추가
    if 'window.generateTypeTable = generateTypeTable' not in content:
        # DOMContentLoaded 끝나기 직전에 추가
        dom_content_pattern = r"(document\.addEventListener\('DOMContentLoaded', function\(\) \{.*?)(    \}\);)"
        if re.search(dom_content_pattern, content, re.DOTALL):
            content = re.sub(
                dom_content_pattern,
                r"\1" + global_expose + r"\n\2",
                content,
                flags=re.DOTALL,
                count=1
            )

    # 7. 언어 전환 시 TYPE 테이블도 업데이트하도록 수정
    change_language_update = """
            // TYPE 테이블 언어 업데이트
            const typeSummaryBody = document.getElementById('typeSummaryBody');
            if (typeSummaryBody) {
                const rows = typeSummaryBody.querySelectorAll('tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        // "명"을 해당 언어로 변경
                        [1, 2].forEach(idx => {
                            if (cells[idx]) {
                                const text = cells[idx].textContent;
                                const number = text.replace(/[^\\d]/g, '');
                                if (number) {
                                    const unit = lang === 'ko' ? '명' : lang === 'en' ? '' : '';
                                    cells[idx].textContent = number + unit;
                                }
                            }
                        });
                    }
                });
            }
    """

    # changeLanguage 함수에 TYPE 테이블 업데이트 추가
    if 'TYPE 테이블 언어 업데이트' not in content:
        change_lang_pattern = r"(function changeLanguage\(lang\) \{[^}]*updateAllTexts\(lang\);)"
        if re.search(change_lang_pattern, content, re.DOTALL):
            content = re.sub(
                change_lang_pattern,
                r"\1" + change_language_update,
                content,
                flags=re.DOTALL,
                count=1
            )

    # 8. 번역 파일 업데이트
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # 누락된 번역 추가
    if 'typeSummary' not in translations:
        translations['typeSummary'] = {
            'ko': 'Type별 현황',
            'en': 'Type Summary',
            'vi': 'Tóm tắt theo loại'
        }

    if 'tableHeaders' not in translations:
        translations['tableHeaders'] = {}

    translations['tableHeaders'].update({
        'totalEmployees': {
            'ko': '전체 직원',
            'en': 'Total Employees',
            'vi': 'Tổng nhân viên'
        },
        'eligibleEmployees': {
            'ko': '수령 직원',
            'en': 'Eligible Employees',
            'vi': 'Nhân viên đủ điều kiện'
        },
        'paymentRate': {
            'ko': '지급률',
            'en': 'Payment Rate',
            'vi': 'Tỷ lệ thanh toán'
        },
        'totalAmount': {
            'ko': '총 지급액',
            'en': 'Total Amount',
            'vi': 'Tổng số tiền'
        }
    })

    # 번역 파일 저장
    with open('config_files/dashboard_translations.json', 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    # 9. 수정된 파일 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 대시보드 수정 완료!")
    print("\n주요 수정 사항:")
    print("  1. TYPE 테이블 생성 함수 추가")
    print("  2. 영어/한국어 혼재 문제 해결")
    print("  3. 전역 함수 노출로 JavaScript 에러 해결")
    print("  4. 언어 전환 기능 개선")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  ./action.sh")

if __name__ == "__main__":
    fix_dashboard()