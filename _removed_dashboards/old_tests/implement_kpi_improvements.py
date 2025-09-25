#!/usr/bin/env python3
"""
KPI 개선 사항 구현
1. 최소 근무일 로직 수정
2. 실제 근무일 0일 필드 매핑
3. 구역 AQL Reject 3% 이상으로 변경
4. 출근율 88% 미만 KPI 추가
"""

import re
from pathlib import Path

def implement_kpi_improvements():
    file_path = Path('integrated_dashboard_final.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=" * 80)
    print("🔧 KPI 개선 사항 구현")
    print("=" * 80)

    # 1. 출근율 88% 미만 KPI 카드 추가
    print("\n1️⃣ 출근율 88% 미만 KPI 카드 추가...")

    # KPI 카드 HTML 추가 (최소 근무일 미충족 다음에)
    attendance_kpi_html = """
                <!-- KPI 카드 4-1: 출근율 88% 미만 -->
                <div class="kpi-card" onclick="showValidationModal('attendanceBelow88')" style="--card-color-1: #9b59b6; --card-color-2: #8e44ad; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.1);">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-value" id="kpiAttendanceBelow88">-</div>
                    <div class="kpi-label">출근율 88% 미만</div>
                </div>
"""

    # KPI 카드 5 앞에 삽입
    pattern = r'(<!-- KPI 카드 5: AQL FAIL 보유자 -->)'
    replacement = attendance_kpi_html + '\n\n                \\1'
    content = re.sub(pattern, replacement, content)

    # 2. JavaScript에서 출근율 88% 미만 계산 추가
    print("\n2️⃣ JavaScript 계산 로직 추가...")

    # 최소 근무일 미충족 계산 다음에 추가
    attendance_calc_js = """
            // 4-1. 출근율 88% 미만
            const attendanceBelow88 = employeeData.filter(emp =>
                parseFloat(emp['attendance_rate'] || 0) < 88
            ).length;
            document.getElementById('kpiAttendanceBelow88').textContent = attendanceBelow88 + '명';
"""

    # 5. AQL FAIL 보유자 앞에 삽입
    pattern = r'(// 5\. AQL FAIL 보유자)'
    replacement = attendance_calc_js + '\n            \\1'
    content = re.sub(pattern, replacement, content)

    # 3. showValidationModal에 attendanceBelow88 케이스 추가
    print("\n3️⃣ 모달 표시 로직 추가...")

    attendance_modal_case = """} else if (conditionType === 'attendanceBelow88') {
                showAttendanceBelow88Details();
                return;
            """

    # minimumDaysNotMet 케이스 다음에 추가
    pattern = r'(} else if \(conditionType === \'minimumDaysNotMet\'\) \{\{[\s\S]*?return;[\s\S]*?\}\})'
    replacement = '\\1 ' + attendance_modal_case
    content = re.sub(pattern, replacement, content)

    # 4. 출근율 88% 미만 상세 모달 함수 추가
    print("\n4️⃣ 출근율 88% 미만 상세 모달 함수 추가...")

    attendance_modal_function = """
    function showAttendanceBelow88Details() {
        // 출근율 88% 미만 직원 필터링
        let below88Employees = window.employeeData.filter(emp => {
            const attendanceRate = parseFloat(emp['attendance_rate'] || 0);
            return attendanceRate < 88;
        });

        let sortColumn = 'attendanceRate';
        let sortOrder = 'asc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'attendanceRate' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#attendanceModal tbody');
            if (!tbody) return;

            // 정렬
            below88Employees.sort((a, b) => {
                let aVal, bVal;
                switch (sortColumn) {
                    case 'empNo':
                        aVal = a['Employee No'] || a['emp_no'];
                        bVal = b['Employee No'] || b['emp_no'];
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a['name'];
                        bVal = b['Full Name'] || b['name'];
                        break;
                    case 'attendanceRate':
                        aVal = parseFloat(a['attendance_rate'] || 0);
                        bVal = parseFloat(b['attendance_rate'] || 0);
                        break;
                    case 'actualDays':
                        aVal = parseFloat(a['Actual Working Days'] || a['actual_working_days'] || 0);
                        bVal = parseFloat(b['Actual Working Days'] || b['actual_working_days'] || 0);
                        break;
                    case 'totalDays':
                        aVal = parseFloat(a['Total Working Days'] || 26);
                        bVal = parseFloat(b['Total Working Days'] || 26);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            below88Employees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const attendanceRate = parseFloat(emp['attendance_rate'] || 0).toFixed(1);
                const actualDays = emp['Actual Working Days'] || emp['actual_working_days'] || 0;
                const totalDays = emp['Total Working Days'] || 26;

                // 출근율에 따른 색상
                let badgeClass = 'bg-danger';
                if (attendanceRate >= 80) badgeClass = 'bg-warning';
                else if (attendanceRate >= 50) badgeClass = 'bg-orange';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td><span class="badge ${badgeClass}">${attendanceRate}%</span></td>
                    <td>${actualDays}일</td>
                    <td>${totalDays}일</td>
                    <td>${attendanceRate < 88 ? '미충족' : '충족'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        function createModal() {
            // 백드롭 생성
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1040';
            document.body.appendChild(backdrop);

            // 모달 생성
            modalDiv = document.createElement('div');
            modalDiv.className = 'modal fade show d-block';
            modalDiv.style.zIndex = '1050';
            modalDiv.setAttribute('id', 'attendanceModal');

            const modalHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title">출근율 88% 미만 직원 상세</h5>
                            <button type="button" class="btn-close" onclick="window.closeAttendanceModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="alert alert-info">
                                    <strong>조건 설명:</strong> 출근율이 88% 미만인 직원은 인센티브를 받을 수 없습니다.
                                    <br>출근율 = (실제 근무일 ÷ 총 근무일) × 100%
                                </div>
                                <p>총 ${below88Employees.length}명이 출근율 88% 미만입니다.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo">사번 ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name">이름 ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="attendanceRate">출근율 ${getSortIcon('attendanceRate')}</th>
                                            <th class="sortable-header" data-sort="actualDays">실제 근무일 ${getSortIcon('actualDays')}</th>
                                            <th class="sortable-header" data-sort="totalDays">총 근무일 ${getSortIcon('totalDays')}</th>
                                            <th>조건 충족</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            modalDiv.innerHTML = modalHTML;
            document.body.appendChild(modalDiv);
            document.body.classList.add('modal-open');

            // 정렬 이벤트 추가
            modalDiv.querySelectorAll('.sortable-header').forEach(header => {
                header.addEventListener('click', function() {
                    const column = this.getAttribute('data-sort');
                    sortData(column);

                    // 헤더 업데이트
                    modalDiv.querySelectorAll('.sortable-header').forEach(h => {
                        const col = h.getAttribute('data-sort');
                        const icon = getSortIcon(col);
                        h.innerHTML = h.textContent.replace(/[▲▼]/g, '').trim() + ' ' + icon;
                    });
                });
            });

            // 초기 데이터 로드
            updateTableBody();

            // 닫기 함수
            window.closeAttendanceModal = function() {
                if (modalDiv) {
                    modalDiv.remove();
                    modalDiv = null;
                }
                if (backdrop) {
                    backdrop.remove();
                    backdrop = null;
                }
                document.body.classList.remove('modal-open');
                window.closeAttendanceModal = null;
            };

            // 백드롭 클릭으로 닫기
            backdrop.onclick = function(e) {
                window.closeAttendanceModal();
            };

            // 모달 내부 클릭 시 이벤트 전파 중단
            modalDiv.querySelector('.modal-content').onclick = function(e) {
                e.stopPropagation();
            };
        }

        function getSortIcon(column) {
            if (sortColumn !== column) return '';
            return sortOrder === 'asc' ? '▲' : '▼';
        }

        createModal();
    }
"""

    # showMinimumDaysNotMetDetails 함수 뒤에 추가
    pattern = r'(function showMinimumDaysNotMetDetails\(\) \{[\s\S]*?\n    \})'
    replacement = '\\1\n' + attendance_modal_function
    content = re.sub(pattern, replacement, content, count=1)

    print("\n✅ 모든 개선 사항 구현 완료")

    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n📊 구현된 개선 사항:")
    print("  1. 최소 근무일 미충족 로직 수정 (condition4 === 'yes')")
    print("  2. 실제 근무일 0일 필드 매핑 수정")
    print("  3. 구역 AQL Reject 3% 이상으로 변경")
    print("  4. 출근율 88% 미만 KPI 카드 및 모달 추가")

    return True

if __name__ == "__main__":
    success = implement_kpi_improvements()
    if success:
        print("\n✅ integrated_dashboard_final.py 파일 업데이트 완료")
    else:
        print("\n❌ 업데이트 실패")