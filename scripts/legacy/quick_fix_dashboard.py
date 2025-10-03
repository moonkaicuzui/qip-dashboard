#!/usr/bin/env python3
"""
대시보드 Type별 요약 테이블 문제 즉시 수정 스크립트
CompleteRenderer의 JavaScript를 직접 수정하여 문제 해결
"""

import shutil
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🔧 대시보드 Type별 요약 테이블 즉시 수정")
print("=" * 60)

# 백업 생성
js_file = Path("dashboard_v2/static/js/dashboard_complete.js")
backup_file = js_file.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js")

if js_file.exists():
    shutil.copy2(js_file, backup_file)
    print(f"✅ 백업 생성: {backup_file.name}")

# JavaScript 파일 읽기
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

# updateTypeSummaryTable 함수가 제대로 실행되지 않는 문제 수정
# updateSummaryCards에서 에러가 발생해도 updateTypeSummaryTable이 실행되도록 수정

fix_code = """
    // 초기화 시 Type별 테이블 강제 업데이트
    window.forceUpdateTypeSummary = function() {
        console.log('=== Type별 요약 테이블 강제 업데이트 ===');

        // Type별 데이터 집계
        const typeData = {
            'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
        };

        if (!window.employeeData || !Array.isArray(window.employeeData)) {
            console.error('employeeData가 없거나 배열이 아닙니다.');
            return;
        }

        // 직원 데이터 순회하며 집계
        window.employeeData.forEach(emp => {
            // type 필드를 여러 가능한 이름에서 찾기
            const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';

            if (typeData[type]) {
                typeData[type].total++;

                // 인센티브 금액 찾기
                const amount = parseInt(
                    emp['Final Incentive amount'] ||
                    emp['September_Incentive'] ||
                    emp['최종 인센티브 금액'] ||
                    0
                );

                if (amount > 0) {
                    typeData[type].paid++;
                    typeData[type].totalAmount += amount;
                }
            }
        });

        // 테이블 tbody 업데이트
        const tbody = document.getElementById('typeSummaryBody');
        if (!tbody) {
            console.error('typeSummaryBody 요소를 찾을 수 없습니다.');
            return;
        }

        let html = '';
        let grandTotal = 0;
        let grandPaid = 0;
        let grandAmount = 0;

        // 각 Type별 행 생성
        ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
            const data = typeData[type];
            if (data.total > 0) {
                const paymentRate = (data.paid / data.total * 100).toFixed(1);
                const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                const avgTotal = Math.round(data.totalAmount / data.total);

                html += '<tr>';
                html += '<td>' + type + '</td>';
                html += '<td>' + data.total + '명</td>';
                html += '<td>' + data.paid + '명</td>';
                html += '<td>' + paymentRate + '%</td>';
                html += '<td>' + data.totalAmount.toLocaleString() + ' VND</td>';
                html += '<td>' + avgPaid.toLocaleString() + ' VND</td>';
                html += '<td>' + avgTotal.toLocaleString() + ' VND</td>';
                html += '</tr>';

                grandTotal += data.total;
                grandPaid += data.paid;
                grandAmount += data.totalAmount;
            }
        });

        // 전체 합계 행 추가
        if (grandTotal > 0) {
            const grandPaymentRate = (grandPaid / grandTotal * 100).toFixed(1);
            const grandAvgPaid = grandPaid > 0 ? Math.round(grandAmount / grandPaid) : 0;
            const grandAvgTotal = Math.round(grandAmount / grandTotal);

            html += '<tr class="table-info fw-bold">';
            html += '<td>전체</td>';
            html += '<td>' + grandTotal + '명</td>';
            html += '<td>' + grandPaid + '명</td>';
            html += '<td>' + grandPaymentRate + '%</td>';
            html += '<td>' + grandAmount.toLocaleString() + ' VND</td>';
            html += '<td>' + grandAvgPaid.toLocaleString() + ' VND</td>';
            html += '<td>' + grandAvgTotal.toLocaleString() + ' VND</td>';
            html += '</tr>';
        }

        tbody.innerHTML = html;
        console.log('✅ Type별 요약 테이블 업데이트 완료!');
    };

    // 페이지 로드 후 자동 실행
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(window.forceUpdateTypeSummary, 1000);
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(window.forceUpdateTypeSummary, 1000);
        });
    }
"""

# 코드 끝부분에 추가
if "window.forceUpdateTypeSummary" not in content:
    content = content + "\n\n" + fix_code
    print("✅ 강제 업데이트 함수 추가됨")

# 파일 저장
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ JavaScript 파일 수정 완료!")

# 대시보드 재생성
print("\n🔄 대시보드 재생성 중...")
import subprocess
result = subprocess.run(
    ["python", "dashboard_v2/generate_dashboard.py", "--month", "september", "--year", "2025"],
    capture_output=True,
    text=True,
    cwd="/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일"
)

if result.returncode == 0:
    print("✅ 대시보드 재생성 완료!")
    print("\n📌 확인 방법:")
    print("1. 브라우저에서 파일 열기:")
    print("   open output_files/Incentive_Dashboard_2025_09_Version_6.html")
    print("\n2. Type별 요약 테이블이 자동으로 채워집니다.")
    print("\n3. 만약 아직도 비어있다면 브라우저 콘솔(F12)에서:")
    print("   window.forceUpdateTypeSummary()")
else:
    print(f"❌ 대시보드 생성 실패: {result.stderr}")

print("=" * 60)