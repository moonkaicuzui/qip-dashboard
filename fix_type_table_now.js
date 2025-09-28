// Type별 요약 테이블 즉시 수정 스크립트
// 브라우저 콘솔에 복사해서 실행하세요

console.log("========== Type별 요약 테이블 강제 수정 ==========");

// 1. 현재 상태 확인
console.log("1. 현재 데이터 확인:");
console.log("   - employeeData 존재:", typeof employeeData !== 'undefined');
console.log("   - 직원 수:", employeeData ? employeeData.length : 0);

// 2. Type별 데이터 재집계
if (typeof employeeData !== 'undefined' && employeeData.length > 0) {
    const typeData = {
        'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
        'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
        'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
    };

    let grandTotal = 0;
    let grandPaid = 0;
    let grandAmount = 0;

    // 데이터 집계
    employeeData.forEach((emp, idx) => {
        // Type 찾기 - 모든 가능한 필드 체크
        const type = emp['ROLE TYPE STD'] || emp.type || emp.Type || emp['Role Type'] || 'UNKNOWN';

        if (idx < 3) {
            console.log(`샘플 ${idx + 1}: Type=${type}, Name=${emp['Full Name'] || emp.name}`);
        }

        if (typeData[type]) {
            typeData[type].total++;
            grandTotal++;

            // 인센티브 금액 찾기 - 모든 가능한 필드 체크
            const amount = parseInt(
                emp['Final Incentive amount'] ||
                emp['September_Incentive'] ||
                emp['september_incentive'] ||
                emp['9월_incentive'] ||
                emp['인센티브'] ||
                0
            );

            if (amount > 0) {
                typeData[type].paid++;
                typeData[type].totalAmount += amount;
                grandPaid++;
                grandAmount += amount;
            }
        }
    });

    console.log("\n2. 집계 결과:");
    console.log("   TYPE-1:", typeData['TYPE-1']);
    console.log("   TYPE-2:", typeData['TYPE-2']);
    console.log("   TYPE-3:", typeData['TYPE-3']);
    console.log("   전체:", { total: grandTotal, paid: grandPaid, amount: grandAmount });

    // 3. 테이블 강제 업데이트
    const tbody = document.getElementById('typeSummaryBody');
    if (tbody) {
        // 현재 언어 확인
        const lang = currentLanguage || 'ko';
        const personUnit = lang === 'ko' ? '명' : lang === 'en' ? ' people' : ' người';

        let html = '';

        // 각 Type별 행 생성
        ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
            const data = typeData[type];
            if (data.total > 0) {
                const paymentRate = ((data.paid / data.total) * 100).toFixed(1);
                const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                const avgTotal = Math.round(data.totalAmount / data.total);

                html += `
                    <tr>
                        <td>
                            <span class="badge bg-primary">${type}</span>
                        </td>
                        <td>${data.total}${personUnit}</td>
                        <td>${data.paid}${personUnit}</td>
                        <td>${paymentRate}%</td>
                        <td>${data.totalAmount.toLocaleString()} VND</td>
                        <td>${avgPaid.toLocaleString()} VND</td>
                        <td>${avgTotal.toLocaleString()} VND</td>
                    </tr>`;
            }
        });

        // 합계 행 추가
        if (grandTotal > 0) {
            const totalPaymentRate = ((grandPaid / grandTotal) * 100).toFixed(1);
            const totalAvgPaid = grandPaid > 0 ? Math.round(grandAmount / grandPaid) : 0;
            const totalAvgTotal = Math.round(grandAmount / grandTotal);

            html += `
                <tr class="table-active fw-bold">
                    <td>Total</td>
                    <td>${grandTotal}${personUnit}</td>
                    <td>${grandPaid}${personUnit}</td>
                    <td>${totalPaymentRate}%</td>
                    <td>${grandAmount.toLocaleString()} VND</td>
                    <td>${totalAvgPaid.toLocaleString()} VND</td>
                    <td>${totalAvgTotal.toLocaleString()} VND</td>
                </tr>`;
        }

        tbody.innerHTML = html;
        console.log("✅ 테이블이 업데이트되었습니다!");

        // 상단 카드도 업데이트
        const totalEmpElem = document.querySelector('#totalEmployees');
        const paidEmpElem = document.querySelector('#paidEmployees');
        const paymentRateElem = document.querySelector('#paymentRate');
        const totalAmountElem = document.querySelector('#totalAmount');

        if (totalEmpElem) totalEmpElem.textContent = grandTotal + personUnit;
        if (paidEmpElem) paidEmpElem.textContent = grandPaid + personUnit;
        if (paymentRateElem) paymentRateElem.textContent = ((grandPaid / grandTotal) * 100).toFixed(1) + '%';
        if (totalAmountElem) totalAmountElem.textContent = grandAmount.toLocaleString() + ' VND';

        console.log("✅ 상단 카드도 업데이트되었습니다!");
    } else {
        console.log("❌ typeSummaryBody 요소를 찾을 수 없습니다!");
    }
} else {
    console.log("❌ employeeData가 없거나 비어있습니다!");

    // 수동으로 데이터 로드 시도
    if (typeof excelDashboardData !== 'undefined' && excelDashboardData.employee_data) {
        console.log("excelDashboardData에서 데이터를 가져옵니다...");
        window.employeeData = excelDashboardData.employee_data;
        console.log("데이터를 다시 로드했습니다. 스크립트를 다시 실행하세요.");
    }
}

console.log("========== 완료 ==========")