// ==================================================
// 브라우저 콘솔에서 직접 실행할 디버깅 코드
// ==================================================
//
// 사용 방법:
// 1. 대시보드 HTML 파일을 브라우저에서 열기
// 2. F12 또는 개발자 도구 열기
// 3. Console 탭 선택
// 4. 아래 코드를 복사해서 붙여넣기
// ==================================================

// 1. employeeData 확인
console.log("========== 데이터 확인 ==========");
console.log("1. employeeData 존재 여부:", typeof employeeData !== 'undefined');
console.log("2. employeeData 타입:", typeof employeeData);
console.log("3. employeeData 길이:", employeeData ? employeeData.length : 0);

// 첫 번째 직원 데이터 확인
if (employeeData && employeeData.length > 0) {
    console.log("4. 첫 번째 직원 데이터:");
    const first = employeeData[0];
    console.log("   - ROLE TYPE STD:", first['ROLE TYPE STD']);
    console.log("   - type:", first.type);
    console.log("   - September_Incentive:", first.September_Incentive);
    console.log("   - Final Incentive amount:", first['Final Incentive amount']);
}

// 2. Type별 집계 실행
console.log("\n========== Type별 집계 테스트 ==========");
const typeData = {
    'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
    'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
    'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
};

let unknownTypes = [];

employeeData.forEach((emp, index) => {
    // type 필드 찾기
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
    } else {
        unknownTypes.push({index, type, name: emp.name || emp['Full Name']});
    }
});

// 결과 출력
Object.keys(typeData).forEach(type => {
    const data = typeData[type];
    console.log(`${type}: 총 ${data.total}명, 지급 ${data.paid}명, 금액 ${data.totalAmount.toLocaleString()} VND`);
});

if (unknownTypes.length > 0) {
    console.log("\n⚠️ 알 수 없는 Type:", unknownTypes.length, "개");
    console.log(unknownTypes.slice(0, 5));
}

// 3. 실제 테이블 확인
console.log("\n========== DOM 테이블 확인 ==========");
const tbody = document.getElementById('typeSummaryBody');
console.log("테이블 tbody 존재:", tbody !== null);
if (tbody) {
    console.log("현재 테이블 내용:", tbody.innerHTML.substring(0, 200));
    console.log("테이블 행 개수:", tbody.rows ? tbody.rows.length : 0);
}

// 4. updateTypeSummaryTable 함수 실행
console.log("\n========== updateTypeSummaryTable 실행 ==========");
if (typeof updateTypeSummaryTable === 'function') {
    console.log("함수 존재: YES");
    try {
        updateTypeSummaryTable();
        console.log("✅ 함수 실행 완료!");

        // 실행 후 테이블 확인
        if (tbody) {
            console.log("실행 후 테이블 행 개수:", tbody.rows ? tbody.rows.length : 0);
        }
    } catch(e) {
        console.error("❌ 함수 실행 중 에러:", e);
    }
} else {
    console.error("❌ updateTypeSummaryTable 함수가 없습니다!");
}

// 5. 직접 테이블 업데이트 (테스트용)
console.log("\n========== 직접 테이블 업데이트 테스트 ==========");
if (tbody && typeData['TYPE-1'].total > 0) {
    // 테스트용 HTML 생성
    let testHtml = '';
    ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
        const data = typeData[type];
        if (data.total > 0) {
            testHtml += `<tr>
                <td>${type}</td>
                <td>${data.total}명</td>
                <td>${data.paid}명</td>
                <td>${(data.paid/data.total*100).toFixed(1)}%</td>
                <td>${data.totalAmount.toLocaleString()} VND</td>
                <td>${data.paid > 0 ? Math.round(data.totalAmount/data.paid).toLocaleString() : 0} VND</td>
                <td>${Math.round(data.totalAmount/data.total).toLocaleString()} VND</td>
            </tr>`;
        }
    });

    if (testHtml) {
        tbody.innerHTML = testHtml;
        console.log("✅ 테이블이 업데이트되었습니다! 화면을 확인하세요.");
    } else {
        console.log("⚠️ 생성할 데이터가 없습니다.");
    }
} else {
    console.log("⚠️ tbody가 없거나 데이터가 없습니다.");
}

console.log("\n========== 디버깅 완료 ==========");