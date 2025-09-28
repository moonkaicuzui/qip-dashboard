// 대시보드 완전 수정 스크립트
// 브라우저 콘솔에 복사해서 실행하세요

console.log("========== 대시보드 완전 수정 시작 ==========");

// 1. Base64 데이터에서 employeeData 추출
const scripts = document.querySelectorAll('script');
let dataLoaded = false;

for (let i = 0; i < scripts.length; i++) {
    const scriptText = scripts[i].innerHTML;
    if (scriptText.includes('const base64Data')) {
        console.log("Base64 데이터 발견!");

        // Base64 데이터 추출
        const match = scriptText.match(/const base64Data = '([^']+)'/);
        if (match) {
            try {
                const base64Str = match[1];
                const jsonStr = atob(base64Str);
                window.employeeData = JSON.parse(jsonStr);
                console.log(`✅ 직원 데이터 로드 성공: ${window.employeeData.length}명`);
                dataLoaded = true;
            } catch(e) {
                console.error("데이터 파싱 실패:", e);
            }
        }
        break;
    }
}

if (!dataLoaded) {
    console.error("❌ 직원 데이터를 찾을 수 없습니다!");
} else {
    // 2. 상단 카드 업데이트
    let totalCount = window.employeeData.length;
    let paidCount = 0;
    let totalAmount = 0;

    window.employeeData.forEach(emp => {
        const amount = parseInt(
            emp['september_incentive'] ||
            emp['September_Incentive'] ||
            emp['Final Incentive amount'] ||
            0
        );
        if (amount > 0) {
            paidCount++;
            totalAmount += amount;
        }
    });

    const paymentRate = totalCount > 0 ? (paidCount / totalCount * 100).toFixed(1) : '0.0';

    // 카드 업데이트
    const totalEmpElem = document.querySelector('#totalEmployees');
    const paidEmpElem = document.querySelector('#paidEmployees');
    const paymentRateElem = document.querySelector('#paymentRate');
    const totalAmountElem = document.querySelector('#totalAmount');

    const lang = window.currentLanguage || 'ko';
    const personUnit = lang === 'ko' ? '명' : lang === 'en' ? ' people' : ' người';

    if (totalEmpElem) totalEmpElem.textContent = totalCount + personUnit;
    if (paidEmpElem) paidEmpElem.textContent = paidCount + personUnit;
    if (paymentRateElem) paymentRateElem.textContent = paymentRate + '%';
    if (totalAmountElem) totalAmountElem.textContent = totalAmount.toLocaleString() + ' VND';

    console.log(`✅ 상단 카드 업데이트: 전체 ${totalCount}명, 지급 ${paidCount}명, 지급률 ${paymentRate}%`);

    // 3. Type별 요약 테이블 업데이트
    window.updateTypeSummaryTable = function() {
        const typeData = {
            'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
        };

        let grandTotal = 0;
        let grandPaid = 0;
        let grandAmount = 0;

        window.employeeData.forEach(emp => {
            const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';
            if (typeData[type]) {
                typeData[type].total++;
                grandTotal++;

                const amount = parseInt(
                    emp['september_incentive'] ||
                    emp['September_Incentive'] ||
                    emp['Final Incentive amount'] ||
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

        const lang = window.currentLanguage || 'ko';
        const personUnit = lang === 'ko' ? '명' : lang === 'en' ? ' people' : ' người';

        const tbody = document.getElementById('typeSummaryBody');
        if (tbody) {
            let html = '';

            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
                const data = typeData[type];
                if (data.total > 0) {
                    const paymentRate = ((data.paid / data.total) * 100).toFixed(1);
                    const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                    const avgTotal = Math.round(data.totalAmount / data.total);

                    html += `
                        <tr>
                            <td><span class="badge bg-primary">${type}</span></td>
                            <td>${data.total}${personUnit}</td>
                            <td>${data.paid}${personUnit}</td>
                            <td>${paymentRate}%</td>
                            <td>${data.totalAmount.toLocaleString()} VND</td>
                            <td>${avgPaid.toLocaleString()} VND</td>
                            <td>${avgTotal.toLocaleString()} VND</td>
                        </tr>`;
                }
            });

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
            console.log("✅ Type별 요약 테이블 업데이트 완료!");
        }
    };

    // Type별 테이블 업데이트 실행
    updateTypeSummaryTable();

    // 4. changeLanguage 함수 재정의
    const originalChangeLanguage = window.changeLanguage;
    window.changeLanguage = function(lang) {
        window.currentLanguage = lang;
        if (typeof updateAllTexts === 'function') {
            updateAllTexts();
        }
        updateTypeSummaryTable();

        // 상단 카드 단위도 업데이트
        const personUnit = lang === 'ko' ? '명' : lang === 'en' ? ' people' : ' người';
        if (totalEmpElem) totalEmpElem.textContent = totalCount + personUnit;
        if (paidEmpElem) paidEmpElem.textContent = paidCount + personUnit;

        localStorage.setItem('dashboardLanguage', lang);
        console.log(`✅ Language changed to ${lang}`);
    };

    console.log("========== 대시보드 완전 수정 완료 ==========");
    console.log("이제 모든 기능이 정상적으로 작동해야 합니다!");
}