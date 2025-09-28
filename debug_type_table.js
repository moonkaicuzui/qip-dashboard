// Type별 요약 테이블 디버그 스크립트

console.log("========== Type별 요약 테이블 디버깅 ==========");

// 1. employeeData 확인
if (typeof employeeData !== 'undefined') {
    console.log("1. employeeData 존재: ✓");
    console.log("   - 총 직원 수:", employeeData.length);

    // 첫 번째 직원 데이터 확인
    if (employeeData.length > 0) {
        console.log("2. 첫 번째 직원 데이터 필드:");
        const firstEmp = employeeData[0];
        console.log("   - ROLE TYPE STD:", firstEmp['ROLE TYPE STD']);
        console.log("   - type:", firstEmp.type);
        console.log("   - Type:", firstEmp.Type);
        console.log("   - September_Incentive:", firstEmp.September_Incentive);
        console.log("   - september_incentive:", firstEmp.september_incentive);
        console.log("   - Final Incentive amount:", firstEmp['Final Incentive amount']);
    }

    // Type별 수동 집계
    console.log("\n3. Type별 수동 집계:");
    const typeCount = {};
    const typeAmount = {};

    employeeData.forEach((emp, idx) => {
        // Type 필드 찾기 - 다양한 가능성 체크
        const type = emp['ROLE TYPE STD'] || emp.type || emp.Type || 'UNKNOWN';

        // 처음 몇 개 데이터 샘플 출력
        if (idx < 3) {
            console.log(`   직원 ${idx + 1}: Type=${type}, Name=${emp['Full Name'] || emp.full_name || 'Unknown'}`);
        }

        // Type별 카운트
        if (!typeCount[type]) {
            typeCount[type] = 0;
            typeAmount[type] = 0;
        }
        typeCount[type]++;

        // 인센티브 금액 합계
        const amount = parseInt(
            emp['Final Incentive amount'] ||
            emp['September_Incentive'] ||
            emp['september_incentive'] ||
            0
        );
        if (amount > 0) {
            typeAmount[type] += amount;
        }
    });

    console.log("\n4. Type별 집계 결과:");
    Object.keys(typeCount).sort().forEach(type => {
        console.log(`   ${type}: ${typeCount[type]}명, 총 ${typeAmount[type].toLocaleString()} VND`);
    });
} else {
    console.log("❌ employeeData가 정의되지 않았습니다!");
}

// 5. updateTypeSummaryTable 함수 존재 확인
console.log("\n5. 함수 확인:");
console.log("   - updateTypeSummaryTable:", typeof updateTypeSummaryTable);
console.log("   - forceUpdateTypeSummary:", typeof window.forceUpdateTypeSummary);

// 6. DOM 요소 확인
console.log("\n6. DOM 요소 확인:");
const tbody = document.getElementById('typeSummaryBody');
console.log("   - typeSummaryBody 존재:", tbody !== null);
if (tbody) {
    console.log("   - 현재 행 수:", tbody.rows.length);
    if (tbody.rows.length === 0) {
        console.log("   ⚠️ 테이블이 비어있습니다!");
    }
}

// 7. 강제 업데이트 시도
console.log("\n7. 강제 업데이트 시도...");
if (typeof updateTypeSummaryTable === 'function') {
    try {
        updateTypeSummaryTable();
        console.log("   ✓ updateTypeSummaryTable() 실행 완료");

        // 업데이트 후 확인
        setTimeout(() => {
            const tbody = document.getElementById('typeSummaryBody');
            if (tbody && tbody.rows.length > 0) {
                console.log("   ✓ 테이블이 업데이트되었습니다! 행 수:", tbody.rows.length);
            } else {
                console.log("   ❌ 테이블이 여전히 비어있습니다.");
            }
        }, 500);
    } catch(e) {
        console.error("   ❌ 함수 실행 중 에러:", e);
    }
} else {
    console.log("   ❌ updateTypeSummaryTable 함수를 찾을 수 없습니다!");
}

console.log("========== 디버깅 완료 ==========");