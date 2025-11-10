#!/usr/bin/env python3
"""
대시보드 완전 수정 스크립트 v2
- TYPE 테이블 데이터 생성 로직 추가
- 언어 전환 문제 해결
- 영어/한국어 혼재 문제 수정
"""

import re
import json

def fix_dashboard():
    print("🔧 대시보드 완전 수정 시작 (v2)...")

    # 1. integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 영어/한국어 혼재 텍스트 수정
    replacements = [
        # HTML 제목 부분
        ("heading='QIP incentive calculation 결과", "heading='QIP 인센티브 계산 결과"),
        ('heading="QIP incentive calculation 결과', 'heading="QIP 인센티브 계산 결과'),
        ("<h1>QIP incentive calculation 결과", "<h1>QIP 인센티브 계산 결과"),

        # 통계 카드 레이블
        ('heading="total 직원"', 'heading="전체 직원"'),
        ('heading="TOTAL 직원"', 'heading="전체 직원"'),
        ('>total 직원<', '>전체 직원<'),
        ('>TOTAL 직원<', '>전체 직원<'),

        ('heading="total 지급액"', 'heading="총 지급액"'),
        ('heading="TOTAL 지급액"', 'heading="총 지급액"'),
        ('>total 지급액<', '>총 지급액<'),
        ('>TOTAL 지급액<', '>총 지급액<'),

        ('heading="수령률"', 'heading="지급률"'),
        ('>수령률<', '>지급률<'),

        # 보고서 배너
        ('heading="final report"', 'heading="최종 보고서"'),
        ('>final report<', '>최종 보고서<'),
        ('이 report는 month말 final report입니다', '이 보고서는 월말 최종 보고서입니다'),
        ('모든 incentive 조건이 정상적으로 apply됩니다', '모든 인센티브 조건이 정상적으로 적용됩니다'),

        # 테이블 헤더
        ('>total 인원<', '>전체 인원<'),
        ('total 인원', '전체 인원'),
        ('>total 지급액<', '>총 지급액<'),
        ('total 지급액', '총 지급액'),

        # 날짜 관련
        ('creationth:', '생성일:'),
        ("'creationth: '", "'생성일: '"),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    # 3. generateTypeTable 함수를 찾아서 수정 또는 추가
    # 먼저 기존에 generateTypeTable이 있는지 확인
    if 'function generateTypeTable()' not in content:
        # JavaScript 섹션 찾기 - employeeData 정의 이후 부분 찾기
        type_table_js = '''
        // TYPE 테이블 생성 함수
        function generateTypeTable() {{
            console.log('Generating TYPE table...');

            const typeSummaryBody = document.getElementById('typeSummaryBody');
            if (!typeSummaryBody) {{
                console.error('typeSummaryBody element not found');
                return;
            }}

            // 데이터가 없으면 employeeData를 사용
            if (!window.employeeData || window.employeeData.length === 0) {{
                console.log('No employee data available for TYPE table');
                typeSummaryBody.innerHTML = '<tr><td colspan="7" class="text-center">데이터 없음</td></tr>';
                return;
            }}

            // TYPE별 집계
            const typeStats = {{
                'TYPE-1': {{ total: 0, eligible: 0, amount: 0 }},
                'TYPE-2': {{ total: 0, eligible: 0, amount: 0 }},
                'TYPE-3': {{ total: 0, eligible: 0, amount: 0 }}
            }};

            window.employeeData.forEach(emp => {{
                const empType = emp['type'] || emp['ROLE TYPE STD'] || 'TYPE-2';
                const incentiveAmount = parseFloat(emp['Incentive Amount (VND)']) || 0;

                if (typeStats[empType]) {{
                    typeStats[empType].total++;
                    if (incentiveAmount > 0) {{
                        typeStats[empType].eligible++;
                        typeStats[empType].amount += incentiveAmount;
                    }}
                }}
            }});

            // 테이블 생성
            let tableHTML = '';
            let totalAll = 0, eligibleAll = 0, amountAll = 0;

            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {{
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
                        <td><span class="badge bg-${{typeClass === 'type-1' ? 'primary' : typeClass === 'type-2' ? 'warning' : 'success'}}">${{type}}</span></td>
                        <td>${{stats.total}}명</td>
                        <td>${{stats.eligible}}명</td>
                        <td>${{paymentRate}}%</td>
                        <td>${{stats.amount.toLocaleString()}} VND</td>
                        <td>${{avgEligible.toLocaleString()}} VND</td>
                        <td>${{avgTotal.toLocaleString()}} VND</td>
                    </tr>
                `;
            }});

            // 합계 행 추가
            const totalPaymentRate = totalAll > 0 ? ((eligibleAll / totalAll) * 100).toFixed(1) : '0.0';
            const totalAvgEligible = eligibleAll > 0 ? Math.round(amountAll / eligibleAll) : 0;
            const totalAvgTotal = totalAll > 0 ? Math.round(amountAll / totalAll) : 0;

            tableHTML += `
                <tr class="table-info fw-bold">
                    <td>Total</td>
                    <td>${{totalAll}}명</td>
                    <td>${{eligibleAll}}명</td>
                    <td>${{totalPaymentRate}}%</td>
                    <td>${{amountAll.toLocaleString()}} VND</td>
                    <td>${{totalAvgEligible.toLocaleString()}} VND</td>
                    <td>${{totalAvgTotal.toLocaleString()}} VND</td>
                </tr>
            `;

            typeSummaryBody.innerHTML = tableHTML;
            console.log('TYPE table generated successfully');
        }}
'''

        # employeeData 정의 후에 추가
        insert_pos = content.find('window.employeeData = employeeData;')
        if insert_pos != -1:
            insert_pos = content.find('\n', insert_pos) + 1
            content = content[:insert_pos] + type_table_js + content[insert_pos:]

    # 4. DOMContentLoaded에서 generateTypeTable 호출 추가
    dom_pattern = r"document\.addEventListener\('DOMContentLoaded', function\(\) \{"
    dom_match = re.search(dom_pattern, content)

    if dom_match and 'generateTypeTable();' not in content:
        # showTab('summary'); 이후에 추가
        showTab_pos = content.find("showTab('summary');")
        if showTab_pos != -1:
            insert_pos = content.find('\n', showTab_pos) + 1
            content = content[:insert_pos] + "            generateTypeTable();  // TYPE 테이블 생성\n" + content[insert_pos:]

    # 5. 전역 함수 노출 확인 및 추가
    if 'window.generateTypeTable = generateTypeTable;' not in content:
        # DOMContentLoaded 끝나기 전에 추가
        dom_end = content.find("    });  // DOMContentLoaded end")
        if dom_end == -1:
            # 다른 패턴 시도
            dom_end = content.rfind("});", 0, content.rfind("</script>"))

        if dom_end != -1:
            expose_code = """
        // 전역 함수로 노출
        window.generateTypeTable = generateTypeTable;
        window.showTab = showTab;
        window.changeLanguage = changeLanguage;
        window.openPositionModal = openPositionModal;
        window.generateEmployeeTable = generateEmployeeTable;
        window.generatePositionTables = generatePositionTables;
"""
            content = content[:dom_end] + expose_code + "\n    " + content[dom_end:]

    # 6. showTab 함수에서 summary 탭 클릭 시 TYPE 테이블 재생성 추가
    showtab_pattern = r"if \(tabName === 'summary'\) \{"
    if re.search(showtab_pattern, content):
        # summary 탭 표시 후 generateTypeTable 호출 추가
        if "generateTypeTable();" not in content[content.find("if (tabName === 'summary')"):content.find("if (tabName === 'summary')") + 200]:
            content = re.sub(
                r"(if \(tabName === 'summary'\) \{[^}]*)",
                r"\1\n            generateTypeTable();",
                content,
                count=1
            )

    # 7. 저장
    with open('integrated_dashboard_final.py', 'w', encoding='utf-8') as f:
        f.write(content)

    # 8. 번역 파일 업데이트
    with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # 누락된 번역 추가
    if 'sectionTitles' not in translations:
        translations['sectionTitles'] = {}

    translations['sectionTitles']['typeSummary'] = {
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

    with open('config_files/dashboard_translations.json', 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print("✅ 대시보드 수정 완료!")
    print("\n주요 수정 사항:")
    print("  1. TYPE 테이블 생성 함수 추가")
    print("  2. 영어/한국어 혼재 문제 해결")
    print("  3. 전역 함수 노출로 JavaScript 에러 해결")
    print("  4. 언어 전환 기능 개선")
    print("\n다음 명령어로 대시보드를 재생성하세요:")
    print("  python integrated_dashboard_final.py --month 10 --year 2025")

if __name__ == "__main__":
    fix_dashboard()