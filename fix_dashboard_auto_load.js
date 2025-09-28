// 대시보드 자동 로드 수정 스크립트
// 브라우저 콘솔에 복사해서 실행하거나 북마크릿으로 저장하세요

(function() {
    console.log("========== 대시보드 자동 로드 시작 ==========");

    // 1. Base64 데이터에서 employeeData 로드
    const base64Element = document.getElementById('employeeDataBase64');
    if (base64Element) {
        try {
            const base64Data = base64Element.textContent;
            const jsonStr = atob(base64Data);
            window.employeeData = JSON.parse(jsonStr);
            console.log(`✅ 직원 데이터 로드 성공: ${window.employeeData.length}명`);
        } catch(e) {
            console.error("❌ 데이터 로드 실패:", e);
            return;
        }
    } else {
        console.error("❌ Base64 데이터 요소를 찾을 수 없습니다!");
        return;
    }

    // 2. Type별 요약 테이블 업데이트
    const typeData = {
        'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
        'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
        'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
    };

    let grandTotal = 0;
    let grandPaid = 0;
    let grandAmount = 0;

    // 데이터 집계
    window.employeeData.forEach(emp => {
        const type = emp['ROLE TYPE STD'] || emp.type || emp.Type || 'UNKNOWN';

        if (typeData[type]) {
            typeData[type].total++;
            grandTotal++;

            const amount = parseInt(
                emp['Final Incentive amount'] ||
                emp['september_incentive'] ||
                emp['September_Incentive'] ||
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

    // 3. 테이블 업데이트
    const tbody = document.getElementById('typeSummaryBody');
    if (tbody) {
        const lang = window.currentLanguage || 'ko';
        const personUnit = lang === 'ko' ? '명' : lang === 'en' ? ' people' : ' người';

        let html = '';

        // 각 Type별 행 추가
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
        console.log("✅ Type별 요약 테이블 업데이트 완료!");
    }

    // 4. 다른 초기화 함수들도 실행
    if (typeof initCharts === 'function') {
        try {
            initCharts();
            console.log("✅ 차트 초기화 완료");
        } catch(e) {
            console.warn("⚠️ 차트 초기화 실패:", e);
        }
    }

    if (typeof updateAllTexts === 'function') {
        try {
            updateAllTexts();
            console.log("✅ 텍스트 업데이트 완료");
        } catch(e) {
            console.warn("⚠️ 텍스트 업데이트 실패:", e);
        }
    }

    console.log("========== 대시보드 자동 로드 완료 ==========");
    console.log(`📊 결과: 전체 ${grandTotal}명, 지급 ${grandPaid}명 (${((grandPaid/grandTotal)*100).toFixed(1)}%), 총액 ${grandAmount.toLocaleString()} VND`);
})();