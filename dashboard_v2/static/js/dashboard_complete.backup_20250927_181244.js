// Modal Functions

// Helper function to get incentive amount from employee data
function getIncentiveAmount(emp) {
    // 여러 가능한 인센티브 필드명 확인
    return parseInt(
        emp['Final Incentive amount'] ||
        emp['September_Incentive'] ||
        emp['최종 인센티브 금액'] ||
        emp[`${dashboardMonth}_incentive`] ||
        emp[`${dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1)}_Incentive`] ||
        0
    );
}

    function showTotalWorkingDaysDetails() {
        /* Excel 데이터에서 실제 근무일 정보 가져오기 (Single Source of Truth) */
        let workDays = [];
        let holidays = [];
        let totalWorkingDays = 13; /* Default fallback */

        if (window.excelDashboardData && window.excelDashboardData.attendance) {
            /* 실제 출근 데이터에서 근무일과 휴일 추출 */
            const dailyData = window.excelDashboardData.attendance.daily_data;
            totalWorkingDays = window.excelDashboardData.attendance.total_working_days;

            /* 일별 데이터 분석 */
            for (let day = 1; day <= 19; day++) {
                if (dailyData && dailyData[day]) {
                    if (dailyData[day].is_working_day) {
                        workDays.push(day);
                    } else {
                        holidays.push(day);
                    }
                } else {
                    /* 데이터가 없는 날은 휴일로 처리 */
                    holidays.push(day);
                }
            }
            console.log('실제 근무일:', workDays);
            console.log('휴일:', holidays);
            console.log('총 근무일수:', totalWorkingDays);
        } else {
            /* Fallback: 기본 근무일 데이터 사용 */
            console.warn('Excel 대시보드 데이터가 없습니다. 기본값 사용.');
            workDays = [2,3,4,5,6,9,10,11,12,13,16,17,18,19];
            holidays = [1,7,8,14,15];
        }

        /* 2025년 9월 요일 계산 (9월 1일은 월요일) */
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const getWeekday = (day) => {
            /* 2025년 9월 1일은 월요일(index 1) */
            const firstDayOfWeek = 1; /* 월요일 = 1 */
            const dayIndex = (firstDayOfWeek + day - 1) % 7;
            return weekdays[dayIndex];
        };

        let calendarHTML = '<div class="calendar-grid">';
        for (let day = 1; day <= 19; day++) {
            const isWorkDay = workDays.includes(day);
            const hasNoData = !isWorkDay;
            const dayClass = isWorkDay ? 'work-day' : 'no-data';
            const icon = isWorkDay ? '💼' : '';
            const weekday = getWeekday(day);

            /* Excel 데이터에서 해당 날짜의 출근 인원 수 가져오기 */
            let attendanceCount = '';
            if (isWorkDay && window.excelDashboardData && window.excelDashboardData.attendance && window.excelDashboardData.attendance.daily_data && window.excelDashboardData.attendance.daily_data[day]) {
                const count = window.excelDashboardData.attendance.daily_data[day].count;
                if (count > 0) {
                    attendanceCount = `<div class="attendance-count">${count}명</div>`;
                }
            } else if (hasNoData) {
                attendanceCount = `<div class="attendance-count no-data-text">
                    <i class="fas fa-times-circle"></i>
                    <span>데이터 없음</span>
                </div>`;
            }

            calendarHTML += `
                <div class="calendar-day ${dayClass}">
                    <div class="day-number">${day}</div>
                    <div class="day-weekday">${weekday}요일</div>
                    ${icon ? `<div class="day-icon">${icon}</div>` : ''}
                    ${attendanceCount}
                </div>
            `;
        }
        calendarHTML += '</div>';

        const modalContent = `
            <div class="unified-modal-header">
                <h5 class="unified-modal-title">
                    <i class="fas fa-calendar-alt me-2"></i> 2025년 9월 근무일 현황
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">💼</div>
                            <div class="stat-label">총 근무일 (실제)</div>
                            <div class="stat-value text-primary h3">${totalWorkingDays}일</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">📅</div>
                            <div class="stat-label">총 일수</div>
                            <div class="stat-value text-info h3">19일</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">❌</div>
                            <div class="stat-label">데이터 없음</div>
                            <div class="stat-value text-secondary h3">${holidays.length}일</div>
                        </div>
                    </div>
                </div>
                ${calendarHTML}
                <div class="mt-3">
                    <span class="legend-badge legend-workday">💼 근무일 (출근 데이터 있음)</span>
                    <span class="legend-badge legend-nodata">❌ 데이터 없음</span>
                </div>
            </div>
        `;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // 기존 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 생성 with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    function showZeroWorkingDaysDetails() {
        // Excel 데이터 사용 (Single Source of Truth)
        let zeroWorkingEmployees = [];

        if (window.excelDashboardData && window.excelDashboardData.modal_data && window.excelDashboardData.modal_data.zero_working_days_employees) {
            // Excel에서 이미 필터링된 데이터 사용
            zeroWorkingEmployees = window.excelDashboardData.modal_data.zero_working_days_employees;
        } else if (window.employeeData) {
            // Fallback to employeeData
            zeroWorkingEmployees = window.employeeData.filter(emp => {
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                return actualDays === 0;
            });
        }

        // 정렬 상태 관리
        let sortColumn = 'empNo';
        let sortOrder = 'asc';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            zeroWorkingEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a['Employee No'] || '';
                        bVal = b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a['Full Name'] || '';
                        bVal = b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'totalDays':
                        aVal = a['Total Working Days'] || 15;
                        bVal = b['Total Working Days'] || 15;
                        break;
                    case 'actualDays':
                        aVal = a['Actual Working Days'] || 0;
                        bVal = b['Actual Working Days'] || 0;
                        break;
                    case 'status':
                        const aType = a['Stop_Working_Type'] || 'active';
                        const bType = b['Stop_Working_Type'] || 'active';
                        aVal = aType === 'resigned' ? '퇴사' : aType === 'contract_end' ? '계약종료' : '전체 결근';
                        bVal = bType === 'resigned' ? '퇴사' : bType === 'contract_end' ? '계약종료' : '전체 결근';
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            renderTable();
        }

        function renderTable() {
            let tableRows = '';
            if (zeroWorkingEmployees.length === 0) {
                tableRows = '<tr><td colspan="6" class="text-center py-4"><i class="fas fa-check-circle text-success fa-2x mb-2 d-block"></i>0일 근무자가 없습니다</td></tr>';
            } else {
                tableRows = zeroWorkingEmployees.map(emp => {
                    // Excel에서 가져온 필드 사용 (Single Source of Truth)
                    const actualDays = emp['Actual Working Days'] || 0;
                    const totalDays = emp['Total Working Days'] || 15;
                    const stopDate = emp['Stop working Date'] || '';
                    const workingType = emp['Stop_Working_Type'] || 'active';
                    const position = emp['FINAL QIP POSITION NAME CODE'] || '-';

                    return `
                        <tr class="unified-table-row">
                            <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                            <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                            <td class="unified-table-cell">${position}</td>
                            <td class="unified-table-cell text-center">${totalDays}</td>
                            <td class="unified-table-cell text-center">
                                <span class="badge bg-danger">${actualDays}</span>
                            </td>
                            <td class="unified-table-cell text-center">
                                <span class="badge ${workingType === 'resigned' ? 'bg-warning text-dark' : workingType === 'contract_end' ? 'bg-info text-white' : 'bg-danger'}">
                                    ${workingType === 'resigned' ? `퇴사 (${stopDate})` : workingType === 'contract_end' ? `계약종료예정 (${stopDate})` : '전체 결근'}
                                </span>
                            </td>
                        </tr>
                    `;
                }).join('');
            }

            const modalContent = `
                <div class="unified-modal-header">
                    <h5 class="unified-modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i> 0일 근무자 상세
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-light border-start border-4 border-danger mb-3">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-info-circle text-danger me-2"></i>
                            <span>실제 근무일이 0일인 직원 목록입니다.</span>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="unified-table-header">
                                <tr>
                                    <th class="sortable-header ${sortColumn === 'empNo' ? sortOrder : ''}" onclick="window.zeroModalSort('empNo')">사번</th>
                                    <th class="sortable-header ${sortColumn === 'name' ? sortOrder : ''}" onclick="window.zeroModalSort('name')">이름</th>
                                    <th class="sortable-header ${sortColumn === 'position' ? sortOrder : ''}" onclick="window.zeroModalSort('position')">직책</th>
                                    <th class="text-center sortable-header ${sortColumn === 'totalDays' ? sortOrder : ''}" onclick="window.zeroModalSort('totalDays')">총 근무일</th>
                                    <th class="text-center sortable-header ${sortColumn === 'actualDays' ? sortOrder : ''}" onclick="window.zeroModalSort('actualDays')">실 근무일</th>
                                    <th class="text-center sortable-header ${sortColumn === 'status' ? sortOrder : ''}" onclick="window.zeroModalSort('status')">상태</th>
                                </tr>
                            </thead>
                            <tbody>${tableRows}</tbody>
                        </table>
                    </div>
                </div>
            `;

            // 모달이 없으면 생성
            let modal = document.getElementById('detailModal');
            if (!modal) {
                const modalHTML = `
                    <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                        <div class="modal-dialog modal-xl">
                            <div class="modal-content" id="detailModalContent"></div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHTML);
                modal = document.getElementById('detailModal');
            }

            document.getElementById('detailModalContent').innerHTML = modalContent;
        }

        // 전역 정렬 함수 등록
        window.zeroModalSort = sortData;

        // 초기 렌더링
        renderTable();

        // Bootstrap 5 Modal 처리
        const modalElement = document.getElementById('detailModal');

        // 기존 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 생성 with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    function showAbsentWithoutInformDetails() {
        let absentEmployees = window.employeeData.filter(emp => {
            const unapproved = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);
            return unapproved >= 1;
        });

        // 정렬 상태 관리
        let sortColumn = 'days';
        let sortOrder = 'desc';

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            absentEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a.employee_no || a['Employee No'] || '';
                        bVal = b.employee_no || b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a.full_name || a['Full Name'] || '';
                        bVal = b.full_name || b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a.qip_position || a['QIP POSITION 1ST  NAME'] || '';
                        bVal = b.qip_position || b['QIP POSITION 1ST  NAME'] || '';
                        break;
                    case 'days':
                        aVal = parseFloat(a.unapproved_absences || a['Unapproved Absences'] || 0);
                        bVal = parseFloat(b.unapproved_absences || b['Unapproved Absences'] || 0);
                        break;
                    case 'status':
                        const aDays = parseFloat(a.unapproved_absences || a['Unapproved Absences'] || 0);
                        const bDays = parseFloat(b.unapproved_absences || b['Unapproved Absences'] || 0);
                        aVal = aDays > 2 ? 3 : (aDays === 2 ? 2 : 1); // 제외=3, 경고=2, 주의=1
                        bVal = bDays > 2 ? 3 : (bDays === 2 ? 2 : 1);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            renderTable();
        }

        function renderTable() {

        let tableRows = absentEmployees.map(emp => {
            const days = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);

            // 개선된 색상 체계와 아이콘
            let rowStyle = '';
            let daysBadgeClass = '';
            let statusBadge = '';
            let statusIcon = '';

            if (days > 2) {
                // 3일 이상 - 인센티브 제외 (위험)
                rowStyle = 'background: linear-gradient(90deg, #fff5f5 0%, #ffe0e0 100%); border-left: 4px solid #dc3545;';
                daysBadgeClass = 'bg-danger text-white fw-bold';
                statusBadge = `
                    <div class="d-flex align-items-center justify-content-center">
                        <span class="badge bg-danger px-3 py-2">
                            <i class="fas fa-ban me-1"></i>
                            인센티브 제외
                        </span>
                    </div>`;
                statusIcon = '<i class="fas fa-exclamation-circle text-danger me-2"></i>';
            } else if (days === 2) {
                // 2일 - 경고 (주의)
                rowStyle = 'background: linear-gradient(90deg, #fffaf0 0%, #fff4e0 100%); border-left: 4px solid #fd7e14;';
                daysBadgeClass = 'bg-warning text-dark fw-bold';
                statusBadge = `
                    <div class="d-flex align-items-center justify-content-center">
                        <span class="badge bg-warning text-dark px-3 py-2">
                            <i class="fas fa-exclamation-triangle me-1"></i>
                            경고
                        </span>
                    </div>`;
                statusIcon = '<i class="fas fa-exclamation-triangle text-warning me-2"></i>';
            } else {
                // 1일 - 주의
                rowStyle = 'background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%); border-left: 4px solid #ffc107;';
                daysBadgeClass = 'bg-info text-white';
                statusBadge = `
                    <div class="d-flex align-items-center justify-content-center">
                        <span class="badge bg-info px-3 py-2">
                            <i class="fas fa-info-circle me-1"></i>
                            주의
                        </span>
                    </div>`;
                statusIcon = '<i class="fas fa-info-circle text-info me-2"></i>';
            }

            return `
                <tr style="${rowStyle} transition: all 0.3s ease;"
                    onmouseover="this.style.transform='translateX(5px)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';"
                    onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='none';">
                    <td style="width: 15%; padding: 12px;">
                        <span class="text-muted small">No.</span>
                        <div class="fw-semibold">${emp.employee_no || emp['Employee No'] || ''}</div>
                    </td>
                    <td style="width: 25%; padding: 12px;">
                        ${statusIcon}
                        <span class="fw-semibold">${emp.full_name || emp['Full Name'] || ''}</span>
                    </td>
                    <td style="width: 25%; padding: 12px;">
                        <span class="text-secondary">${emp.qip_position || emp['QIP POSITION 1ST  NAME'] || '-'}</span>
                    </td>
                    <td style="width: 15%; padding: 12px; text-align: center;">
                        <div class="d-flex flex-column align-items-center">
                            <span class="badge ${daysBadgeClass} px-3 py-2 fs-6">
                                ${days}일
                            </span>
                            ${days > 2 ? '<small class="text-danger mt-1">초과</small>' : ''}
                        </div>
                    </td>
                    <td style="width: 20%; padding: 12px; text-align: center;">
                        ${statusBadge}
                    </td>
                </tr>
            `;
        }).join('') || `
            <tr>
                <td colspan="5" class="text-center py-5">
                    <i class="fas fa-check-circle text-success fa-3x mb-3"></i>
                    <div class="text-muted">무단결근자가 없습니다</div>
                </td>
            </tr>`;

        // 통계 섹션 추가
        const total = absentEmployees.length;
        const excluded = absentEmployees.filter(emp => {
            const days = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);
            return days > 2;
        }).length;
        const warning = absentEmployees.filter(emp => {
            const days = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);
            return days === 2;
        }).length;
        const caution = total - excluded - warning;

        const statsSection = total > 0 ? `
            <div class="alert alert-light border-start border-4 border-warning mb-4">
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">전체</span>
                            <span class="fs-4 fw-bold text-dark">${total}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">주의 (1일)</span>
                            <span class="fs-4 fw-bold text-info">${caution}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">경고 (2일)</span>
                            <span class="fs-4 fw-bold text-warning">${warning}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex flex-column">
                            <span class="text-muted small">제외 (3일+)</span>
                            <span class="fs-4 fw-bold text-danger">${excluded}</span>
                        </div>
                    </div>
                </div>
            </div>
        ` : '';

        const modalContent = `
            <div class="modal-header" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-bottom: 3px solid #2196f3;">
                <h5 class="modal-title" style="color: #1565c0; font-weight: 700;">
                    <i class="fas fa-user-times me-2" style="color: #1976d2;"></i>무단결근 직원 상세
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                ${statsSection}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="unified-table-header">
                            <tr>
                                <th class="sortable-header ${sortColumn === 'empNo' ? sortOrder : ''}" onclick="window.absentModalSort('empNo')" style="width: 15%;">
                                    사번
                                </th>
                                <th class="sortable-header ${sortColumn === 'name' ? sortOrder : ''}" onclick="window.absentModalSort('name')" style="width: 25%;">
                                    이름
                                </th>
                                <th class="sortable-header ${sortColumn === 'position' ? sortOrder : ''}" onclick="window.absentModalSort('position')" style="width: 25%;">
                                    직책
                                </th>
                                <th class="sortable-header text-center ${sortColumn === 'days' ? sortOrder : ''}" onclick="window.absentModalSort('days')" style="width: 15%;">
                                    <div style="line-height: 1.2;">
                                        <div>무단결근</div>
                                        <div style="font-size: 0.75rem; font-weight: 400; color: #757575;">(일수)</div>
                                    </div>
                                </th>
                                <th class="sortable-header text-center ${sortColumn === 'status' ? sortOrder : ''}" onclick="window.absentModalSort('status')" style="width: 20%;">
                                    상태
                                </th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
            </div>
            <div class="modal-footer" style="background: #fafafa; border-top: 1px solid #e0e0e0;">
                <small style="color: #616161; font-weight: 500;">
                    <i class="fas fa-info-circle me-1" style="color: #9e9e9e;"></i>
                    무단결근 3일 이상 시 인센티브가 자동 제외됩니다
                </small>
            </div>
        `;

            document.getElementById('detailModalContent').innerHTML = modalContent;
        }

        // 전역 정렬 함수 등록
        window.absentModalSort = sortData;

        // 초기 정렬 상태로 렌더링
        sortData('days');

        // 모달 표시 처리
        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // 기존 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 생성 with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    function showMinimumDaysNotMetDetails() {
        // Excel의 Minimum_Working_Days_Required 사용 (Single Source of Truth)
        const firstEmp = window.employeeData[0] || {};
        const minimumRequired = firstEmp['Minimum_Working_Days_Required'] || 12;

        // Excel의 Minimum_Days_Met 필드 사용 (Single Source of Truth)
        let notMetEmployees = window.employeeData.filter(emp => {
            // 방법 1: Excel의 Minimum_Days_Met 필드 직접 사용
            const minimumDaysMet = emp['Minimum_Days_Met'];
            if (minimumDaysMet !== undefined) {
                return minimumDaysMet === false || minimumDaysMet === 'False' || minimumDaysMet === 0;
            }
            // 방법 2: Fallback - condition4 필드 사용 (yes = 미충족)
            if (emp['condition4'] !== undefined) {
                return emp['condition4'] === 'yes';
            }
            // 방법 3: Fallback - 실제 계산
            const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
            return actualDays < minimumRequired;
        });

        // 정렬 상태 관리
        let sortColumn = 'actualDays';
        let sortOrder = 'asc';

        function renderTable() {
            // 정렬 적용
            const sorted = [...notMetEmployees].sort((a, b) => {
                let aVal, bVal;

                switch(sortColumn) {
                    case 'empNo':
                        aVal = a.employee_no || a['Employee No'] || '';
                        bVal = b.employee_no || b['Employee No'] || '';
                        break;
                    case 'name':
                        aVal = a.full_name || a['Full Name'] || '';
                        bVal = b.full_name || b['Full Name'] || '';
                        break;
                    case 'position':
                        aVal = a.qip_position || a['QIP POSITION 1ST  NAME'] || '';
                        bVal = b.qip_position || b['QIP POSITION 1ST  NAME'] || '';
                        break;
                    case 'actualDays':
                        aVal = parseFloat(a.actual_working_days || a['Actual Working Days'] || 0);
                        bVal = parseFloat(b.actual_working_days || b['Actual Working Days'] || 0);
                        break;
                    case 'shortage':
                        aVal = minimumRequired - parseFloat(a.actual_working_days || a['Actual Working Days'] || 0);
                        bVal = minimumRequired - parseFloat(b.actual_working_days || b['Actual Working Days'] || 0);
                        break;
                    case 'status':
                        aVal = parseFloat(a.actual_working_days || a['Actual Working Days'] || 0) >= minimumRequired ? 1 : 0;
                        bVal = parseFloat(b.actual_working_days || b['Actual Working Days'] || 0) >= minimumRequired ? 1 : 0;
                        break;
                    default:
                        aVal = 0;
                        bVal = 0;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                } else {
                    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
                }
            });

            let tableRows = sorted.map(emp => {
                const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
                const shortage = minimumRequired - actualDays;
                const percentage = (actualDays / minimumRequired * 100).toFixed(1);

                // 더 명확한 색상 구분
                let progressColor = 'danger';
                let textColor = 'text-white';
                if (percentage >= 75) {
                    progressColor = 'info';
                    textColor = 'text-dark';  // 하늘색 배경에 검은색 텍스트
                } else if (percentage >= 50) {
                    progressColor = 'warning';
                    textColor = 'text-dark';  // 노란색 배경에 검은색 텍스트
                }
                // percentage < 50은 danger (빨간색) 유지

                const isMet = actualDays >= minimumRequired;

                return `
                    <tr class="unified-table-row">
                        <td style="padding: 12px 8px; font-weight: 500;">${emp.employee_no || emp['Employee No'] || ''}</td>
                        <td style="padding: 12px 8px; font-weight: 500;">${emp.full_name || emp['Full Name'] || ''}</td>
                        <td style="padding: 12px 8px; font-size: 13px;">${emp.qip_position || emp['QIP POSITION 1ST  NAME'] || '-'}</td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <div class="d-flex align-items-center justify-content-center">
                                <span class="badge bg-${progressColor} ${textColor}" style="font-size: 14px; padding: 8px 12px;">
                                    ${actualDays}일
                                </span>
                            </div>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge bg-primary" style="font-size: 14px; padding: 8px 12px;">${minimumRequired}일</span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge bg-danger" style="font-size: 14px; padding: 8px 12px;">-${shortage}일</span>
                        </td>
                        <td class="text-center" style="padding: 10px 8px;">
                            <span class="badge ${isMet ? 'bg-success' : 'bg-danger'}" style="font-size: 13px; padding: 6px 10px;">
                                ${isMet ? '충족' : '미충족'}
                            </span>
                        </td>
                    </tr>
                `;
            }).join('') || `<tr><td colspan="7" class="text-center py-4"><i class="fas fa-check-circle text-success fa-2x mb-2 d-block"></i>모든 직원이 최소 근무일(${minimumRequired}일)을 충족했습니다</td></tr>`;

            return tableRows;
        }

        function setSorting(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            const tbody = document.querySelector('#detailModal tbody');
            if (tbody) {
                tbody.innerHTML = renderTable();
            }

            // 헤더 클래스 업데이트
            document.querySelectorAll('#detailModal .sortable-header').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            const currentHeader = document.querySelector(`#detailModal .sortable-header[data-sort="${column}"]`);
            if (currentHeader) {
                currentHeader.classList.add(sortOrder);
            }
        }

        const modalContent = `
            <div class="unified-modal-header">
                <h5 class="unified-modal-title">
                    <i class="fas fa-clock me-2"></i> 최소 근무일 미충족 직원 상세
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="alert alert-light border-start border-4 border-warning mb-3">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-info-circle text-warning me-2"></i>
                        <span>최소 요구 근무일: ${minimumRequired}일</span>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover" id="minimumDaysTable" style="font-size: 14px;">
                        <thead class="unified-table-header">
                            <tr>
                                <th class="sortable-header" data-sort="empNo" onclick="window.minDaysSort('empNo')" style="min-width: 100px;">사번</th>
                                <th class="sortable-header" data-sort="name" onclick="window.minDaysSort('name')" style="min-width: 130px;">이름</th>
                                <th class="sortable-header" data-sort="position" onclick="window.minDaysSort('position')" style="min-width: 150px;">직책</th>
                                <th class="text-center sortable-header asc" data-sort="actualDays" onclick="window.minDaysSort('actualDays')" style="min-width: 110px;">실제<br>근무일</th>
                                <th class="text-center" style="min-width: 80px;">최소<br>요구</th>
                                <th class="text-center sortable-header" data-sort="shortage" onclick="window.minDaysSort('shortage')" style="min-width: 70px;">부족</th>
                                <th class="text-center sortable-header" data-sort="status" onclick="window.minDaysSort('status')" style="min-width: 80px;">상태</th>
                            </tr>
                        </thead>
                        <tbody>${renderTable()}</tbody>
                    </table>
                </div>
            </div>
        `;

        // 전역 정렬 함수 설정
        window.minDaysSort = setSorting;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        /* Bootstrap 5 Modal 처리 */
        const modalElement = document.getElementById('detailModal');

        // 기존 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 생성 with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    function showAttendanceBelow88Details() {
        // 출근율 88% 미만 직원 필터링
        let below88Employees = window.employeeData.filter(emp => {
            const attendanceRate = parseFloat(emp['attendance_rate'] || 0);
            return attendanceRate < 88;
        });

        let sortColumn = 'attendanceRate';
        let sortOrder = 'asc';

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
                        aVal = parseFloat(a['Total Working Days'] || 13);
                        bVal = parseFloat(b['Total Working Days'] || 13);
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
                const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
                const totalDays = parseFloat(emp['Total Working Days'] || 13);

                // 출근율에 따른 색상과 텍스트 색상 - 더 명확한 구분
                let badgeClass = 'bg-danger';
                let textColor = 'text-white';
                let customStyle = '';

                if (attendanceRate >= 70) {
                    badgeClass = 'bg-info';  // 70% 이상은 하늘색
                    textColor = 'text-dark';
                } else if (attendanceRate >= 50) {
                    badgeClass = 'bg-warning';  // 50-70%는 노란색
                    textColor = 'text-dark';
                } else if (attendanceRate >= 30) {
                    // 30-50%는 주황색 (커스텀 스타일)
                    badgeClass = '';
                    customStyle = 'background-color: #ff6b35 !important; color: white !important;';
                }
                // attendanceRate < 30은 bg-danger (빨간색) 유지

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="padding: 10px; font-weight: 500;">${empNo}</td>
                    <td style="padding: 10px; font-weight: 500;">${name}</td>
                    <td style="padding: 10px;"><span class="badge ${badgeClass} ${textColor}" style="font-size: 14px; padding: 6px 10px; ${customStyle}">${attendanceRate}%</span></td>
                    <td style="padding: 10px;">${actualDays}일</td>
                    <td style="padding: 10px;">${totalDays}일</td>
                    <td style="padding: 10px;"><span class="badge ${attendanceRate < 88 ? 'bg-danger' : 'bg-success'}" style="font-size: 13px; padding: 4px 8px;">${attendanceRate < 88 ? '미충족' : '충족'}</span></td>
                `;
                tbody.appendChild(row);
            });
        }

        function getSortIcon(column) {
            if (sortColumn !== column) return '';
            return sortOrder === 'asc' ? '▲' : '▼';
        }

        // Bootstrap 모달 HTML 생성
        const modalHTML = `
            <div class="modal fade" id="attendanceModal" tabindex="-1" role="dialog" aria-labelledby="attendanceModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-xl" role="document">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title" id="attendanceModalLabel">
                                <i class="fas fa-percentage me-2"></i> 출근율 88% 미만 직원 상세
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
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
                                <table class="table table-hover" style="font-size: 14px;">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo" style="min-width: 100px; padding: 12px; cursor: pointer;">사번 ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name" style="min-width: 130px; padding: 12px; cursor: pointer;">이름 ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="attendanceRate" style="min-width: 100px; padding: 12px; cursor: pointer;">출근율 ${getSortIcon('attendanceRate')}</th>
                                            <th class="sortable-header" data-sort="actualDays" style="min-width: 110px; padding: 12px; cursor: pointer;">실제<br>근무일 ${getSortIcon('actualDays')}</th>
                                            <th class="sortable-header" data-sort="totalDays" style="min-width: 100px; padding: 12px; cursor: pointer;">총<br>근무일 ${getSortIcon('totalDays')}</th>
                                            <th style="min-width: 90px; padding: 12px;">조건<br>충족</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 기존 모달이 있으면 제거
        const existingModal = document.getElementById('attendanceModal');
        if (existingModal) {
            const existingBsModal = bootstrap.Modal.getInstance(existingModal);
            if (existingBsModal) {
                existingBsModal.dispose();
            }
            existingModal.remove();
        }

        // 모달을 body에 추가
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // 모달 엘리먼트 참조
        const modalElement = document.getElementById('attendanceModal');

        // Bootstrap 모달 인스턴스 생성 및 표시
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기 활성화
            keyboard: true,      // ESC 키로 닫기 활성화
            focus: true
        });

        // 정렬 이벤트 추가
        modalElement.querySelectorAll('.sortable-header').forEach(header => {
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sort');
                sortData(column);

                // 헤더 업데이트
                modalElement.querySelectorAll('.sortable-header').forEach(h => {
                    const col = h.getAttribute('data-sort');
                    const icon = getSortIcon(col);
                    h.innerHTML = h.textContent.replace(/[▲▼]/g, '').trim() + ' ' + icon;
                });
            });
        });

        // 초기 데이터 로드
        updateTableBody();

        // 모달 표시
        bsModal.show();

        // 백드롭 클릭 이벤트 명시적 처리 (출근율 모달)
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.cursor = 'pointer';
                backdrop.addEventListener('click', function(e) {
                    if (e.target === backdrop) {
                        bsModal.hide();
                    }
                });
            }
        }, 100);

        // 모달이 닫힐 때 DOM에서 제거
        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.remove();
        });
    }


    function showConsecutiveAqlFailDetails() {
        // 3개월 연속 실패자와 2개월 연속 실패자 분리
        const threeMonthFails = window.employeeData.filter(emp =>
            emp['Continuous_FAIL'] === 'YES_3MONTHS'
        );

        const twoMonthFails = window.employeeData.filter(emp =>
            emp['Continuous_FAIL'] && emp['Continuous_FAIL'].includes('2MONTHS')
        );

        // Custom HTML for this specific modal
        const existingModal = document.getElementById('consecutiveAqlFailModal');
        if (existingModal) {
            existingModal.remove();
        }

        let modalHTML = `
            <div id="consecutiveAqlFailModal" class="modal" style="display: block; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
                <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 0; border: 1px solid #888; width: 80%; max-width: 1200px; border-radius: 10px;">
                    <div class="modal-header" style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px 10px 0 0;">
                        <span class="close" onclick="document.getElementById('consecutiveAqlFailModal').remove()" style="color: white; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
                        <h2>3개월 연속 AQL FAIL 현황</h2>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
        `;

        // 3개월 연속 실패 섹션
        modalHTML += '<div class="section-container" style="margin-bottom: 30px;">';
        modalHTML += '<h3 style="color: #c0392b; margin-bottom: 15px;">🔴 3개월 연속 AQL 실패</h3>';

        if (threeMonthFails.length === 0) {
            modalHTML += '<div class="alert alert-success" style="padding: 15px; background: #d4edda; color: #155724; border-radius: 5px;">';
            modalHTML += '✅ 현재 3개월 연속 실패자가 없습니다.';
            modalHTML += '</div>';
        } else {
            modalHTML += '<table style="width: 100%; border-collapse: collapse;">';
            modalHTML += '<thead><tr style="background: #f8f9fa;">';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직원번호</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">이름</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직책</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직속상사</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">실패 패턴</th>';
            modalHTML += '</tr></thead><tbody>';

            threeMonthFails.forEach(emp => {
                modalHTML += '<tr>';
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Employee No'] || emp['emp_no']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Full Name'] || emp['name']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['position'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['boss_name'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['AQL_Fail_Pattern'] || 'Jul-Aug-Sep'}</td>`;
                modalHTML += '</tr>';
            });

            modalHTML += '</tbody></table>';
        }
        modalHTML += '</div>';

        // 2개월 연속 실패 섹션
        modalHTML += '<div class="section-container">';
        modalHTML += '<h3 style="color: #e67e22; margin-bottom: 15px;">⚠️ 2개월 연속 AQL 실패 - 주의 관찰 대상</h3>';

        if (twoMonthFails.length === 0) {
            modalHTML += '<div class="alert alert-info" style="padding: 15px; background: #d1ecf1; color: #0c5460; border-radius: 5px;">';
            modalHTML += '현재 2개월 연속 실패자가 없습니다.';
            modalHTML += '</div>';
        } else {
            modalHTML += '<table style="width: 100%; border-collapse: collapse;">';
            modalHTML += '<thead><tr style="background: #f8f9fa;">';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직원번호</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">이름</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직책</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">직속상사</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">실패 패턴</th>';
            modalHTML += '<th style="border: 1px solid #dee2e6; padding: 8px;">위험도</th>';
            modalHTML += '</tr></thead><tbody>';

            // 8-9월 연속 실패자를 먼저 표시 (높은 위험)
            const augSepFails = twoMonthFails.filter(emp => emp['Continuous_FAIL'].includes('AUG_SEP'));
            const julAugFails = twoMonthFails.filter(emp => emp['Continuous_FAIL'].includes('JUL_AUG'));

            augSepFails.forEach(emp => {
                modalHTML += '<tr style="background: #fff5f5;">';
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Employee No'] || emp['emp_no']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Full Name'] || emp['name']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['QIP POSITION 1ST  NAME'] || emp['position'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['MST direct boss name'] || emp['boss_name'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['AQL_Fail_Pattern'] || 'Aug-Sep'}</td>`;
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;"><span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px;">🔴 높음</span></td>';
                modalHTML += '</tr>';
            });

            julAugFails.forEach(emp => {
                modalHTML += '<tr>';
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Employee No'] || emp['emp_no']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['Full Name'] || emp['name']}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['QIP POSITION 1ST  NAME'] || emp['position'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['MST direct boss name'] || emp['boss_name'] || '-'}</td>`;
                modalHTML += `<td style="border: 1px solid #dee2e6; padding: 8px;">${emp['AQL_Fail_Pattern'] || 'Jul-Aug'}</td>`;
                modalHTML += '<td style="border: 1px solid #dee2e6; padding: 8px;"><span style="background: #ffc107; color: #212529; padding: 2px 8px; border-radius: 3px;">🟡 보통</span></td>';
                modalHTML += '</tr>';
            });

            modalHTML += '</tbody></table>';

            // 범례 추가
            modalHTML += '<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">';
            modalHTML += '<strong>위험도 설명:</strong><br>';
            modalHTML += '🔴 <strong>높음 (Aug-Sep):</strong> 10월에 실패 시 3개월 연속 실패가 됩니다. 즉시 조치 필요!<br>';
            modalHTML += '🟡 <strong>보통 (Jul-Aug):</strong> 9월에 회복했지만 지속적인 모니터링이 필요합니다.';
            modalHTML += '</div>';
        }
        modalHTML += '</div>';

        // 요약 통계
        modalHTML += '<div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 5px;">';
        modalHTML += '<strong>📊 요약:</strong><br>';
        modalHTML += `• 3개월 연속 실패: ${threeMonthFails.length}명<br>`;
        modalHTML += `• 2개월 연속 실패: ${twoMonthFails.length}명<br>`;
        const augSepCount = twoMonthFails.filter(emp => emp['Continuous_FAIL'].includes('AUG_SEP')).length;
        modalHTML += `&nbsp;&nbsp;- 8-9월 연속 (높은 위험): ${augSepCount}명<br>`;
        modalHTML += `&nbsp;&nbsp;- 7-8월 연속 (모니터링): ${twoMonthFails.length - augSepCount}명`;
        modalHTML += '</div>';

        // Close modal HTML
        modalHTML += `
                    </div>
                </div>
            </div>
        `;

        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add click outside to close functionality
        const modal = document.getElementById('consecutiveAqlFailModal');
        modal.onclick = function(event) {
            if (event.target === modal) {
                modal.remove();
            }
        };
    }

    function showAqlFailDetails() {
        // AQL FAIL이 있는 직원 필터링
        let aqlFailEmployees = window.employeeData.filter(emp => {
            const aqlFailures = parseFloat(emp['September AQL Failures'] || emp['aql_failures'] || 0);
            return aqlFailures > 0;
        });

        // 정렬 상태 관리
        let sortColumn = 'failPercent';
        let sortOrder = 'desc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            console.log('sortData called with column:', column, 'current sortColumn:', sortColumn, 'sortOrder:', sortOrder);

            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = 'asc';
            }

            aqlFailEmployees.sort((a, b) => {
                let aVal, bVal;

                switch(column) {
                    case 'empNo':
                        aVal = a['Employee No'] || a.employee_no || '';
                        bVal = b['Employee No'] || b.employee_no || '';
                        break;
                    case 'name':
                        aVal = a['Full Name'] || a.full_name || '';
                        bVal = b['Full Name'] || b.full_name || '';
                        break;
                    case 'manager':
                        // 모든 가능한 직속 상사 필드 체크
                        aVal = a['MST direct boss name'] || a['direct boss name'] || a['Direct Boss Name'] || a.direct_boss_name || '-';
                        bVal = b['MST direct boss name'] || b['direct boss name'] || b['Direct Boss Name'] || b.direct_boss_name || '-';
                        break;
                    case 'passCount':
                        // 엑셀에서 직접 PASS 횟수 가져오기
                        aVal = parseFloat(a['AQL_Pass_Count'] || 0);
                        bVal = parseFloat(b['AQL_Pass_Count'] || 0);
                        break;
                    case 'failures':
                        aVal = parseFloat(a['September AQL Failures'] || a['aql_failures'] || 0);
                        bVal = parseFloat(b['September AQL Failures'] || b['aql_failures'] || 0);
                        break;
                    case 'failPercent':
                        // 엑셀에서 직접 FAIL % 가져오기
                        aVal = parseFloat(a['AQL_Fail_Percent'] || 0);
                        bVal = parseFloat(b['AQL_Fail_Percent'] || 0);
                        break;
                    default:
                        aVal = '';
                        bVal = '';
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
                } else {
                    return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal);
                }
            });

            updateTableBody();
        }

        function updateTableBody() {
            // 테이블 바디만 업데이트 (이벤트 리스너 유지)
            const tbody = document.querySelector('#detailModal tbody');
            if (!tbody) return;

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp['September AQL Failures'] || emp['aql_failures'] || 0);
                // 모든 가능한 직속 상사 필드 체크
                const managerName = emp['MST direct boss name'] || emp['direct boss name'] || emp['Direct Boss Name'] || emp.direct_boss_name || '-';

                // 엑셀 파일에서 AQL 통계 데이터 가져오기 (Single Source of Truth)
                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                // 실패율에 따른 색상 구분
                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = `${failPercent}% (심각)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = `${failPercent}% (경고)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || emp.employee_no || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || emp.full_name || ''}</td>
                        <td class="unified-table-cell">${managerName}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${passCount}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${failures}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${failBadgeText}</span>
                        </td>
                    </tr>
                `;
            }).join('');

            tbody.innerHTML = tableRows || '<tr><td colspan="6" class="text-center text-muted">AQL FAIL이 없습니다</td></tr>';

            // 정렬 아이콘 업데이트
            document.querySelectorAll('#detailModal th[data-sort]').forEach(th => {
                const column = th.getAttribute('data-sort');
                const sortIcon = th.querySelector('.sort-icon');
                if (sortIcon) {
                    if (sortColumn === column) {
                        sortIcon.textContent = sortOrder === 'asc' ? ' ▲' : ' ▼';
                    } else {
                        sortIcon.textContent = ' ⇅';
                    }
                }
            });
        }

        function createModal() {
            // 정렬 아이콘 업데이트 함수
            function getSortIcon(column) {
                if (sortColumn === column) {
                    return sortOrder === 'asc' ? ' ▲' : ' ▼';
                }
                return ' ⇅';
            }

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp['September AQL Failures'] || emp['aql_failures'] || 0);
                // 모든 가능한 직속 상사 필드 체크
                const managerName = emp['MST direct boss name'] || emp['direct boss name'] || emp['Direct Boss Name'] || emp.direct_boss_name || '-';

                // 엑셀 파일에서 AQL 통계 데이터 가져오기
                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                // 실패율에 따른 색상 구분
                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = `${failPercent}% (심각)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = `${failPercent}% (경고)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || emp.employee_no || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || emp.full_name || ''}</td>
                        <td class="unified-table-cell">${managerName}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${passCount}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${failures}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${failBadgeText}</span>
                        </td>
                    </tr>
                `;
            }).join('');

            let modalContent = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                AQL FAIL 보유자 상세
                            </h5>
                            <button type="button" class="btn-close" onclick="window.closeAqlModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning d-flex align-items-center mb-3">
                                <i class="fas fa-info-circle me-2"></i>
                                <div>
                                    <strong>AQL (Acceptable Quality Level) FAIL</strong>은 품질 검사에서 불합격을 받은 경우를 의미합니다.<br>
                                    총 <strong>${aqlFailEmployees.length}명</strong>의 직원이 9월에 AQL FAIL을 기록했습니다.
                                </div>
                            </div>

                            <table class="table table-hover">
                                <thead class="unified-table-header">
                                    <tr>
                                        <th style="cursor: pointer;" data-sort="empNo">
                                            사번<span class="sort-icon">${getSortIcon('empNo')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="name">
                                            이름<span class="sort-icon">${getSortIcon('name')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="manager">
                                            직속 상사<span class="sort-icon">${getSortIcon('manager')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="passCount">
                                            AQL PASS<span class="sort-icon">${getSortIcon('passCount')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failures">
                                            AQL FAIL<span class="sort-icon">${getSortIcon('failures')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failPercent">
                                            FAIL %<span class="sort-icon">${getSortIcon('failPercent')}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableRows || '<tr><td colspan="6" class="text-center text-muted">AQL FAIL이 없습니다</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            // 기존 모달 제거
            const existingModal = document.getElementById('detailModal');
            if (existingModal) {
                existingModal.remove();
            }

            // 백드롭 제거
            const existingBackdrop = document.querySelector('.modal-backdrop');
            if (existingBackdrop) {
                existingBackdrop.remove();
            }

            // 새 모달 생성
            modalDiv = document.createElement('div');
            modalDiv.className = 'modal fade show';
            modalDiv.id = 'detailModal';
            modalDiv.style.display = 'block';
            modalDiv.style.position = 'fixed';
            modalDiv.style.top = '0';
            modalDiv.style.left = '0';
            modalDiv.style.width = '100%';
            modalDiv.style.height = '100%';
            modalDiv.style.zIndex = '1050';
            modalDiv.innerHTML = modalContent;
            document.body.appendChild(modalDiv);

            // 백드롭 추가
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.position = 'fixed';
            backdrop.style.top = '0';
            backdrop.style.left = '0';
            backdrop.style.width = '100%';
            backdrop.style.height = '100%';
            backdrop.style.zIndex = '1040';
            backdrop.style.backgroundColor = 'rgba(0,0,0,0.5)';
            document.body.appendChild(backdrop);

            // body 스타일 조정
            document.body.classList.add('modal-open');
            document.body.style.overflow = 'hidden';
            document.body.style.paddingRight = '17px';

            // 전역 closeModal 함수 정의
            window.closeAqlModal = function() {
                console.log('Closing modal...');
                if (modalDiv) modalDiv.remove();
                if (backdrop) backdrop.remove();
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                delete window.closeAqlModal;
            };

            // 백드롭 클릭 이벤트 (모달 밖 클릭으로 닫기)
            backdrop.onclick = function(e) {
                if (e.target === backdrop) {
                    console.log('Backdrop clicked');
                    window.closeAqlModal();
                }
            };

            // 모달 자체 클릭 이벤트 (모달 콘텐츠 밖 클릭 시 닫기)
            modalDiv.onclick = function(e) {
                if (e.target === modalDiv) {
                    console.log('Modal outer area clicked');
                    window.closeAqlModal();
                }
            };

            // 정렬 헤더 클릭 이벤트
            setTimeout(() => {
                const sortHeaders = document.querySelectorAll('#detailModal th[data-sort]');
                sortHeaders.forEach(header => {
                    header.onclick = function(e) {
                        e.stopPropagation();
                        const column = this.getAttribute('data-sort');
                        console.log('Header clicked:', column);
                        sortData(column);
                    };
                });
            }, 100);
        }

        // 초기 모달 생성
        createModal();
    }

    // Area AQL Reject Rate 상세 모달 (조건 7번, 8번 구분 표시)
    function showAreaRejectRateDetails() {
        // 구역 매핑 데이터
        const areaMapping = {
            '618110087': 'Building C',
            '623080475': 'Building C',
            '619070185': 'Building D',
            '620070020': 'Building D',
            '620070013': 'Building A',
            '618060092': 'Building B & Repacking',
            '620080295': 'All Buildings',
            '618030241': 'All Buildings',  // 전체 구역이 아닌 All Buildings로 변경
            '618110097': 'All Buildings',  // 전체 구역이 아닌 All Buildings로 변경
            '620120386': 'All Buildings'   // 전체 구역이 아닌 All Buildings로 변경
        };

        // AQL Building 정보를 사용하여 매핑 확장
        window.employeeData.forEach(emp => {
            const building = emp['AQL_Building'];
            const empNo = emp['Employee No'] || emp['emp_no'];
            if (building && empNo && !areaMapping[empNo]) {
                areaMapping[empNo] = 'Building ' + building;
            }
        });

        // 조건 7번: 팀/구역 AQL 3개월 연속 실패
        let cond7FailEmployees = window.employeeData.filter(emp => {
            const cond7 = emp['cond_7_aql_team_area'] || 'PASS';
            return cond7 === 'FAIL';
        });

        // 조건 8번: 구역 reject rate > 3%
        let cond8FailEmployees = window.employeeData.filter(emp => {
            const cond8 = emp['cond_8_area_reject'] || 'PASS';
            const areaRejectRate = parseFloat(emp['Area_Reject_Rate'] || emp['area_reject_rate'] || 0);
            return cond8 === 'FAIL' || areaRejectRate > 3;
        });

        // 구역별 통계 계산
        function calculateAreaStatistics() {
            const areaStats = {};
            let totalInspected = 0;
            let totalRejects = 0;

            // 모든 직원 데이터를 순회하며 구역별 통계 수집
            window.employeeData.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const area = areaMapping[empNo] || 'AUDIT & TRAINING TEAM';

                // 실제 AQL 데이터 사용 (Excel의 Single Source of Truth)
                const aqlTotalTests = parseFloat(emp['AQL_Total_Tests'] || 0);
                const aqlPassCount = parseFloat(emp['AQL_Pass_Count'] || 0);
                const aqlFailPercent = parseFloat(emp['AQL_Fail_Percent'] || 0);
                const aqlBuilding = emp['AQL_Building'] || '';

                // 테스트 건수 기반 계산
                const totalTests = aqlTotalTests;
                const passTests = aqlPassCount;
                const failTests = totalTests > 0 ? Math.round(totalTests * aqlFailPercent / 100) : 0;

                if (!areaStats[area]) {
                    areaStats[area] = {
                        totalEmployees: 0,  // 전체 직원수
                        cond7FailCount: 0,   // 조건 7번 미충족 인원
                        cond8FailCount: 0,   // 조건 8번 미충족 인원
                        totalPassTests: 0,
                        totalFailTests: 0,
                        totalTests: 0,
                        rejectRate: 0
                    };
                }

                // 전체 직원수 카운트
                areaStats[area].totalEmployees += 1;

                // 조건별 카운트
                const cond7 = emp['cond_7_aql_team_area'] || 'PASS';
                const cond8 = emp['cond_8_area_reject'] || 'PASS';
                const personalRejectRate = parseFloat(emp['Area_Reject_Rate'] || emp['area_reject_rate'] || 0);

                if (cond7 === 'FAIL') {
                    areaStats[area].cond7FailCount += 1;
                }
                if (cond8 === 'FAIL' || personalRejectRate > 3) {
                    areaStats[area].cond8FailCount += 1;
                }

                // 테스트 통계는 전체 직원 대상
                if (totalTests > 0) {
                    areaStats[area].totalPassTests += passTests;
                    areaStats[area].totalFailTests += failTests;
                    areaStats[area].totalTests += totalTests;

                    totalInspected += totalTests;
                    totalRejects += failTests;
                }
            });

            // 각 구역의 Reject Rate 계산
            for (const area in areaStats) {
                const stats = areaStats[area];
                stats.rejectRate = stats.totalTests > 0
                    ? (stats.totalFailTests / stats.totalTests * 100).toFixed(2)
                    : 0;
            }

            // 전체 통계 추가
            const totalPassTests = Object.values(areaStats).reduce((sum, stats) => sum + stats.totalPassTests, 0);
            const totalFailTests = Object.values(areaStats).reduce((sum, stats) => sum + stats.totalFailTests, 0);
            const totalTestsAll = totalPassTests + totalFailTests;
            const totalEmployees = Object.values(areaStats).reduce((sum, stats) => sum + stats.totalEmployees, 0);
            const totalCond7Fail = Object.values(areaStats).reduce((sum, stats) => sum + stats.cond7FailCount, 0);
            const totalCond8Fail = Object.values(areaStats).reduce((sum, stats) => sum + stats.cond8FailCount, 0);

            areaStats['전체'] = {
                totalEmployees: totalEmployees,
                cond7FailCount: totalCond7Fail,
                cond8FailCount: totalCond8Fail,
                totalPassTests: totalPassTests,
                totalFailTests: totalFailTests,
                totalTests: totalTestsAll,
                rejectRate: totalTestsAll > 0
                    ? (totalFailTests / totalTestsAll * 100).toFixed(2)
                    : 0
            };

            return areaStats;
        }

        const areaStatistics = calculateAreaStatistics();

        // Bootstrap 모달 생성 및 표시
        const modalContent = `
            <div class="modal-header unified-modal-header">
                <h5 class="modal-title unified-modal-title">
                    <i class="bi bi-graph-up-arrow"></i>
                    구역별 AQL 상태 및 조건 7번/8번 분석
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <div class="alert alert-info">
                        <strong>조건 7번:</strong> 팀/구역 AQL 3개월 연속 실패 - ${cond7FailEmployees.length}명<br>
                        <strong>조건 8번:</strong> 구역 Reject Rate 3% 초과 - ${cond8FailEmployees.length}명
                    </div>
                    <p>구역별 AQL 상세 현황과 조건 충족 상태를 확인할 수 있습니다.</p>
                </div>

                <!-- 구역별 Reject Rate 통계 테이블 -->
                <div class="mb-4">
                                <h6 class="mb-3"><i class="fas fa-chart-bar me-2"></i>구역별 Reject Rate 통계</h6>
                                <div class="table-responsive">
                                    <table class="table table-bordered" style="font-size: 13px;">
                                        <thead class="table-light">
                                            <tr>
                                                <th style="padding: 10px;">구역</th>
                                                <th style="padding: 10px; text-align: center;">전체<br>인원</th>
                                                <th style="padding: 10px; text-align: center;">조건7<br>미충족</th>
                                                <th style="padding: 10px; text-align: center;">조건8<br>미충족</th>
                                                <th style="padding: 10px; text-align: center;">총 AQL<br>건수</th>
                                                <th style="padding: 10px; text-align: center;">PASS<br>건수</th>
                                                <th style="padding: 10px; text-align: center;">FAIL<br>건수</th>
                                                <th style="padding: 10px; text-align: center;">Reject<br>Rate</th>
                                                <th style="padding: 10px; text-align: center;">상태</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${Object.entries(areaStatistics).map(([area, stats]) => {
                                                const isTotal = area === '전체';
                                                const rejectRate = parseFloat(stats.rejectRate);
                                                let badgeClass = 'bg-success';
                                                let statusText = '정상';
                                                if (rejectRate > 3) {
                                                    badgeClass = 'bg-danger';
                                                    statusText = '초과';
                                                } else if (rejectRate > 2.5) {
                                                    badgeClass = 'bg-warning';
                                                    statusText = '주의';
                                                }
                                                return `
                                                    <tr class="${isTotal ? 'table-primary fw-bold' : ''}">
                                                        <td style="padding: 8px;">${area}</td>
                                                        <td style="padding: 8px; text-align: center;">${stats.totalEmployees}</td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            ${stats.cond7FailCount > 0 ?
                                                                `<span class="badge bg-warning">${stats.cond7FailCount}</span>` :
                                                                '<span class="text-muted">0</span>'}
                                                        </td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            ${stats.cond8FailCount > 0 ?
                                                                `<span class="badge bg-danger">${stats.cond8FailCount}</span>` :
                                                                '<span class="text-muted">0</span>'}
                                                        </td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalPassTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalFailTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                                ${stats.rejectRate}%
                                                            </span>
                                                        </td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                                ${statusText}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- 조건별 직원 목록 -->
                            <div class="mb-4">
                                <h6 class="mb-3"><i class="fas fa-users me-2"></i>조건 미충족 직원 상세</h6>
                                <div class="table-responsive">
                                    <table class="table table-bordered" style="font-size: 13px;">
                                        <thead class="table-light">
                                            <tr>
                                                <th style="padding: 10px;">구역</th>
                                                <th style="padding: 10px; text-align: center;">인원수</th>
                                                <th style="padding: 10px; text-align: center;">PASS 건수</th>
                                                <th style="padding: 10px; text-align: center;">FAIL 건수</th>
                                                <th style="padding: 10px; text-align: center;">전체 테스트</th>
                                                <th style="padding: 10px; text-align: center;">Pass Rate</th>
                                                <th style="padding: 10px; text-align: center;">상태</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${Object.entries(areaStatistics).map(([area, stats]) => {
                                                const isTotal = area === '전체';
                                                const passRate = (100 - parseFloat(stats.rejectRate)).toFixed(2);
                                                let badgeClass = 'bg-danger';
                                                let statusText = '저조';
                                                if (passRate >= 97) {
                                                    badgeClass = 'bg-success';
                                                    statusText = '우수';
                                                } else if (passRate >= 95) {
                                                    badgeClass = 'bg-info';
                                                    statusText = '양호';
                                                } else if (passRate >= 90) {
                                                    badgeClass = 'bg-warning';
                                                    statusText = '보통';
                                                }
                                                return `
                                                    <tr class="${isTotal ? 'table-success fw-bold' : ''}">
                                                        <td style="padding: 8px;">${area}</td>
                                                        <td style="padding: 8px; text-align: center;">${stats.employees}명</td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalPassTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalFailTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">${(stats.totalTests || 0).toLocaleString()}</td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                                ${passRate}%
                                                            </span>
                                                        </td>
                                                        <td style="padding: 8px; text-align: center;">
                                                            <span class="badge ${badgeClass}" style="font-size: 12px; padding: 4px 8px;">
                                                                ${statusText}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

        // Bootstrap 모달 처리
        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true" data-bs-backdrop="true" data-bs-keyboard="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content" id="detailModalContent"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;

        // Bootstrap 5 Modal 처리
        const modalElement = document.getElementById('detailModal');

        // 기존 모달 인스턴스 정리
        const existingModal = bootstrap.Modal.getInstance(modalElement);
        if (existingModal) {
            existingModal.dispose();
        }

        // 새 모달 인스턴스 생성 with proper options
        const bsModal = new bootstrap.Modal(modalElement, {
            backdrop: true,      // 배경 클릭으로 닫기
            keyboard: true,      // ESC 키로 닫기
            focus: true
        });

        bsModal.show();

        // 백드롭 클릭 이벤트 명시적 처리 (구역 AQL 모달)
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.cursor = 'pointer';
                backdrop.addEventListener('click', function(e) {
                    if (e.target === backdrop) {
                        bsModal.hide();
                    }
                });
            }
        }, 100);

        // 모달 닫기 이벤트 리스너 추가
        modalElement.addEventListener('hidden.bs.modal', function () {
            // 모달이 닫힌 후 정리 작업
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }

    // 5PRS 통과율 < 95% 상세 모달
    function showLowPassRateDetails() {
        // TYPE-1 ASSEMBLY INSPECTOR with pass rate < 95% 필터링
        let lowPassEmployees = window.employeeData.filter(emp => {
            const isType1 = emp['type'] === 'TYPE-1' || emp['ROLE TYPE STD'] === 'TYPE-1';
            const position = (emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();
            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
            const passRate = parseFloat(emp['pass_rate'] || emp['5PRS Pass Rate'] || 100);
            return isType1 && isAssemblyInspector && passRate < 95;
        });

        let sortColumn = 'passRate';
        let sortOrder = 'asc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'passRate' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#lowPassRateModal tbody');
            if (!tbody) return;

            // 정렬
            lowPassEmployees.sort((a, b) => {
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
                    case 'position':
                        aVal = a['position'] || a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['position'] || b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'passRate':
                        aVal = parseFloat(a['pass_rate'] || a['5PRS Pass Rate'] || 100);
                        bVal = parseFloat(b['pass_rate'] || b['5PRS Pass Rate'] || 100);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            lowPassEmployees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const position = emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '-';
                const passRate = parseFloat(emp['pass_rate'] || emp['5PRS Pass Rate'] || 0).toFixed(1);

                // Pass Rate에 따른 색상
                let badgeClass = 'bg-danger';
                if (passRate >= 90) badgeClass = 'bg-warning';
                else if (passRate >= 80) badgeClass = 'bg-orange';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td>${position}</td>
                    <td>TYPE-1</td>
                    <td><span class="badge ${badgeClass}">${passRate}%</span></td>
                    <td>${passRate < 95 ? '미충족' : '충족'}</td>
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
            modalDiv.setAttribute('id', 'lowPassRateModal');

            const modalHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="bi bi-graph-down"></i>
                                5PRS 통과율 95% 미만 상세
                            </h5>
                            <button type="button" class="btn-close" onclick="window.closeLowPassRateModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="alert alert-warning">
                                    <strong>조건 설명:</strong> TYPE-1 ASSEMBLY INSPECTOR의 5PRS 통과율이 95% 미만인 경우 인센티브를 받을 수 없습니다.
                                </div>
                                <p>총 ${lowPassEmployees.length}명이 5PRS 통과율 95% 미만입니다.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo">사번 ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name">이름 ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="position">직책 ${getSortIcon('position')}</th>
                                            <th>타입</th>
                                            <th class="sortable-header" data-sort="passRate">통과율 ${getSortIcon('passRate')}</th>
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
            window.closeLowPassRateModal = function() {
                if (modalDiv) {
                    modalDiv.remove();
                    modalDiv = null;
                }
                if (backdrop) {
                    backdrop.remove();
                    backdrop = null;
                }
                document.body.classList.remove('modal-open');
                window.closeLowPassRateModal = null;
            };

            // 백드롭 클릭으로 닫기
            backdrop.onclick = function(e) {
                if (e.target === backdrop) {
                    window.closeLowPassRateModal();
                }
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

    // 5PRS 검사량 < 100족 상세 모달
    function showLowInspectionQtyDetails() {
        // TYPE-1 ASSEMBLY INSPECTOR with inspection qty < 100 필터링
        let lowQtyEmployees = window.employeeData.filter(emp => {
            const isType1 = emp['type'] === 'TYPE-1' || emp['ROLE TYPE STD'] === 'TYPE-1';
            const position = (emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();
            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
            const inspectionQty = parseFloat(emp['validation_qty'] || emp['5PRS Inspection Quantity'] || 0);
            return isType1 && isAssemblyInspector && inspectionQty < 100;
        });

        let sortColumn = 'inspectionQty';
        let sortOrder = 'asc';
        let modalDiv = null;
        let backdrop = null;

        function sortData(column) {
            if (sortColumn === column) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortOrder = column === 'inspectionQty' ? 'asc' : 'desc';
            }
            updateTableBody();
        }

        function updateTableBody() {
            const tbody = document.querySelector('#lowInspectionQtyModal tbody');
            if (!tbody) return;

            // 정렬
            lowQtyEmployees.sort((a, b) => {
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
                    case 'position':
                        aVal = a['position'] || a['FINAL QIP POSITION NAME CODE'] || '';
                        bVal = b['position'] || b['FINAL QIP POSITION NAME CODE'] || '';
                        break;
                    case 'inspectionQty':
                        aVal = parseFloat(a['validation_qty'] || a['5PRS Inspection Quantity'] || 0);
                        bVal = parseFloat(b['validation_qty'] || b['5PRS Inspection Quantity'] || 0);
                        break;
                }

                if (typeof aVal === 'string') {
                    return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }
                return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
            });

            // 테이블 업데이트
            tbody.innerHTML = '';
            lowQtyEmployees.forEach(emp => {
                const empNo = emp['Employee No'] || emp['emp_no'];
                const name = emp['Full Name'] || emp['name'];
                const position = emp['position'] || emp['FINAL QIP POSITION NAME CODE'] || '-';
                const inspectionQty = Math.round(parseFloat(emp['validation_qty'] || emp['5PRS Inspection Quantity'] || 0));

                // Inspection Qty에 따른 색상
                let badgeClass = 'bg-danger';
                if (inspectionQty >= 80) badgeClass = 'bg-warning';
                else if (inspectionQty >= 50) badgeClass = 'bg-orange';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${empNo}</td>
                    <td>${name}</td>
                    <td>${position}</td>
                    <td>TYPE-1</td>
                    <td><span class="badge ${badgeClass}">${inspectionQty}족</span></td>
                    <td>${inspectionQty < 100 ? '미충족' : '충족'}</td>
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
            modalDiv.setAttribute('id', 'lowInspectionQtyModal');

            const modalHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="bi bi-search"></i>
                                5PRS 검사량 100족 미만 상세
                            </h5>
                            <button type="button" class="btn-close" onclick="window.closeLowInspectionQtyModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <div class="alert alert-warning">
                                    <strong>조건 설명:</strong> TYPE-1 ASSEMBLY INSPECTOR의 5PRS 검사량이 100족 미만인 경우 인센티브를 받을 수 없습니다.
                                </div>
                                <p>총 ${lowQtyEmployees.length}명이 5PRS 검사량 100족 미만입니다.</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="unified-table-header">
                                        <tr>
                                            <th class="sortable-header" data-sort="empNo">사번 ${getSortIcon('empNo')}</th>
                                            <th class="sortable-header" data-sort="name">이름 ${getSortIcon('name')}</th>
                                            <th class="sortable-header" data-sort="position">직책 ${getSortIcon('position')}</th>
                                            <th>타입</th>
                                            <th class="sortable-header" data-sort="inspectionQty">검사량 ${getSortIcon('inspectionQty')}</th>
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
            window.closeLowInspectionQtyModal = function() {
                if (modalDiv) {
                    modalDiv.remove();
                    modalDiv = null;
                }
                if (backdrop) {
                    backdrop.remove();
                    backdrop = null;
                }
                document.body.classList.remove('modal-open');
                window.closeLowInspectionQtyModal = null;
            };

            // 백드롭 클릭으로 닫기
            backdrop.onclick = function(e) {
                if (e.target === backdrop) {
                    window.closeLowInspectionQtyModal();
                }
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
    


// Main Dashboard JavaScript

// Note: The following variables are defined in the HTML by CompleteRenderer:
// - window.employeeData (and const employeeData)
// - const translations
// - const positionMatrix
// - window.excelDashboardData (and const excelDashboardData)
// - let currentLanguage
// - const dashboardMonth
// - const dashboardYear

    // Excel의 employee_data를 employeeData와 병합 (Single Source of Truth)
    if (excelDashboardData && excelDashboardData.employee_data) {
        const excelEmployeeMap = {};
        excelDashboardData.employee_data.forEach(excelEmp => {
            const empNo = excelEmp['Employee No'] || excelEmp.employee_no;
            if (empNo) {
                excelEmployeeMap[empNo] = excelEmp;
            }
        });

        // employeeData에 Excel 데이터 병합
        employeeData.forEach(emp => {
            const empNo = emp.employee_no || emp['Employee No'];
            if (empNo && excelEmployeeMap[empNo]) {
                const excelData = excelEmployeeMap[empNo];
                // Excel의 Minimum_Days_Met 필드 추가
                emp['Minimum_Days_Met'] = excelData['Minimum_Days_Met'];
                emp['Minimum_Working_Days_Required'] = excelData['Minimum_Working_Days_Required'];
                emp['Minimum_Days_Shortage'] = excelData['Minimum_Days_Shortage'];
                // 기타 Excel 필드도 병합
                emp['Actual Working Days'] = excelData['Actual Working Days'] || emp['Actual Working Days'];
                emp['Adjusted_Total_Working_Days'] = excelData['Adjusted_Total_Working_Days'];
                emp['Adjusted_Attendance_Rate'] = excelData['Adjusted_Attendance_Rate'];
            }
        });
    }

    // employeeData 필드 정규화 - boss_id 매핑 추가
    employeeData.forEach(emp => {
        // boss_id 필드 생성 (여러 가능한 필드명 체크)
        emp.boss_id = emp.boss_id ||
                     emp.Direct_Manager_ID ||
                     emp['Direct Manager ID'] ||
                     emp.direct_manager_id ||
                     '';

        // emp_no도 문자열로 통일
        emp.emp_no = String(emp.emp_no || emp['Employee No'] || '');

        // position과 name 필드도 확인
        emp.position = emp.position || emp['QIP POSITION 1ST  NAME'] || '';
        emp.name = emp.name || emp['Full Name'] || emp.employee_name || '';
        emp.type = emp.type || emp['ROLE TYPE STD'] || '';
    });

    console.log('Employee data normalized. Sample:', employeeData.slice(0, 2));

    // 번역 함수
    function getTranslation(keyPath, lang = currentLanguage) {
        const keys = keyPath.split('.');
        let value = translations;
        
        try {
            for (const key of keys) {
                value = value[key];
            }
            return value[lang] || value['ko'] || keyPath;
        } catch (e) {
            return keyPath;
        }
    }
    
    // FAQ 예시 섹션 업데이트 함수
    function updateFAQExamples() {
        const lang = currentLanguage;
        console.log('Updating FAQ examples for language:', lang);
        
        // FAQ 계산 예시 타이틀
        const calcTitle = document.getElementById('faqCalculationExampleTitle');
        if (calcTitle) {
            calcTitle.textContent = translations.incentiveCalculation?.faq?.calculationExampleTitle?.[lang] || '📐 실제 계산 예시';
        }
        
        // Case 1 - TYPE-1 ASSEMBLY INSPECTOR
        const case1Title = document.getElementById('faqCase1Title');
        if (case1Title) {
            case1Title.textContent = translations.incentiveCalculation?.faq?.case1Title?.[lang] || '예시 1: TYPE-1 ASSEMBLY INSPECTOR (10개월 연속 근무)';
        }
        
        const case1EmployeeLabel = document.getElementById('faqCase1EmployeeLabel');
        if (case1EmployeeLabel) {
            case1EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
        }
        
        const case1PrevMonthLabel = document.getElementById('faqCase1PrevMonthLabel');
        if (case1PrevMonthLabel) {
            case1PrevMonthLabel.textContent = translations.incentiveCalculation?.faq?.previousMonth?.[lang] || '전월 상태:';
        }
        
        const case1PrevMonthText = document.getElementById('faqCase1PrevMonthText');
        if (case1PrevMonthText) {
            const months = translations.incentiveCalculation?.faq?.consecutiveMonthsWorked?.[lang] || '개월 연속 →';
            const received = translations.incentiveCalculation?.faq?.incentiveReceived?.[lang] || 'VND 수령';
            case1PrevMonthText.textContent = `9$null 750,000 $null`;
        }
        
        const case1ConditionsLabel = document.getElementById('faqCase1ConditionsLabel');
        if (case1ConditionsLabel) {
            case1ConditionsLabel.textContent = translations.incentiveCalculation?.faq?.conditionEvaluation?.[lang] || '당월 조건 충족:';
        }
        
        // Case 1 조건들 업데이트
        document.querySelectorAll('.faq-attendance-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.attendanceRateMet?.[lang] || '출근율:';
        });
        document.querySelectorAll('.faq-absence-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.unauthorizedAbsenceMet?.[lang] || '무단결근:';
        });
        document.querySelectorAll('.faq-actual-days-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || '실제 근무일:';
        });
        document.querySelectorAll('.faq-min-days-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.minimumWorkingDays?.[lang] || '최소 근무일:';
        });
        document.querySelectorAll('.faq-aql-current-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.personalAql?.[lang] || '개인 AQL (당월):';
        });
        document.querySelectorAll('.faq-aql-consecutive-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.personalAqlContinuous?.[lang] || '개인 AQL (연속):';
        });
        document.querySelectorAll('.faq-fprs-rate-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.fprsPassRate?.[lang] || '5PRS 통과율:';
        });
        document.querySelectorAll('.faq-fprs-qty-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.fprsInspection?.[lang] || '5PRS 검사량:';
        });
        
        // 값들 업데이트
        const days = translations.incentiveCalculation?.faq?.days?.[lang] || '일';
        const items = translations.incentiveCalculation?.faq?.items?.[lang] || '개';
        
        document.querySelectorAll('.faq-absence-value').forEach(el => {
            el.textContent = '0' + days;
        });
        document.querySelectorAll('.faq-absence-limit').forEach(el => {
            el.textContent = '2' + days;
        });
        document.querySelectorAll('.faq-actual-days-value').forEach(el => {
            el.textContent = '20' + days;
        });
        document.querySelectorAll('.faq-actual-days-min').forEach(el => {
            el.textContent = '0' + days;
        });
        document.querySelectorAll('.faq-min-days-value').forEach(el => {
            el.textContent = '20' + days;
        });
        document.querySelectorAll('.faq-min-days-req').forEach(el => {
            el.textContent = '12' + days;
        });
        document.querySelectorAll('.faq-aql-current-value').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.failureText?.[lang] || '실패 0건';
        });
        document.querySelectorAll('.faq-aql-consecutive-value').forEach(el => {
            el.textContent = '3' + (translations.incentiveCalculation?.faq?.monthsConsecutiveNoFailure?.[lang] || '개월 연속 실패 없음');
        });
        document.querySelectorAll('.faq-fprs-qty-value').forEach(el => {
            el.textContent = '150' + items;
        });
        document.querySelectorAll('.faq-fprs-qty-min').forEach(el => {
            el.textContent = '100' + items;
        });
        
        const case1ResultLabel = document.getElementById('faqCase1ResultLabel');
        if (case1ResultLabel) {
            case1ResultLabel.textContent = translations.incentiveCalculation?.faq?.result?.[lang] || '결과:';
        }
        
        const case1ResultText = document.getElementById('faqCase1ResultText');
        if (case1ResultText) {
            const allMet = translations.incentiveCalculation?.faq?.allConditionsMet?.[lang] || '모든 조건 충족';
            const consecutive = translations.incentiveCalculation?.faq?.consecutiveMonthsWorked?.[lang] || '개월 연속 →';
            const payment = translations.incentiveCalculation?.faq?.incentivePayment?.[lang] || 'VND 지급';
            case1ResultText.innerHTML = `$null → <span class="badge bg-success">10$null 850,000 $null</span>`;
        }
        
        // Case 2 - AUDIT & TRAINING TEAM
        const case2Title = document.getElementById('faqCase2Title');
        if (case2Title) {
            case2Title.textContent = translations.incentiveCalculation?.faq?.case2Title?.[lang] || '예시 2: AUDIT & TRAINING TEAM (담당구역 reject율 계산)';
        }
        
        const case2EmployeeLabel = document.getElementById('faqCase2EmployeeLabel');
        if (case2EmployeeLabel) {
            case2EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
        }
        
        const case2AreaLabel = document.getElementById('faqCase2AreaLabel');
        if (case2AreaLabel) {
            case2AreaLabel.textContent = translations.incentiveCalculation?.faq?.teamLeader?.[lang] || '담당 구역:';
        }
        
        const case2InspectionLabel = document.getElementById('faqCase2InspectionLabel');
        if (case2InspectionLabel) {
            const label = translations.incentiveCalculation?.faq?.aqlInspectionPassed?.[lang] || '구역 생산 총 AQL 검사 PO 수량:';
            case2InspectionLabel.textContent = 'Building B ' + label;
        }
        
        const case2InspectionQty = document.getElementById('faqCase2InspectionQty');
        if (case2InspectionQty) {
            case2InspectionQty.textContent = '100' + items;
        }
        
        const case2RejectLabel = document.getElementById('faqCase2RejectLabel');
        if (case2RejectLabel) {
            const label = translations.incentiveCalculation?.faq?.aqlRejectPo?.[lang] || '구역 생산 총 AQL 리젝 PO 수량:';
            case2RejectLabel.textContent = 'Building B ' + label;
        }
        
        const case2RejectQty = document.getElementById('faqCase2RejectQty');
        if (case2RejectQty) {
            case2RejectQty.textContent = '2' + items;
        }
        
        const case2CalcLabel = document.getElementById('faqCase2CalcLabel');
        if (case2CalcLabel) {
            case2CalcLabel.textContent = translations.incentiveCalculation?.faq?.calculation?.[lang] || '계산:';
        }
        
        const case2ResultLabel = document.getElementById('faqCase2ResultLabel');
        if (case2ResultLabel) {
            case2ResultLabel.textContent = translations.incentiveCalculation?.faq?.resultCondition?.[lang] || '결과:';
        }
        
        const case2ResultBadge = document.getElementById('faqCase2ResultBadge');
        if (case2ResultBadge) {
            case2ResultBadge.textContent = translations.incentiveCalculation?.faq?.conditionMet?.[lang] || '조건 충족';
        }
        
        // 멤버 테이블 타이틀
        const memberTableTitle = document.getElementById('faqMemberTableTitle');
        if (memberTableTitle) {
            memberTableTitle.textContent = translations.incentiveCalculation?.faq?.memberTable?.[lang] || 'AUDIT & TRAINING TEAM 멤버별 담당 구역';
        }
        
        // 테이블 헤더
        const headerName = document.getElementById('faqTableHeaderName');
        if (headerName) {
            headerName.textContent = translations.incentiveCalculation?.faq?.employeeNameLabel?.[lang] || '직원명';
        }
        
        const headerBuilding = document.getElementById('faqTableHeaderBuilding');
        if (headerBuilding) {
            headerBuilding.textContent = translations.incentiveCalculation?.faq?.assignedBuilding?.[lang] || '담당 Building';
        }
        
        const headerDesc = document.getElementById('faqTableHeaderDesc');
        if (headerDesc) {
            headerDesc.textContent = translations.incentiveCalculation?.faq?.buildingDescription?.[lang] || '설명';
        }
        
        const headerReject = document.getElementById('faqTableHeaderReject');
        if (headerReject) {
            headerReject.textContent = translations.incentiveCalculation?.faq?.rejectRate?.[lang] || 'Reject율';
        }
        
        // 테이블 내용
        document.querySelectorAll('.faq-building-whole').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.buildingWhole?.[lang] || '전체';
        });
        
        document.querySelectorAll('.faq-team-leader-desc').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.teamLeaderDescription?.[lang] || 'Team Leader - 전체 Building 총괄';
        });
        
        document.querySelectorAll('.faq-other-conditions').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.noMissingData?.[lang] || '기타 조건 미충족';
        });
        
        const rejectRateNote = document.getElementById('faqRejectRateNote');
        if (rejectRateNote) {
            rejectRateNote.textContent = translations.incentiveCalculation?.faq?.rejectRateNote?.[lang] || '* Reject율 기준: 3% 미만 (✅ 충족, ❌ 미충족)';
        }
        
        const memberNote = document.getElementById('faqMemberNote');
        if (memberNote) {
            const monthText = dashboardMonth === 'september' ? '9월' : dashboardMonth === 'august' ? '8월' : dashboardMonth === 'july' ? '7월' : dashboardMonth;
            memberNote.textContent = translations.incentiveCalculation?.faq?.memberNote?.[lang] || `* $null 기준 모든 AUDIT & TRAINING TEAM 멤버가 reject율 조건 미충족으로 인센티브 0원`;
        }
        
        // Case 3 - TYPE-2 STITCHING INSPECTOR
        const case3Title = document.getElementById('faqCase3Title');
        if (case3Title) {
            case3Title.textContent = translations.incentiveCalculation?.faq?.case3Title?.[lang] || '예시 3: TYPE-2 STITCHING INSPECTOR';
        }
        
        const case3EmployeeLabel = document.getElementById('faqCase3EmployeeLabel');
        if (case3EmployeeLabel) {
            case3EmployeeLabel.textContent = translations.incentiveCalculation?.faq?.employee?.[lang] || '직원:';
        }
        
        const case3TypeLabel = document.getElementById('faqCase3TypeLabel');
        if (case3TypeLabel) {
            case3TypeLabel.textContent = translations.incentiveCalculation?.faq?.positionType?.[lang] || '직급 타입:';
        }
        
        const case3StatusLabel = document.getElementById('faqCase3StatusLabel');
        if (case3StatusLabel) {
            case3StatusLabel.textContent = translations.incentiveCalculation?.faq?.conditionStatus?.[lang] || '조건 충족 현황:';
        }
        
        // Case 3 조건들
        document.querySelectorAll('.faq-case3-attendance-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.attendanceRateMet?.[lang] || '출근율:';
        });
        document.querySelectorAll('.faq-case3-absence-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.unauthorizedAbsenceMet?.[lang] || '무단결근:';
        });
        document.querySelectorAll('.faq-case3-actual-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.actualWorkingDays?.[lang] || '실제근무일:';
        });
        document.querySelectorAll('.faq-case3-min-label').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.minimumWorkingDays?.[lang] || '최소근무일:';
        });
        
        // Case 3 값들
        document.querySelectorAll('.faq-case3-met').forEach(el => {
            el.textContent = translations.incentiveCalculation?.faq?.conditionsMet?.[lang] || '충족';
        });
        document.querySelectorAll('.faq-case3-absence-value').forEach(el => {
            el.textContent = '0' + days;
        });
        document.querySelectorAll('.faq-case3-absence-limit').forEach(el => {
            el.textContent = '2' + days;
        });
        document.querySelectorAll('.faq-case3-actual-value').forEach(el => {
            el.textContent = '19' + days;
        });
        document.querySelectorAll('.faq-case3-actual-min').forEach(el => {
            el.textContent = '0' + days;
        });
        document.querySelectorAll('.faq-case3-min-value').forEach(el => {
            el.textContent = '19' + days;
        });
        document.querySelectorAll('.faq-case3-min-req').forEach(el => {
            el.textContent = '12' + days;
        });
        
        const case3CalcLabel = document.getElementById('faqCase3CalcLabel');
        if (case3CalcLabel) {
            case3CalcLabel.textContent = translations.incentiveCalculation?.faq?.incentiveCalculation?.[lang] || '인센티브 계산:';
        }
        
        const case3Explanation = document.getElementById('faqCase3Explanation');
        if (case3Explanation) {
            case3Explanation.textContent = translations.incentiveCalculation?.faq?.type2Explanation?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 출근 조건(1-4번)만 확인하며, 모든 조건을 충족했으므로 기본 인센티브를 받습니다.';
        }
        
        const case3PaymentLabel = document.getElementById('faqCase3PaymentLabel');
        if (case3PaymentLabel) {
            case3PaymentLabel.textContent = translations.incentiveCalculation?.faq?.paymentAmount?.[lang] || '지급액:';
        }
        
        const case3BasicText = document.getElementById('faqCase3BasicText');
        if (case3BasicText) {
            case3BasicText.textContent = translations.incentiveCalculation?.faq?.type2BasicIncentive?.[lang] || 'TYPE-2 기본 인센티브';
        }
        
        const case3Note = document.getElementById('faqCase3Note');
        if (case3Note) {
            case3Note.textContent = translations.incentiveCalculation?.faq?.type2Note?.[lang] || '* TYPE-2는 AQL이나 5PRS 조건 없이 출근 조건만으로 인센티브가 결정됩니다.';
        }
    }
    
    // 출근율 계산 방식 섹션 업데이트 함수
    function updateAttendanceSection() {
        const lang = currentLanguage;
        console.log('Updating attendance section for language:', lang);
        
        // 제목
        const title = document.getElementById('attendanceCalcTitle');
        if (title) {
            title.textContent = translations.incentive?.attendance?.title?.[lang] || '📊 출근율 계산 방식';
        }
        
        // 공식 제목
        const formulaTitle = document.getElementById('attendanceFormulaTitle');
        if (formulaTitle) {
            formulaTitle.textContent = translations.incentive?.attendance?.formulaTitle?.[lang] || '실제 계산 공식 (시스템 구현):';
        }
        
        // 공식들
        const formula1 = document.getElementById('attendanceFormula1');
        if (formula1) {
            formula1.textContent = translations.incentive?.attendance?.attendanceFormula?.[lang] || '출근율(%) = 100 - 결근율(%)';
        }
        
        const formula2 = document.getElementById('attendanceFormula2');
        if (formula2) {
            formula2.textContent = translations.incentive?.attendance?.absenceFormula?.[lang] || '결근율(%) = (결근 일수 / 총 근무일) × 100';
        }
        
        const formulaNote = document.getElementById('attendanceFormulaNote');
        if (formulaNote) {
            formulaNote.textContent = translations.incentive?.attendance?.absenceDaysNote?.[lang] || '* 결근 일수 = 총 근무일 - 실제 근무일 - 승인된 휴가';
        }
        
        // 예시 제목
        const examplesTitle = document.getElementById('attendanceExamplesTitle');
        if (examplesTitle) {
            examplesTitle.textContent = translations.incentive?.attendance?.examplesTitle?.[lang] || '결근율 계산 예시:';
        }
        
        const example1Title = document.getElementById('attendanceExample1Title');
        if (example1Title) {
            example1Title.textContent = translations.incentive?.attendance?.example1Title?.[lang] || '예시 1: 정상 근무자';
        }
        
        const example2Title = document.getElementById('attendanceExample2Title');
        if (example2Title) {
            example2Title.textContent = translations.incentive?.attendance?.example2Title?.[lang] || '예시 2: 무단결근 포함';
        }
        
        const example3Title = document.getElementById('attendanceExample3Title');
        if (example3Title) {
            example3Title.textContent = translations.incentive?.attendance?.example3Title?.[lang] || '예시 3: 조건 충족 경계선';
        }
        
        // 라벨들 업데이트
        document.querySelectorAll('.att-total-days-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.totalWorkingDays?.[lang] || '총 근무일';
        });
        document.querySelectorAll('.att-actual-days-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.actualWorkingDays?.[lang] || '실제 근무일';
        });
        document.querySelectorAll('.att-approved-leave-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.approvedLeave?.[lang] || '승인된 휴가';
        });
        document.querySelectorAll('.att-absence-days-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.absenceDays?.[lang] || '결근 일수';
        });
        document.querySelectorAll('.att-absence-rate-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.absenceRate?.[lang] || '결근율';
        });
        document.querySelectorAll('.att-attendance-rate-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.attendanceRate?.[lang] || '출근율';
        });
        document.querySelectorAll('.att-unauthorized-absence-label').forEach(el => {
            el.textContent = translations.incentive?.attendance?.unauthorizedAbsence?.[lang] || '무단결근';
        });
        document.querySelectorAll('.att-annual-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.annualLeave?.[lang] || '연차';
        });
        document.querySelectorAll('.att-sick-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.sickLeave?.[lang] || '병가';
        });
        document.querySelectorAll('.att-days-unit').forEach(el => {
            el.textContent = translations.incentive?.attendance?.days?.[lang] || '일';
        });
        document.querySelectorAll('.att-less-than-88').forEach(el => {
            el.textContent = translations.incentive?.attendance?.lessThan88?.[lang] || '88% 미만';
        });
        document.querySelectorAll('.att-more-than-88').forEach(el => {
            el.textContent = translations.incentive?.attendance?.moreThan88?.[lang] || '88% 이상';
        });
        
        const condition2NotMet = document.getElementById('attendanceCondition2NotMet');
        if (condition2NotMet) {
            condition2NotMet.textContent = translations.incentive?.attendance?.condition2NotMet?.[lang] || '단, 무단결근 3일로 조건 2 미충족 → 인센티브 0원';
        }
        
        // 결근 분류 섹션
        const classificationTitle = document.getElementById('attendanceClassificationTitle');
        if (classificationTitle) {
            classificationTitle.textContent = translations.incentive?.attendance?.absenceClassificationTitle?.[lang] || '결근 사유별 분류:';
        }
        
        const notIncludedTitle = document.getElementById('attendanceNotIncludedTitle');
        if (notIncludedTitle) {
            notIncludedTitle.textContent = translations.incentive?.attendance?.notIncludedInAbsence?.[lang] || '✅ 결근율에 포함 안됨 (승인된 휴가):';
        }
        
        const includedTitle = document.getElementById('attendanceIncludedTitle');
        if (includedTitle) {
            includedTitle.textContent = translations.incentive?.attendance?.includedInAbsence?.[lang] || '❌ 결근율에 포함됨 (무단결근):';
        }
        
        // 휴가 타입 번역
        document.querySelectorAll('.att-maternity-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.maternityLeave?.[lang] || '출산휴가';
        });
        document.querySelectorAll('.att-annual-leave-vn').forEach(el => {
            el.textContent = translations.incentive?.attendance?.annualLeaveVn?.[lang] || '연차휴가';
        });
        document.querySelectorAll('.att-approved-absence').forEach(el => {
            el.textContent = translations.incentive?.attendance?.approvedAbsence?.[lang] || '승인된 휴가';
        });
        document.querySelectorAll('.att-postpartum-rest').forEach(el => {
            el.textContent = translations.incentive?.attendance?.postpartumRest?.[lang] || '출산 후 요양';
        });
        document.querySelectorAll('.att-prenatal-checkup').forEach(el => {
            el.textContent = translations.incentive?.attendance?.prenatalCheckup?.[lang] || '산전검진';
        });
        document.querySelectorAll('.att-childcare-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.childcareLeave?.[lang] || '육아휴가';
        });
        document.querySelectorAll('.att-short-sick-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.shortSickLeave?.[lang] || '병가';
        });
        document.querySelectorAll('.att-business-trip').forEach(el => {
            el.textContent = translations.incentive?.attendance?.businessTrip?.[lang] || '출장';
        });
        document.querySelectorAll('.att-military-service').forEach(el => {
            el.textContent = translations.incentive?.attendance?.militaryService?.[lang] || '군복무';
        });
        document.querySelectorAll('.att-card-not-swiped').forEach(el => {
            el.textContent = translations.incentive?.attendance?.cardNotSwiped?.[lang] || '출퇴근 체크 누락';
        });
        document.querySelectorAll('.att-new-employee').forEach(el => {
            el.textContent = translations.incentive?.attendance?.newEmployee?.[lang] || '신규입사 특례';
        });
        document.querySelectorAll('.att-compensatory-leave').forEach(el => {
            el.textContent = translations.incentive?.attendance?.compensatoryLeave?.[lang] || '대체휴무';
        });
        document.querySelectorAll('.att-unauthorized-absence-ar1').forEach(el => {
            el.textContent = translations.incentive?.attendance?.unauthorizedAbsenceAR1?.[lang] || '무단결근';
        });
        document.querySelectorAll('.att-written-notice-absence').forEach(el => {
            el.textContent = translations.incentive?.attendance?.writtenNoticeAbsence?.[lang] || '서면통지 결근';
        });
        
        // 카운팅 규칙
        const countingRulesTitle = document.getElementById('attendanceCountingRulesTitle');
        if (countingRulesTitle) {
            countingRulesTitle.textContent = translations.incentive?.attendance?.countingRulesTitle?.[lang] || '📢 무단결근 카운팅 규칙:';
        }
        
        const countingRule1 = document.getElementById('attendanceCountingRule1');
        if (countingRule1) {
            countingRule1.textContent = translations.incentive?.attendance?.countingRule1?.[lang] || 'AR1 카테고리만 무단결근으로 카운트';
        }
        
        const countingRule2 = document.getElementById('attendanceCountingRule2');
        if (countingRule2) {
            countingRule2.textContent = translations.incentive?.attendance?.countingRule2?.[lang] || '2일까지는 인센티브 지급 가능';
        }
        
        const countingRule3 = document.getElementById('attendanceCountingRule3');
        if (countingRule3) {
            countingRule3.textContent = translations.incentive?.attendance?.countingRule3?.[lang] || '3일 이상 → 인센티브 0원';
        }
        
        // 조건 충족 기준
        const conditionCriteriaTitle = document.getElementById('attendanceConditionCriteriaTitle');
        if (conditionCriteriaTitle) {
            conditionCriteriaTitle.textContent = translations.incentive?.attendance?.conditionCriteriaTitle?.[lang] || '조건 충족 기준:';
        }
        
        const criteria1 = document.getElementById('attendanceCriteria1');
        if (criteria1) {
            criteria1.innerHTML = translations.incentive?.attendance?.attendanceCriteria?.[lang] || '<strong>출근율:</strong> ≥ 88% (결근율 ≤ 12%)';
        }
        
        const criteria2 = document.getElementById('attendanceCriteria2');
        if (criteria2) {
            criteria2.innerHTML = translations.incentive?.attendance?.unauthorizedAbsenceCriteria?.[lang] || '<strong>무단결근:</strong> ≤ 2일 (AR1 카테고리만 해당)';
        }
        
        const criteria3 = document.getElementById('attendanceCriteria3');
        if (criteria3) {
            criteria3.innerHTML = translations.incentive?.attendance?.actualWorkingDaysCriteria?.[lang] || '<strong>실제 근무일:</strong> > 0일';
        }
        
        const criteria4 = document.getElementById('attendanceCriteria4');
        if (criteria4) {
            criteria4.innerHTML = translations.incentive?.attendance?.minimumWorkingDaysCriteria?.[lang] || '<strong>최소 근무일:</strong> ≥ 12일';
        }
        
        // Unapproved Absence 설명
        const unapprovedTitle = document.getElementById('attendanceUnapprovedTitle');
        if (unapprovedTitle) {
            unapprovedTitle.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanationTitle?.[lang] || '📊 Unapproved Absence Days 설명:';
        }
        
        const unapproved1 = document.getElementById('attendanceUnapproved1');
        if (unapproved1) {
            unapproved1.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation1?.[lang] || 'HR 시스템에서 제공하는 무단결근 일수 데이터';
        }
        
        const unapproved2 = document.getElementById('attendanceUnapproved2');
        if (unapproved2) {
            unapproved2.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation2?.[lang] || 'AR1 (Vắng không phép) 카테고리만 집계';
        }
        
        const unapproved3 = document.getElementById('attendanceUnapproved3');
        if (unapproved3) {
            unapproved3.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation3?.[lang] || '서면통지 결근(Gửi thư)도 AR1에 포함';
        }
        
        const unapproved4 = document.getElementById('attendanceUnapproved4');
        if (unapproved4) {
            unapproved4.textContent = translations.incentive?.attendance?.unapprovedAbsenceExplanation4?.[lang] || '인센티브 조건: ≤2일 (개인별 최대 허용치)';
        }
    }
    
    // FAQ Q&A 섹션 업데이트 함수
    function updateFAQQASection() {
        const lang = currentLanguage;
        console.log('Updating FAQ Q&A section for language:', lang);
        console.log('FAQ translations available:', translations.incentive?.faq);
        console.log('Question1 translations:', translations.incentiveCalculation?.faq?.question1);
        
        // FAQ 섹션 제목
        const faqTitle = document.getElementById('faqSectionTitle');
        if (faqTitle) {
            faqTitle.textContent = translations.incentiveCalculation?.faq?.faqSectionTitle?.[lang] || '❓ 자주 묻는 질문 (FAQ)';
        }
        
        // Q1
        const q1 = document.getElementById('faqQuestion1');
        if (q1) {
            console.log('Updating Q1, current text:', q1.textContent);
            const newText = translations.incentiveCalculation?.faq?.question1?.[lang] || 'Q1. 왜 나는 인센티브를 못 받았나요? 조건을 확인하는 방법은?';
            console.log('New text for Q1:', newText);
            q1.textContent = newText;
        }
        document.getElementById('faqAnswer1Main').textContent = translations.incentiveCalculation?.faq?.answer1Main?.[lang] || '인센티브를 받지 못한 주요 이유:';
        document.getElementById('faqAnswer1Reason1').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.minDays?.[lang] || '최소 근무일 12일 미충족';
        document.getElementById('faqAnswer1Reason2').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.attendance?.[lang] || '출근율 88% 미만';
        document.getElementById('faqAnswer1Reason3').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.absence?.[lang] || '무단결근 3일 이상';
        document.getElementById('faqAnswer1Reason4').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.aql?.[lang] || 'AQL 실패 (해당 직급)';
        document.getElementById('faqAnswer1Reason5').textContent = translations.incentiveCalculation?.faq?.answer1Reasons?.fprs?.[lang] || '5PRS 통과율 95% 미만 (해당 직급)';
        document.getElementById('faqAnswer1CheckMethod').textContent = translations.incentiveCalculation?.faq?.answer1CheckMethod?.[lang] || '개인별 상세 페이지에서 본인의 조건 충족 여부를 확인할 수 있습니다.';
        
        // Q2
        const q2 = document.getElementById('faqQuestion2');
        if (q2) {
            q2.textContent = translations.incentiveCalculation?.faq?.question2?.[lang] || 'Q2. 무단결근이 며칠까지 허용되나요?';
        }
        document.getElementById('faqAnswer2Main').textContent = translations.incentiveCalculation?.faq?.answer2Main?.[lang] || '무단결근은 최대 2일까지 허용됩니다.';
        document.getElementById('faqAnswer2Detail').textContent = translations.incentiveCalculation?.faq?.answer2Detail?.[lang] || '3일 이상 무단결근시 해당 월 인센티브를 받을 수 없습니다. 사전 승인된 휴가나 병가는 무단결근에 포함되지 않습니다.';
        
        // Q3
        const q3 = document.getElementById('faqQuestion3');
        if (q3) {
            q3.textContent = translations.incentiveCalculation?.faq?.question3?.[lang] || 'Q3. TYPE-2 직급의 인센티브는 어떻게 계산되나요?';
        }
        document.getElementById('faqAnswer3Main').textContent = translations.incentiveCalculation?.faq?.answer3Main?.[lang] || 'TYPE-2 직급의 인센티브는 해당하는 TYPE-1 직급의 평균 인센티브를 기준으로 계산됩니다.';
        document.getElementById('faqAnswer3Example').textContent = translations.incentiveCalculation?.faq?.answer3Example?.[lang] || '예를 들어:';
        document.getElementById('faqAnswer3Example1').textContent = translations.incentiveCalculation?.faq?.answer3Example1?.[lang] || 'TYPE-2 GROUP LEADER는 TYPE-1 GROUP LEADER들의 평균 인센티브';
        document.getElementById('faqAnswer3Example2').textContent = translations.incentiveCalculation?.faq?.answer3Example2?.[lang] || 'TYPE-2 STITCHING INSPECTOR는 TYPE-1 ASSEMBLY INSPECTOR들의 평균 인센티브';
        
        // Q4
        const q4 = document.getElementById('faqQuestion4');
        if (q4) {
            q4.textContent = translations.incentiveCalculation?.faq?.question4?.[lang] || 'Q4. ASSEMBLY INSPECTOR의 연속 근무 개월은 어떻게 계산되나요?';
        }
        document.getElementById('faqAnswer4Main').textContent = translations.incentiveCalculation?.faq?.answer4Main?.[lang] || 'TYPE-1 ASSEMBLY INSPECTOR만 해당되며, 조건을 충족하며 인센티브를 받은 개월수가 누적됩니다.';
        document.getElementById('faqAnswer4Detail1').textContent = translations.incentiveCalculation?.faq?.answer4Detail1?.[lang] || '조건 미충족으로 인센티브를 못 받으면 0개월로 리셋';
        document.getElementById('faqAnswer4Detail2').textContent = translations.incentiveCalculation?.faq?.answer4Detail2?.[lang] || '12개월 이상 연속시 최대 인센티브 1,000,000 VND';
        
        // Q5
        const q5 = document.getElementById('faqQuestion5');
        if (q5) {
            q5.textContent = translations.incentiveCalculation?.faq?.question5?.[lang] || 'Q5. AQL 실패가 무엇이고 어떤 영향을 미치나요?';
        }
        document.getElementById('faqAnswer5Main').textContent = translations.incentiveCalculation?.faq?.answer5Main?.[lang] || 'AQL(Acceptable Quality Limit)은 품질 검사 기준입니다.';
        document.getElementById('faqAnswer5Detail1').textContent = translations.incentiveCalculation?.faq?.answer5Detail1?.[lang] || '개인 AQL 실패: 해당 월에 품질 검사 실패한 경우';
        document.getElementById('faqAnswer5Detail2').textContent = translations.incentiveCalculation?.faq?.answer5Detail2?.[lang] || '3개월 연속 실패: 지난 3개월 동안 연속으로 실패한 경우';
        document.getElementById('faqAnswer5Detail3').textContent = translations.incentiveCalculation?.faq?.answer5Detail3?.[lang] || 'AQL 관련 직급만 영향받음 (INSPECTOR 계열 등)';
        
        // Q6
        const q6 = document.getElementById('faqQuestion6');
        if (q6) {
            q6.textContent = translations.incentiveCalculation?.faq?.question6?.[lang] || 'Q6. 5PRS 검사량이 부족하면 어떻게 되나요?';
        }
        document.getElementById('faqAnswer6Main').textContent = translations.incentiveCalculation?.faq?.answer6Main?.[lang] || '5PRS 관련 직급은 다음 조건을 충족해야 합니다:';
        document.getElementById('faqAnswer6Detail1').textContent = translations.incentiveCalculation?.faq?.answer6Detail1?.[lang] || '검사량 100족 이상';
        document.getElementById('faqAnswer6Detail2').textContent = translations.incentiveCalculation?.faq?.answer6Detail2?.[lang] || '통과율 95% 이상';
        document.getElementById('faqAnswer6Conclusion').textContent = translations.incentiveCalculation?.faq?.answer6Conclusion?.[lang] || '둘 중 하나라도 미충족시 인센티브를 받을 수 없습니다.';
        
        // Q7
        const q7 = document.getElementById('faqQuestion7');
        if (q7) {
            q7.textContent = translations.incentiveCalculation?.faq?.question7?.[lang] || 'Q7. 출산휴가나 병가 중에도 인센티브를 받을 수 있나요?';
        }
        document.getElementById('faqAnswer7Main').textContent = translations.incentiveCalculation?.faq?.answer7Main?.[lang] || '출산휴가나 장기 병가 중에는 인센티브가 지급되지 않습니다.';
        document.getElementById('faqAnswer7Detail1').textContent = translations.incentiveCalculation?.faq?.answer7Detail1?.[lang] || '최소 근무일 12일 조건을 충족할 수 없기 때문';
        document.getElementById('faqAnswer7Detail2').textContent = translations.incentiveCalculation?.faq?.answer7Detail2?.[lang] || '복귀 후 조건 충족시 다시 인센티브 수령 가능';
        document.getElementById('faqAnswer7Detail3').textContent = translations.incentiveCalculation?.faq?.answer7Detail3?.[lang] || 'ASSEMBLY INSPECTOR의 경우 연속 개월수는 0으로 리셋';
        
        // Q8
        const q8 = document.getElementById('faqQuestion8');
        if (q8) {
            q8.textContent = translations.incentiveCalculation?.faq?.question8?.[lang] || 'Q8. 전월 인센티브와 차이가 나는 이유는 무엇인가요?';
        }
        const answer8Main = document.getElementById('faqAnswer8Main');
        if (answer8Main) {
            answer8Main.textContent = translations.incentiveCalculation?.faq?.answer8Main?.[lang] || '인센티브 금액이 변동하는 주요 이유:';
        }
        const answer8Reason1 = document.getElementById('faqAnswer8Reason1');
        if (answer8Reason1) {
            answer8Reason1.innerHTML = `<strong>ASSEMBLY INSPECTOR</strong>: ${translations.incentiveCalculation?.faq?.answer8Reason1?.[lang] || '연속 근무 개월 변화'}`;
        }
        const answer8Reason2 = document.getElementById('faqAnswer8Reason2');
        if (answer8Reason2) {
            answer8Reason2.innerHTML = `<strong>TYPE-2 ${lang === 'ko' ? '직급' : lang === 'en' ? 'positions' : 'vị trí'}</strong>: ${translations.incentiveCalculation?.faq?.answer8Reason2?.[lang] || 'TYPE-1 평균값 변동'}`;
        }
        const answer8Reason3 = document.getElementById('faqAnswer8Reason3');
        if (answer8Reason3) {
            answer8Reason3.innerHTML = `<strong>AQL INSPECTOR</strong>: ${translations.incentiveCalculation?.faq?.answer8Reason3?.[lang] || 'Part1, Part2, Part3 조건 변화'}`;
        }
        const answer8Reason4 = document.getElementById('faqAnswer8Reason4');
        if (answer8Reason4) {
            answer8Reason4.innerHTML = `<strong>${lang === 'ko' ? '조건 미충족' : lang === 'en' ? 'Unmet conditions' : 'Điều kiện không đạt'}</strong>: ${translations.incentiveCalculation?.faq?.answer8Reason4?.[lang] || '하나라도 미충족시 0'}`;
        }
        
        // Q9
        const q9 = document.getElementById('faqQuestion9');
        if (q9) {
            q9.textContent = translations.incentiveCalculation?.faq?.question9?.[lang] || 'Q9. TYPE-3에서 TYPE-2로 승진하면 인센티브가 어떻게 변하나요?';
        }
        const answer9Detail1 = document.getElementById('faqAnswer9Detail1');
        if (answer9Detail1) {
            answer9Detail1.innerHTML = `<strong>TYPE-3</strong>: ${translations.incentiveCalculation?.faq?.answer9Detail1?.[lang] || '조건 없이 기본 150,000 VND (근무시 자동 지급)'}`;
        }
        const answer9Detail2 = document.getElementById('faqAnswer9Detail2');
        if (answer9Detail2) {
            answer9Detail2.innerHTML = `<strong>TYPE-2</strong>: ${translations.incentiveCalculation?.faq?.answer9Detail2?.[lang] || '조건 충족 필요, TYPE-1 평균 기준 계산'}`;
        }
        const answer9Detail3 = document.getElementById('faqAnswer9Detail3');
        if (answer9Detail3) {
            answer9Detail3.textContent = translations.incentiveCalculation?.faq?.answer9Detail3?.[lang] || '승진 후 조건 충족시 일반적으로 인센티브 증가';
        }
        const answer9Detail4 = document.getElementById('faqAnswer9Detail4');
        if (answer9Detail4) {
            answer9Detail4.textContent = translations.incentiveCalculation?.faq?.answer9Detail4?.[lang] || '하지만 조건 미충족시 0이 될 수 있으므로 주의 필요';
        }
        
        // Q10
        const q10 = document.getElementById('faqQuestion10');
        if (q10) {
            q10.textContent = translations.incentiveCalculation?.faq?.question10?.[lang] || 'Q10. 조건을 모두 충족했는데도 인센티브가 0인 이유는 무엇인가요?';
        }
        const answer10Main = document.getElementById('faqAnswer10Main');
        if (answer10Main) {
            answer10Main.textContent = translations.incentiveCalculation?.faq?.answer10Main?.[lang] || '다음 사항을 재확인해 보세요:';
        }
        const answer10Reason1 = document.getElementById('faqAnswer10Reason1');
        if (answer10Reason1) {
            answer10Reason1.innerHTML = `<strong>${lang === 'ko' ? '숨겨진 조건' : lang === 'en' ? 'Hidden conditions' : 'Điều kiện ẩn'}</strong>: ${translations.incentiveCalculation?.faq?.answer10Reason1?.[lang]?.replace(/.*: (.*)/, '$1') || '직급별로 적용되는 모든 조건 확인'}`;
        }
        const answer10Reason2 = document.getElementById('faqAnswer10Reason2');
        if (answer10Reason2) {
            answer10Reason2.innerHTML = `<strong>${lang === 'ko' ? '데이터 업데이트' : lang === 'en' ? 'Data update' : 'Cập nhật dữ liệu'}</strong>: ${translations.incentiveCalculation?.faq?.answer10Reason2?.[lang]?.replace(/.*: (.*)/, '$1') || '최신 데이터 반영 여부'}`;
        }
        const answer10Reason3 = document.getElementById('faqAnswer10Reason3');
        if (answer10Reason3) {
            answer10Reason3.innerHTML = `<strong>${lang === 'ko' ? '특별한 사유' : lang === 'en' ? 'Special reasons' : 'Lý do đặc biệt'}</strong>: ${translations.incentiveCalculation?.faq?.answer10Reason3?.[lang]?.replace(/.*: (.*)/, '$1') || '징계, 경고 등 특별 사유'}`;
        }
        const answer10Reason4 = document.getElementById('faqAnswer10Reason4');
        if (answer10Reason4) {
            answer10Reason4.innerHTML = `<strong>${lang === 'ko' ? '시스템 오류' : lang === 'en' ? 'System error' : 'Lỗi hệ thống'}</strong>: ${translations.incentiveCalculation?.faq?.answer10Reason4?.[lang]?.replace(/.*: (.*)/, '$1') || 'HR 부서에 문의'}`;
        }
        const answer10Conclusion = document.getElementById('faqAnswer10Conclusion');
        if (answer10Conclusion) {
            answer10Conclusion.textContent = translations.incentiveCalculation?.faq?.answer10Conclusion?.[lang] || '개인별 상세 페이지에서 조건별 충족 여부를 상세히 확인하시기 바랍니다.';
        }

        // FAQ Q11 translations
        const q11 = document.getElementById('faqQuestion11');
        if (q11) {
            q11.textContent = translations.incentiveCalculation?.faq?.question11?.[lang] || 'Q11. TYPE-2 GROUP LEADER가 인센티브를 못 받는 경우가 있나요?';
        }
        const answer11Main = document.getElementById('faqAnswer11Main');
        if (answer11Main) {
            answer11Main.textContent = translations.incentiveCalculation?.faq?.answer11Main?.[lang] || 'TYPE-2 GROUP LEADER는 특별한 계산 규칙이 적용됩니다:';
        }
        const answer11Detail1 = document.getElementById('faqAnswer11Detail1');
        if (answer11Detail1) {
            const baseCalc = translations.incentiveCalculation?.faq?.answer11Detail1?.[lang] || '기본 계산: TYPE-1 GROUP LEADER 평균 인센티브를 받습니다';
            answer11Detail1.innerHTML = `<strong>${baseCalc.split(':')[0]}:</strong> ${baseCalc.split(':')[1] || ''}`;
        }
        const answer11Detail2 = document.getElementById('faqAnswer11Detail2');
        if (answer11Detail2) {
            const indepCalc = translations.incentiveCalculation?.faq?.answer11Detail2?.[lang] || '독립 계산: TYPE-1 GROUP LEADER 평균이 0 VND일 경우, 자동으로 전체 TYPE-2 LINE LEADER 평균 × 2로 계산됩니다';
            answer11Detail2.innerHTML = `<strong>${indepCalc.split(':')[0]}:</strong> ${indepCalc.split(':')[1] || ''}`;
        }
        const answer11Detail3 = document.getElementById('faqAnswer11Detail3');
        if (answer11Detail3) {
            const improvement = translations.incentiveCalculation?.faq?.answer11Detail3?.[lang] || '개선 사항: 부하직원 관계와 상관없이 전체 TYPE-2 LINE LEADER 평균을 사용하여 더 공정한 계산이 이루어집니다';
            answer11Detail3.innerHTML = `<strong>${improvement.split(':')[0]}:</strong> ${improvement.split(':')[1] || ''}`;
        }
        const answer11Detail4 = document.getElementById('faqAnswer11Detail4');
        if (answer11Detail4) {
            const conditions = translations.incentiveCalculation?.faq?.answer11Detail4?.[lang] || '조건: TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브를 받을 수 있습니다';
            answer11Detail4.innerHTML = `<strong>${conditions.split(':')[0]}:</strong> ${conditions.split(':')[1] || ''}`;
        }
        const answer11Conclusion = document.getElementById('faqAnswer11Conclusion');
        if (answer11Conclusion) {
            answer11Conclusion.textContent = translations.incentiveCalculation?.faq?.answer11Conclusion?.[lang] || '따라서 출근 조건을 충족한 TYPE-2 GROUP LEADER는 항상 인센티브를 받을 수 있도록 보장됩니다.';
        }

        // TYPE-2 GROUP LEADER Special Calculation Box translations
        const type2SpecialTitle = document.getElementById('type2GroupLeaderSpecialTitle');
        if (type2SpecialTitle) {
            type2SpecialTitle.textContent = translations.type2GroupLeaderSpecial?.title?.[lang] || '⚠️ TYPE-2 GROUP LEADER 특별 계산 규칙';
        }
        const type2BaseCalc = document.getElementById('type2BaseCalc');
        if (type2BaseCalc) {
            const baseText = translations.type2GroupLeaderSpecial?.baseCalculation?.[lang] || '기본 계산: TYPE-1 GROUP LEADER 평균 인센티브 사용';
            type2BaseCalc.innerHTML = `<strong>${baseText.split(':')[0]}:</strong> ${baseText.split(':')[1] || ''}`;
        }
        const type2IndependentCalc = document.getElementById('type2IndependentCalc');
        if (type2IndependentCalc) {
            const indepText = translations.type2GroupLeaderSpecial?.independentCalculation?.[lang] || 'TYPE-1 평균이 0 VND인 경우: 모든 TYPE-2 LINE LEADER 평균 × 2로 독립 계산';
            type2IndependentCalc.innerHTML = `<strong>${indepText.split(':')[0]}:</strong> ${indepText.split(':')[1] || ''}`;
        }
        const type2Important = document.getElementById('type2Important');
        if (type2Important) {
            const importantText = translations.type2GroupLeaderSpecial?.important?.[lang] || '중요: 부하직원 관계 없이 전체 TYPE-2 LINE LEADER 평균 사용';
            type2Important.innerHTML = `<strong>${importantText.split(':')[0]}:</strong> ${importantText.split(':')[1] || ''}`;
        }
        const type2Conditions = document.getElementById('type2Conditions');
        if (type2Conditions) {
            const conditionsText = translations.type2GroupLeaderSpecial?.conditions?.[lang] || '적용 조건: TYPE-2는 출근 조건(1-4번)만 충족하면 인센티브 지급';
            type2Conditions.innerHTML = `<strong>${conditionsText.split(':')[0]}:</strong> ${conditionsText.split(':')[1] || ''}`;
        }

        // Talent Pool 섹션 번역 업데이트
        const talentPoolTitle = document.getElementById('talentPoolTitle');
        if (talentPoolTitle) {
            talentPoolTitle.textContent = getTranslation('talentPool.sectionTitle', lang);
        }
        
        const talentPoolMemberCountLabel = document.getElementById('talentPoolMemberCountLabel');
        if (talentPoolMemberCountLabel) {
            talentPoolMemberCountLabel.textContent = getTranslation('talentPool.memberCount', lang);
        }
        
        const talentPoolMonthlyBonusLabel = document.getElementById('talentPoolMonthlyBonusLabel');
        if (talentPoolMonthlyBonusLabel) {
            talentPoolMonthlyBonusLabel.textContent = getTranslation('talentPool.monthlyBonus', lang);
        }
        
        const talentPoolTotalBonusLabel = document.getElementById('talentPoolTotalBonusLabel');
        if (talentPoolTotalBonusLabel) {
            talentPoolTotalBonusLabel.textContent = getTranslation('talentPool.totalBonus', lang);
        }
        
        const talentPoolPaymentPeriodLabel = document.getElementById('talentPoolPaymentPeriodLabel');
        if (talentPoolPaymentPeriodLabel) {
            talentPoolPaymentPeriodLabel.textContent = getTranslation('talentPool.paymentPeriod', lang);
        }
        
        // 조직도 탭 번역 업데이트
        const tabOrgChart = document.getElementById('tabOrgChart');
        if (tabOrgChart) {
            tabOrgChart.textContent = getTranslation('tabs.orgChart', currentLanguage);
        }

        // 조직도 제목 및 부제
        const orgChartTitle = document.getElementById('orgChartTitle');
        if (orgChartTitle) {
            orgChartTitle.textContent = getTranslation('orgChart.title', currentLanguage);
        }

        const orgChartSubtitle = document.getElementById('orgChartSubtitle');
        if (orgChartSubtitle) {
            orgChartSubtitle.textContent = getTranslation('orgChart.subtitle', currentLanguage);
        }

        // 사용 안내 텍스트
        const usageGuideTitle = document.getElementById('usageGuideTitle');
        if (usageGuideTitle) {
            usageGuideTitle.textContent = getTranslation('orgChart.usageGuide.title', currentLanguage);
        }
        const usageGuideText = document.getElementById('usageGuideText');
        if (usageGuideText) {
            usageGuideText.innerHTML = getTranslation('orgChart.usageGuide.text', currentLanguage);
        }
        const usageGuideSubtext = document.getElementById('usageGuideSubtext');
        if (usageGuideSubtext) {
            usageGuideSubtext.textContent = getTranslation('orgChart.usageGuide.subtext', currentLanguage);
        }

        // 버튼 텍스트 - span 요소 내부의 텍스트만 업데이트
        const expandAllBtnSpan = document.querySelector('#expandAllBtn');
        if (expandAllBtnSpan) {
            const iconElement = expandAllBtnSpan.parentElement.querySelector('i');
            expandAllBtnSpan.textContent = getTranslation('orgChart.buttons.expandAll', currentLanguage);
        }
        const collapseAllBtnSpan = document.querySelector('#collapseAllBtn');
        if (collapseAllBtnSpan) {
            const iconElement = collapseAllBtnSpan.parentElement.querySelector('i');
            collapseAllBtnSpan.textContent = getTranslation('orgChart.buttons.collapseAll', currentLanguage);
        }
        const resetViewBtnSpan = document.querySelector('#resetViewBtn');
        if (resetViewBtnSpan) {
            const iconElement = resetViewBtnSpan.parentElement.querySelector('i');
            resetViewBtnSpan.textContent = getTranslation('orgChart.buttons.reset', currentLanguage);
        }

        // 모달 내부 텍스트 번역
        document.querySelectorAll('.modal-actual-incentive').forEach(elem => {
            elem.textContent = getTranslation('orgChart.modalLabels.actualIncentive', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-method').forEach(elem => {
            elem.textContent = getTranslation('orgChart.modalLabels.calculationMethod', currentLanguage);
        });
        document.querySelectorAll('.modal-no-payment-reason').forEach(elem => {
            elem.textContent = getTranslation('orgChart.modalLabels.noPaymentReason', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-line-leader').forEach(elem => {
            elem.textContent = getTranslation('orgChart.modalLabels.calcDetailLineLeader', currentLanguage);
        });
        document.querySelectorAll('.modal-close-btn').forEach(elem => {
            elem.textContent = getTranslation('orgChart.buttons.close', currentLanguage);
        });
        document.querySelectorAll('.modal-team-line-leader-list').forEach(elem => {
            elem.textContent = getTranslation('modal.teamLineLeaderList', currentLanguage);
        });
        document.querySelectorAll('.modal-team-line-leader-count').forEach(elem => {
            elem.textContent = getTranslation('modal.teamLineLeaderCount', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-line-leader').forEach(elem => {
            elem.textContent = getTranslation('modal.calcDetailLineLeader', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-group-leader').forEach(elem => {
            elem.textContent = getTranslation('modal.calcDetailGroupLeader', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-supervisor').forEach(elem => {
            elem.textContent = getTranslation('modal.calcDetailSupervisor', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-amanager').forEach(elem => {
            elem.textContent = getTranslation('modal.calcDetailAManager', currentLanguage);
        });
        document.querySelectorAll('.modal-calc-detail-manager').forEach(elem => {
            elem.textContent = getTranslation('modal.calcDetailManager', currentLanguage);
        })

        // 조직도 안내 텍스트
        const orgChartNoteLabel = document.getElementById('orgChartNoteLabel');
        if (orgChartNoteLabel) {
            orgChartNoteLabel.textContent = getTranslation('orgChart.noteLabel', currentLanguage);
        }

        const orgChartExcludedPositions = document.getElementById('orgChartExcludedPositions');
        if (orgChartExcludedPositions) {
            orgChartExcludedPositions.textContent = getTranslation('orgChart.excludedPositions', currentLanguage);
        }

        const orgChartHelpText = document.getElementById('orgChartHelpText');
        if (orgChartHelpText) {
            orgChartHelpText.textContent = getTranslation('orgChart.helpText', currentLanguage);
        }

        // 조직도 필터 옵션 업데이트
        const filterAll = document.getElementById('filterAll');
        if (filterAll) filterAll.textContent = getTranslation('orgChart.filters.viewAll', currentLanguage);

        const filterPaid = document.getElementById('filterPaid');
        if (filterPaid) filterPaid.textContent = getTranslation('orgChart.filters.paidOnly', currentLanguage);

        const filterUnpaid = document.getElementById('filterUnpaid');
        if (filterUnpaid) filterUnpaid.textContent = getTranslation('orgChart.filters.unpaidOnly', currentLanguage);

        // 조직도 범례 업데이트
        const legendReceived = document.getElementById('legendReceived');
        if (legendReceived) legendReceived.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

        const legendNotReceived = document.getElementById('legendNotReceived');
        if (legendNotReceived) legendNotReceived.textContent = getTranslation('orgChart.incentiveNotReceived', currentLanguage);

        const legendIncentiveReceived = document.getElementById('legendIncentiveReceived');
        if (legendIncentiveReceived) legendIncentiveReceived.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

        const legendNoIncentive = document.getElementById('legendNoIncentive');
        if (legendNoIncentive) legendNoIncentive.textContent = getTranslation('orgChart.incentiveNotReceived', currentLanguage);

        // 조직도가 이미 그려져 있다면 다시 그리기
        if (typeof updateOrgChart === 'function' && document.getElementById('orgTreeContent').innerHTML !== '') {
            updateOrgChart();
        }

        // 테이블 재생성하여 툴팁 번역 적용
        generateEmployeeTable();
        updatePositionFilter();
    }
    
    // 언어 변경 함수
    function changeLanguage(lang) {
        currentLanguage = lang;
        updateAllTexts();
        updateTypeSummaryTable();  // Type별 요약 테이블도 업데이트

        // Position tab이 활성화되어 있으면 position tables도 업데이트
        const positionTab = document.querySelector('#position');
        if (positionTab && positionTab.classList.contains('active')) {
            generatePositionTables();
        }

        localStorage.setItem('dashboardLanguage', lang);
    }
    
    // 대시보드 변경 함수
    function changeDashboard(type) {
        const currentMonth = '{str(month_num).zfill(2)}';  // 월 번호를 2자리로 패딩
        const currentYear = 'null';
        
        switch(type) {
            case 'management':
                // Management Dashboard로 이동
                window.location.href = `management_dashboard_$null_$null.html`;
                break;
            case 'statistics':
                // Statistics Dashboard로 이동 (향후 구현)
                alert('Statistics Dashboard는 준비 중입니다.');
                document.getElementById('dashboardSelector').value = 'incentive';
                break;
            case 'incentive':
            default:
                // 현재 페이지 유지
                break;
        }
    }
    
    // 모든 텍스트 업데이트 - 완전한 구현
    function updateAllTexts() {
        // 메인 헤더 업데이트
        const mainTitleElement = document.getElementById('mainTitle');
        if (mainTitleElement) {
            mainTitleElement.innerHTML = getTranslation('headers.mainTitle', currentLanguage) + ' <span class="version-badge">v6.01</span>';
        }
        
        // 날짜 관련 업데이트
        const yearText = 'null';
        const monthText = currentLanguage === 'ko' ? '{get_korean_month(month)}' : 
                          currentLanguage === 'en' ? '{month.capitalize()}' : 
                          'Tháng {month if month.isdigit() else "8"}';
        
        const mainSubtitle = document.getElementById('mainSubtitle');
        if (mainSubtitle) {
            const dataYear = mainSubtitle.getAttribute('data-year') || dashboardYear;
            const dataMonth = mainSubtitle.getAttribute('data-month') || dashboardMonth;
            const yearUnit = currentLanguage === 'ko' ? '년' : '';
            const incentiveText = getTranslation('headers.incentiveStatus', currentLanguage);

            // Get proper month text based on language
            let actualMonthText = dataMonth;
            if (currentLanguage === 'ko') {
                actualMonthText = dataMonth + '월';
            } else if (currentLanguage === 'en') {
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                                  'July', 'August', 'September', 'October', 'November', 'December'];
                actualMonthText = monthNames[parseInt(dataMonth) - 1] || dataMonth;
            } else if (currentLanguage === 'vi') {
                actualMonthText = 'Tháng ' + dataMonth;
            }

            mainSubtitle.innerHTML = dataYear + yearUnit + ' ' + actualMonthText + ' ' + incentiveText;
        }
        
        const generationDate = document.getElementById('generationDate');
        if (generationDate) {
            const dateLabel = getTranslation('headers.reportDateLabel', currentLanguage);
            const year = generationDate.getAttribute('data-year');
            const month = generationDate.getAttribute('data-month');
            const day = generationDate.getAttribute('data-day');
            const hour = generationDate.getAttribute('data-hour');
            const minute = generationDate.getAttribute('data-minute');
            
            let formattedDate;
            if (currentLanguage === 'ko') {
                formattedDate = `${year || '2025'}년 ${String(month || '09').padStart(2, '0')}월 ${String(day || '01').padStart(2, '0')}일 ${String(hour || '00').padStart(2, '0')}:${String(minute || '00').padStart(2, '0')}`;
            } else if (currentLanguage === 'en') {
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const monthName = monthNames[parseInt(month || '9') - 1] || 'Sep';
                formattedDate = `${monthName} ${day || '01'}, ${year || '2025'} ${String(hour || '00').padStart(2, '0')}:${String(minute || '00').padStart(2, '0')}`;
            } else {
                formattedDate = `${String(day || '01').padStart(2, '0')}/${String(month || '09').padStart(2, '0')}/${year || '2025'} ${String(hour || '00').padStart(2, '0')}:${String(minute || '00').padStart(2, '0')}`;
            }
            generationDate.innerHTML = dateLabel + ' ' + formattedDate;
        }

        // 데이터 기간 섹션 업데이트
        const dataPeriodTitle = document.getElementById('dataPeriodTitle');
        if (dataPeriodTitle) {
            dataPeriodTitle.innerHTML = getTranslation('headers.dataPeriod.title', currentLanguage) || '📊 사용 데이터 기간:';
        }

        // Update data period items with correct IDs and translations
        const updateDataPeriodItem = (elementId, labelKey, startDay, endDay) => {
            const element = document.getElementById(elementId);
            if (element) {
                const year = element.getAttribute('data-year') || '2025';
                const month = element.getAttribute('data-month') || '09';
                const label = getTranslation(`headers.dataPeriod.${labelKey}`, currentLanguage) || labelKey;

                let dateFormat;
                if (currentLanguage === 'ko') {
                    const start = startDay ? `${month}월 ${startDay}일` : `${month}월`;
                    const end = endDay ? `${month}월 ${endDay}일` : '';
                    dateFormat = endDay ? `${year}년 ${start} ~ ${end}` : `${year}년 ${start} 기준`;
                } else if (currentLanguage === 'en') {
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    const monthName = monthNames[parseInt(month) - 1] || 'Sep';
                    const start = startDay ? `${monthName} ${startDay}` : monthName;
                    const end = endDay ? `${monthName} ${endDay}` : '';
                    dateFormat = endDay ? `${start} - ${end}, ${year}` : `${monthName} ${year} Standard`;
                } else { // Vietnamese
                    const start = startDay ? `${startDay}/${month}` : `Tháng ${month}`;
                    const end = endDay ? `${endDay}/${month}` : '';
                    dateFormat = endDay ? `${start} ~ ${end}/${year}` : `Tiêu chuẩn ${start}/${year}`;
                }

                element.innerHTML = `• ${label}: ${dateFormat}`;
            }
        };

        // Update each data period line
        updateDataPeriodItem('dataPeriodIncentive', 'incentiveData', '01', '30');
        updateDataPeriodItem('dataPeriodAttendance', 'attendanceData', '01', '23');
        updateDataPeriodItem('dataPeriodAQL', 'aqlData', '01', '30');
        updateDataPeriodItem('dataPeriod5PRS', '5prsData', '03', '23');
        updateDataPeriodItem('dataPeriodBasic', 'manpowerData', null, null);

        // 각 데이터 기간 항목 업데이트 (기존 코드 제거)
        const dataPeriodItems = [];

        dataPeriodItems.forEach(item => {
            const element = document.getElementById(item.id);
            if (element) {
                const year = element.getAttribute('data-year');
                const month = element.getAttribute('data-month');
                const startDay = element.getAttribute('data-startday');
                const endDay = element.getAttribute('data-endday');
                const dataLabel = getTranslation('headers.dataPeriod.' + item.key, currentLanguage);

                let periodText;
                if (item.key === 'manpowerData') {
                    // 기본 인력 데이터는 월 기준만 표시
                    if (currentLanguage === 'ko') {
                        periodText = `• $null: $null년 $null월 기준`;
                    } else if (currentLanguage === 'en') {
                        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                        periodText = `• $null: Based on ${monthNames[parseInt(month)-1]} $null`;
                    } else {
                        periodText = `• $null: Dựa trên tháng $null/$null`;
                    }
                } else {
                    // 다른 데이터는 기간 표시
                    if (currentLanguage === 'ko') {
                        periodText = `• $null: $null년 $null월 $null일 ~ $null일`;
                    } else if (currentLanguage === 'en') {
                        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                        periodText = `• $null: ${monthNames[parseInt(month)-1]} $null - $null, $null`;
                    } else {
                        periodText = `• $null: $null/$null - $null/$null/$null`;
                    }
                }
                element.innerHTML = periodText;
            }
        });

        // 요약 카드 라벨 업데이트
        const cardLabels = {
            'totalEmployeesLabel': 'summary.cards.totalEmployees',
            'paidEmployeesLabel': 'summary.cards.paidEmployees',
            'eligibleEmployeesLabel': 'summary.cards.eligibleEmployees',
            'paymentRateLabel': 'summary.cards.paymentRate',
            'totalAmountLabel': 'summary.cards.totalAmount'
        };
        
        for (const [id, key] of Object.entries(cardLabels)) {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = getTranslation(key, currentLanguage);
        }
        
        // 단위 업데이트
        const units = document.querySelectorAll('#totalEmployeesUnit, #paidEmployeesUnit');
        units.forEach(unit => {
            if (unit) unit.textContent = getTranslation('common.people', currentLanguage);
        });
        
        // 탭 메뉴 업데이트
        const tabs = {
            'tabSummary': 'tabs.summary',
            'tabPosition': 'tabs.position',
            'tabIndividual': 'tabs.individual',
            'tabCriteria': 'tabs.criteria',
            'tabOrgChart': 'tabs.orgChart'
        };
        
        for (const [id, key] of Object.entries(tabs)) {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = getTranslation(key, currentLanguage);
        }
        
        // 탭 컨텐츠 제목 업데이트
        const tabTitles = {
            'summaryTabTitle': 'summary.typeTable.title',
            'positionTabTitle': 'position.title',
            'individualDetailTitle': 'individual.title'
        };
        
        for (const [id, key] of Object.entries(tabTitles)) {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = getTranslation(key, currentLanguage);
        }
        
        // 요약 테이블 헤더 업데이트
        const summaryHeaders = {
            'summaryTypeHeader': 'summary.typeTable.columns.type',
            'summaryTotalHeader': 'summary.typeTable.columns.totalEmployees',
            'summaryEligibleHeader': 'summary.typeTable.columns.eligible',
            'summaryPaymentRateHeader': 'summary.typeTable.columns.paymentRate',
            'summaryTotalAmountHeader': 'summary.typeTable.columns.totalAmount',
            'summaryAvgAmountHeader': 'summary.cards.avgAmount',
            'summaryAvgEligibleHeader': 'summary.chartLabels.recipientBased',
            'summaryAvgTotalHeader': 'summary.chartLabels.totalBased'
        };
        
        for (const [id, key] of Object.entries(summaryHeaders)) {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = getTranslation(key, currentLanguage);
        }
        
        // 개인별 상세 테이블 헤더 업데이트
        const individualHeaders = {
            'empIdHeader': 'individual.table.columns.employeeId',
            'nameHeader': 'individual.table.columns.name',
            'positionHeader': 'individual.table.columns.position',
            'typeHeader': 'individual.table.columns.type',
            'statusHeader': 'individual.table.columns.status',
            'detailsHeader': 'individual.table.columns.details'
        };
        
        for (const [id, key] of Object.entries(individualHeaders)) {
            const elem = document.getElementById(id);
            if (elem) elem.textContent = getTranslation(key, currentLanguage);
        }

        // 월별 헤더 동적 업데이트
        const prevMonthHeader = document.getElementById('prevMonthHeader');
        const currentMonthHeader = document.getElementById('currentMonthHeader');

        // 이전 월과 현재 월 이름 설정
        const prevMonthName = 'null';
        const currentMonthName = 'null';

        if (prevMonthHeader) {
            if (currentLanguage === 'ko') {
                prevMonthHeader.textContent = '{get_korean_month(prev_month_name)}';
            } else if (currentLanguage === 'en') {
                prevMonthHeader.textContent = prevMonthName.charAt(0).toUpperCase() + prevMonthName.slice(1);
            } else {
                // Vietnamese
                const monthNum = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}[prevMonthName.toLowerCase()];
                prevMonthHeader.textContent = 'Tháng ' + monthNum;
            }
        }

        if (currentMonthHeader) {
            if (currentLanguage === 'ko') {
                currentMonthHeader.textContent = '{get_korean_month(month)}';
            } else if (currentLanguage === 'en') {
                currentMonthHeader.textContent = currentMonthName.charAt(0).toUpperCase() + currentMonthName.slice(1);
            } else {
                // Vietnamese
                const monthNum = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}[currentMonthName.toLowerCase()];
                currentMonthHeader.textContent = 'Tháng ' + monthNum;
            }
        }
        
        // 필터 업데이트
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.placeholder = getTranslation('individual.filters.search', currentLanguage);
        }
        
        // 필터 옵션 텍스트 업데이트
        const optAllTypes = document.getElementById('optAllTypes');
        if (optAllTypes) optAllTypes.textContent = getTranslation('individual.filters.allTypes', currentLanguage);
        
        const optPaymentAll = document.getElementById('optPaymentAll');
        if (optPaymentAll) optPaymentAll.textContent = getTranslation('individual.filters.allStatus', currentLanguage);
        
        const optPaymentPaid = document.getElementById('optPaymentPaid');
        if (optPaymentPaid) optPaymentPaid.textContent = getTranslation('status.paid', currentLanguage);
        
        const optPaymentUnpaid = document.getElementById('optPaymentUnpaid');
        if (optPaymentUnpaid) optPaymentUnpaid.textContent = getTranslation('status.unpaid', currentLanguage);
        
        // Report Type Banner 업데이트
        const reportTypeBanner = document.getElementById('reportTypeBanner');
        if (reportTypeBanner) {
            const isInterim = false; // Will be set dynamically based on report generation date
            const reportType = isInterim ? 'interim' : 'final';

            // Title 업데이트
            const reportTypeTitle = document.getElementById('reportTypeTitle');
            if (reportTypeTitle) {
                reportTypeTitle.textContent = getTranslation('reportTypeBanner.' + reportType + '.title', currentLanguage);
            }

            // Description 업데이트
            const reportTypeDesc = document.getElementById('reportTypeDesc');
            if (reportTypeDesc) {
                reportTypeDesc.textContent = getTranslation('reportTypeBanner.' + reportType + '.description', currentLanguage);
            }

            // Generated on date 업데이트
            const generatedText = getTranslation('reportTypeBanner.generatedOn', currentLanguage);
            const dayText = currentLanguage === 'ko' ? 'null일' :
                           currentLanguage === 'en' ? 'Day null' :
                           'Ngày null';
            const dateSpan = reportTypeBanner.querySelector('span[style*="font-size: 0.85rem"]');
            if (dateSpan) {
                dateSpan.textContent = generatedText + ': ' + dayText;
            }
        }

        // Summary 테이블의 "명" 단위 업데이트
        const typeSummaryBody = document.getElementById('typeSummaryBody');
        if (typeSummaryBody) {
            const rows = typeSummaryBody.querySelectorAll('tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                // 2번째 칼럼 (Total)과 3번째 칼럼 (Eligible)에 "명" 단위가 있음
                if (cells.length > 2) {
                    // Total 칼럼 - 모든 가능한 단위를 체크
                    const totalText = cells[1].textContent;
                    if (totalText.includes('명') || totalText.includes('people') || totalText.includes('người')) {
                        // 숫자만 추출
                        const number = totalText.replace(/[^\\\\d]/g, '');
                        cells[1].textContent = number + getTranslation('common.people', currentLanguage);
                    }
                    // Eligible 칼럼 - 모든 가능한 단위를 체크
                    const eligibleText = cells[2].textContent;
                    if (eligibleText.includes('명') || eligibleText.includes('people') || eligibleText.includes('người')) {
                        // 숫자만 추출
                        const number = eligibleText.replace(/[^\\d]/g, '');
                        cells[2].textContent = number + getTranslation('common.people', currentLanguage);
                    }
                }
            });
        }
        
        // 인센티브 기준 탭 텍스트 업데이트
        updateCriteriaTabTexts();
        
        // Talent Program 섹션 텍스트 업데이트
        updateTalentProgramTexts();

        // Org Chart 텍스트 업데이트
        updateOrgChartUIText();

        // 차트 업데이트 (차트가 있는 경우)
        if (window.pieChart) {
            updateChartLabels();
        }
        
        // 직급별 테이블 및 개인별 테이블 재생성
        updateTabContents();
    }
    
    // 탭 콘텐츠 업데이트
    function updateTabContents() {
        // 개별 테이블 재생성
        generateEmployeeTable();
        generatePositionTables();
    }
    
    // 인센티브 기준 탭 텍스트 업데이트 - 완전한 동적 번역
    function updateCriteriaTabTexts() {
        // 메인 제목
        const criteriaTitle = document.getElementById('criteriaMainTitle');
        if (criteriaTitle) {
            criteriaTitle.textContent = getTranslation('criteria.mainTitle', currentLanguage);
        }
        
        // 핵심 원칙 섹션
        const corePrinciplesTitle = document.getElementById('corePrinciplesTitle');
        if (corePrinciplesTitle) {
            corePrinciplesTitle.innerHTML = getTranslation('criteria.corePrinciples.title', currentLanguage);
        }
        
        const corePrinciplesDesc1 = document.getElementById('corePrinciplesDesc1');
        if (corePrinciplesDesc1) {
            corePrinciplesDesc1.innerHTML = getTranslation('criteria.corePrinciples.description1', currentLanguage);
        }
        
        const corePrinciplesDesc2 = document.getElementById('corePrinciplesDesc2');
        if (corePrinciplesDesc2) {
            corePrinciplesDesc2.innerHTML = getTranslation('criteria.corePrinciples.description2', currentLanguage);
        }
        
        // 10가지 평가 조건 제목
        const evaluationTitle = document.getElementById('evaluationConditionsTitle');
        if (evaluationTitle) {
            evaluationTitle.textContent = getTranslation('criteria.evaluationConditions.title', currentLanguage);
        }
        
        // 테이블 헤더 업데이트
        const tableHeaders = document.querySelectorAll('#criteria table thead tr');
        tableHeaders.forEach(row => {
            const ths = row.querySelectorAll('th');
            if (ths.length === 4) {
                ths[0].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.number', currentLanguage);
                ths[1].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.conditionName', currentLanguage);
                ths[2].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.criteria', currentLanguage);
                ths[3].textContent = getTranslation('criteria.evaluationConditions.tableHeaders.description', currentLanguage);
            }
        });
        
        // 출근 조건 섹션
        const attendanceTitle = document.getElementById('attendanceConditionTitle');
        if (attendanceTitle) {
            attendanceTitle.textContent = getTranslation('criteria.conditions.attendance.title', currentLanguage);
        }
        
        // AQL 조건 섹션
        const aqlTitle = document.getElementById('aqlConditionTitle');
        if (aqlTitle) {
            aqlTitle.textContent = getTranslation('criteria.conditions.aql.title', currentLanguage);
        }
        
        // 5PRS 조건 섹션
        const prsTitle = document.getElementById('prsConditionTitle');
        if (prsTitle) {
            prsTitle.textContent = getTranslation('criteria.conditions.5prs.title', currentLanguage);
        }
        
        // 직급별 적용 조건 섹션
        const positionMatrixTitle = document.getElementById('positionMatrixTitle');
        if (positionMatrixTitle) {
            positionMatrixTitle.textContent = getTranslation('criteria.positionMatrix.title', currentLanguage);
        }
        
        // TYPE 헤더 업데이트
        const type1Header = document.getElementById('type1Header');
        if (type1Header) {
            type1Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type1', currentLanguage);
        }
        
        // TYPE-2, TYPE-3 헤더 및 테이블 내용 업데이트
        const type2Header = document.getElementById('type2Header');
        if (type2Header) {
            type2Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type2', currentLanguage);
        }
        
        const type3Header = document.getElementById('type3Header');
        if (type3Header) {
            type3Header.textContent = getTranslation('criteria.positionMatrix.typeHeaders.type3', currentLanguage);
        }
        
        // TYPE-2 테이블 내용
        const type2AllPositions = document.getElementById('type2AllPositions');
        if (type2AllPositions) {
            type2AllPositions.textContent = getTranslation('criteria.positionMatrix.type2Table.allType2', currentLanguage);
        }
        
        const type2FourConditions = document.getElementById('type2FourConditions');
        if (type2FourConditions) {
            type2FourConditions.textContent = getTranslation('criteria.positionMatrix.type2Table.fourConditions', currentLanguage);
        }
        
        const type2AttendanceOnly = document.getElementById('type2AttendanceOnly');
        if (type2AttendanceOnly) {
            type2AttendanceOnly.textContent = getTranslation('criteria.positionMatrix.type2Table.attendanceOnly', currentLanguage);
        }
        
        // TYPE-3 테이블 내용
        const type3NewMember = document.getElementById('type3NewMember');
        if (type3NewMember) {
            type3NewMember.textContent = getTranslation('criteria.positionMatrix.type3Table.newMember', currentLanguage);
        }
        
        const type3NoConditions = document.getElementById('type3NoConditions');
        if (type3NoConditions) {
            type3NoConditions.textContent = getTranslation('criteria.positionMatrix.type3Table.noConditions', currentLanguage);
        }
        
        const type3ZeroConditions = document.getElementById('type3ZeroConditions');
        if (type3ZeroConditions) {
            type3ZeroConditions.textContent = getTranslation('criteria.positionMatrix.type3Table.zeroConditions', currentLanguage);
        }
        
        const type3NewMemberNote = document.getElementById('type3NewMemberNote');
        if (type3NewMemberNote) {
            type3NewMemberNote.textContent = getTranslation('criteria.positionMatrix.type3Table.newMemberNote', currentLanguage);
        }
        
        // TYPE-2 테이블 헤더
        const type2Headers = document.querySelectorAll('.type2-header-position, .type2-header-conditions, .type2-header-count, .type2-header-notes');
        type2Headers.forEach(header => {
            if (header.classList.contains('type2-header-position')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
            } else if (header.classList.contains('type2-header-conditions')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
            } else if (header.classList.contains('type2-header-count')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
            } else if (header.classList.contains('type2-header-notes')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
            }
        });
        
        // TYPE-3 테이블 헤더
        const type3Headers = document.querySelectorAll('.type3-header-position, .type3-header-conditions, .type3-header-count, .type3-header-notes');
        type3Headers.forEach(header => {
            if (header.classList.contains('type3-header-position')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
            } else if (header.classList.contains('type3-header-conditions')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
            } else if (header.classList.contains('type3-header-count')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
            } else if (header.classList.contains('type3-header-notes')) {
                header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
            }
        });
        
        // TYPE-1 테이블 조건 수 업데이트 
        const conditionCounts = document.querySelectorAll('.condition-count');
        conditionCounts.forEach(count => {
            const num = count.textContent.replace(/\\D/g, '');
            if (currentLanguage === 'ko') {
                count.textContent = num + '개';
            } else if (currentLanguage === 'en') {
                count.textContent = num;
            } else if (currentLanguage === 'vi') {
                count.textContent = num;
            }
        });
        
        // 직급 테이블 헤더
        const positionHeaders = document.querySelectorAll('.pos-header-position');
        positionHeaders.forEach(header => {
            header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.position', currentLanguage);
        });
        
        const conditionHeaders = document.querySelectorAll('.pos-header-conditions');
        conditionHeaders.forEach(header => {
            header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.appliedConditions', currentLanguage);
        });
        
        const countHeaders = document.querySelectorAll('.pos-header-count');
        countHeaders.forEach(header => {
            header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.conditionCount', currentLanguage);
        });
        
        const notesHeaders = document.querySelectorAll('.pos-header-notes');
        notesHeaders.forEach(header => {
            header.textContent = getTranslation('criteria.positionMatrix.tableHeaders.notes', currentLanguage);
        });
        
        // 인센티브 금액 계산 섹션
        const incentiveAmountTitle = document.querySelectorAll('#criteria .card')[2]?.querySelector('.card-header h5');
        if (incentiveAmountTitle) {
            incentiveAmountTitle.textContent = getTranslation('criteria.incentiveAmount.title', currentLanguage);
        }
        
        // Incentive Amount Table Translations
        const assemblyIncentiveTitle = document.getElementById('assemblyInspectorIncentiveTitle');
        if (assemblyIncentiveTitle) {
            assemblyIncentiveTitle.textContent = getTranslation('incentiveCalculation.assemblyInspectorIncentiveTitle', currentLanguage);
        }
        
        document.querySelectorAll('.consecutive-achievement-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.consecutiveAchievementMonths', currentLanguage);
        });
        
        document.querySelectorAll('.incentive-amount-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.incentiveAmountVND', currentLanguage);
        });
        
        // Month texts in table
        document.querySelectorAll('.month-text-1').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month1', currentLanguage);
        });
        document.querySelectorAll('.month-text-2').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month2', currentLanguage);
        });
        document.querySelectorAll('.month-text-3').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month3', currentLanguage);
        });
        document.querySelectorAll('.month-text-4').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month4', currentLanguage);
        });
        document.querySelectorAll('.month-text-5').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month5', currentLanguage);
        });
        document.querySelectorAll('.month-text-6').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month6', currentLanguage);
        });
        document.querySelectorAll('.month-text-7').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month7', currentLanguage);
        });
        document.querySelectorAll('.month-text-8').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month8', currentLanguage);
        });
        document.querySelectorAll('.month-text-9').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month9', currentLanguage);
        });
        document.querySelectorAll('.month-text-10').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month10', currentLanguage);
        });
        document.querySelectorAll('.month-text-11').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month11', currentLanguage);
        });
        document.querySelectorAll('.month-text-12').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.simpleMonths.month12', currentLanguage);
        });
        document.querySelectorAll('.month-or-more').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.orMore', currentLanguage);
        });
        
        // TYPE-2 calculation section
        const type2CalcTitle = document.getElementById('type2CalculationTitle');
        if (type2CalcTitle) {
            type2CalcTitle.textContent = getTranslation('incentiveCalculation.type2CalculationTitle', currentLanguage);
        }
        
        document.querySelectorAll('.type2-principle-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleLabel', currentLanguage);
        });
        
        document.querySelectorAll('.type2-principle-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type2CalculationPrincipleText', currentLanguage);
        });
        
        document.querySelectorAll('.average-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.average', currentLanguage);
        })
        
        // TYPE-1 인센티브 계산 테이블 번역
        // 타이틀
        const type1CalcTitle = document.getElementById('type1CalculationTitle');
        if (type1CalcTitle) {
            type1CalcTitle.textContent = getTranslation('incentiveCalculation.type1Title', currentLanguage);
        }
        
        // 테이블 헤더
        document.querySelectorAll('.calc-header-position').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.tableHeaders.position', currentLanguage);
        });
        document.querySelectorAll('.calc-header-method').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.tableHeaders.calculationMethod', currentLanguage);
        });
        document.querySelectorAll('.calc-header-example').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.tableHeaders.actualExample', currentLanguage);
        });
        
        // 직급명
        document.querySelectorAll('.calc-position-manager').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.manager', currentLanguage);
        });
        document.querySelectorAll('.calc-position-amanager').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.aManager', currentLanguage);
        });
        document.querySelectorAll('.calc-position-vsupervisor').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.vSupervisor', currentLanguage);
        });
        document.querySelectorAll('.calc-position-groupleader').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.groupLeader', currentLanguage);
        });
        document.querySelectorAll('.calc-position-lineleader').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.lineLeader', currentLanguage);
        });
        document.querySelectorAll('.calc-position-aqlinspector').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.aqlInspector', currentLanguage);
        });
        document.querySelectorAll('.calc-position-assemblyinspector').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.assemblyInspector', currentLanguage);
        });
        document.querySelectorAll('.calc-position-audittraining').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.auditTraining', currentLanguage);
        });
        document.querySelectorAll('.calc-position-modelmaster').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.positions.modelMaster', currentLanguage);
        });
        
        // 계산 방법 관련 텍스트
        document.querySelectorAll('.calc-conditions-met').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.conditionsMet', currentLanguage);
        });
        document.querySelectorAll('.calc-incentive-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.incentive', currentLanguage);
        });
        document.querySelectorAll('.calc-line-leader-avg').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.lineLeaderAverage', currentLanguage);
        });
        document.querySelectorAll('.calc-calculation-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.calculation', currentLanguage);
        });
        document.querySelectorAll('.calc-condition-not-met-zero').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.conditionsNotMetZero', currentLanguage);
        });
        
        // 적용 조건 텍스트
        document.querySelectorAll('.calc-apply-condition-attendance').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.applyConditionAttendance', currentLanguage);
        });
        document.querySelectorAll('.calc-apply-condition-lineleader').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.applyConditionLineLeader', currentLanguage);
        });
        document.querySelectorAll('.calc-apply-condition-assembly').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.applyConditionAssembly', currentLanguage);
        });
        document.querySelectorAll('.calc-apply-condition-audit').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.applyConditionAudit', currentLanguage);
        });
        document.querySelectorAll('.calc-apply-condition-model').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.applyConditionModel', currentLanguage);
        });
        
        // 특별 계산 텍스트
        document.querySelectorAll('.calc-subordinate-incentive').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.subordinateIncentive', currentLanguage);
        });
        document.querySelectorAll('.calc-subordinate-total').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.subordinateTotal', currentLanguage);
        });
        document.querySelectorAll('.calc-receive-ratio').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.receivingRatio', currentLanguage);
        });
        document.querySelectorAll('.calc-special-calculation').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.specialCalculation', currentLanguage);
        });
        document.querySelectorAll('.calc-aql-evaluation').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.aqlEvaluation', currentLanguage);
        });
        document.querySelectorAll('.calc-cfa-certificate').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.cfaCertificate', currentLanguage);
        });
        document.querySelectorAll('.calc-cfa-holder-bonus').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.cfaHolderBonus', currentLanguage);
        });
        document.querySelectorAll('.calc-hwk-claim').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.hwkClaim', currentLanguage);
        });
        document.querySelectorAll('.calc-cfa-holder').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.cfaHolder', currentLanguage);
        });
        document.querySelectorAll('.calc-consecutive-month-incentive').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.consecutiveMonthIncentive', currentLanguage);
        });
        document.querySelectorAll('.calc-total-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.total', currentLanguage);
        });
        
        // 예시 관련 텍스트
        document.querySelectorAll('.calc-example-employee').forEach(el => {
            const employeeId = el.dataset.employee;
            el.textContent = getTranslation('incentiveCalculation.exampleEmployee', currentLanguage).replace('{null}', employeeId);
        });
        document.querySelectorAll('.calc-condition-not-met-days').forEach(el => {
            const days = el.dataset.days;
            el.textContent = getTranslation('incentiveCalculation.conditionNotMetDays', currentLanguage).replace('{null}', days);
        });
        document.querySelectorAll('.calc-example-consecutive').forEach(el => {
            const months = el.dataset.months;
            el.textContent = getTranslation('incentiveCalculation.exampleConsecutiveFulfillment', currentLanguage).replace('{null}', months);
        });
        document.querySelectorAll('.calc-example-max-achieved').forEach(el => {
            const months = el.dataset.months;
            el.textContent = getTranslation('incentiveCalculation.exampleMaxAchieved', currentLanguage).replace('{null}', months);
        });
        document.querySelectorAll('.calc-example-not-met-reset').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.exampleConditionsNotMetReset', currentLanguage);
        });
        document.querySelectorAll('.calc-consecutive-months').forEach(el => {
            const months = el.dataset.months;
            el.textContent = getTranslation('incentiveCalculation.consecutiveMonths', currentLanguage).replace('{null}', months);
        });
        
        // 조건 평가 텍스트
        document.querySelectorAll('.calc-attendance-rate').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.attendanceRate', currentLanguage);
        });
        document.querySelectorAll('.calc-unauthorized-absence').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.unauthorizedAbsence', currentLanguage);
        });
        document.querySelectorAll('.calc-working-days').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.workingDays', currentLanguage);
        });
        document.querySelectorAll('.calc-previous-month').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.previousMonth', currentLanguage);
        });
        document.querySelectorAll('.calc-current-month-eval').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.currentMonthEvaluation', currentLanguage);
        });
        document.querySelectorAll('.calc-all-attendance-met').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.allAttendanceConditionsMet', currentLanguage);
        });
        document.querySelectorAll('.calc-team-aql-no-fail').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.teamAqlNoConsecutiveFail', currentLanguage);
        });
        document.querySelectorAll('.calc-reject-rate').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.rejectRate', currentLanguage);
        });
        document.querySelectorAll('.calc-reset-to-zero').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.resetToZeroMonths', currentLanguage);
        });
        document.querySelectorAll('.calc-personal-aql-failures').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.personalAqlFailures', currentLanguage);
        });
        document.querySelectorAll('.calc-pass-rate').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.passRate', currentLanguage);
        });
        document.querySelectorAll('.calc-inspection-quantity').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.inspectionQuantity', currentLanguage);
        });
        
        // 일/개월/족/건 단위 변환
        document.querySelectorAll('.calc-days-text').forEach(el => {
            const days = el.dataset.days;
            const unit = parseInt(days) <= 1 ? getTranslation('common.day', currentLanguage) : getTranslation('common.days', currentLanguage);
            el.textContent = currentLanguage === 'ko' ? `$null$null` : `$null $null`;
        });
        document.querySelectorAll('.calc-months-text').forEach(el => {
            const months = el.dataset.months;
            const unit = getTranslation('incentiveCalculation.months', currentLanguage);
            el.textContent = currentLanguage === 'ko' ? `$null$null` : `$null $null`;
        });
        document.querySelectorAll('.calc-pieces-text').forEach(el => {
            const pieces = el.dataset.pieces;
            const unit = getTranslation('incentiveCalculation.pieces', currentLanguage);
            el.textContent = currentLanguage === 'ko' ? `$null$null` : `$null $null`;
        });
        document.querySelectorAll('.calc-cases-text').forEach(el => {
            const cases = el.dataset.cases;
            const unit = getTranslation('incentiveCalculation.cases', currentLanguage);
            el.textContent = currentLanguage === 'ko' ? `$null$null` : `$null $null`;
        });
        
        // Month range translations
        document.querySelectorAll('.calc-month-range-0to1').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month0to1', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-1').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month1', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-2').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month2', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-3').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month3', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-4').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month4', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-5').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month5', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-6').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month6', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-7').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month7', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-8').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month8', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-9').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month9', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-9plus').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month9plus', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-10').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month10', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-11').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month11', currentLanguage);
        });
        document.querySelectorAll('.calc-month-range-12plus').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.monthRanges.month12plus', currentLanguage);
        });
        document.querySelectorAll('.calc-level-a').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.levelA', currentLanguage);
        })
        
        // 특별 규칙 섹션
        const specialRulesTitle = document.querySelectorAll('#criteria .card')[3]?.querySelector('.card-header h5');
        if (specialRulesTitle) {
            specialRulesTitle.textContent = getTranslation('criteria.specialRules.title', currentLanguage);
        }
        
        // Good to Know 섹션
        const goodToKnowTitle = document.getElementById('goodToKnowTitle');
        if (goodToKnowTitle) {
            goodToKnowTitle.textContent = getTranslation('criteria.goodToKnow.title', currentLanguage);
        }
        
        const corePrinciplesSubtitle = document.getElementById('corePrinciplesSubtitle');
        if (corePrinciplesSubtitle) {
            corePrinciplesSubtitle.textContent = getTranslation('criteria.goodToKnow.corePrinciplesSubtitle', currentLanguage);
        }
        
        // FAQ 섹션
        const faqTitle = document.querySelectorAll('#criteria .card')[4]?.querySelector('.card-header h5');
        if (faqTitle) {
            faqTitle.textContent = getTranslation('criteria.faq.title', currentLanguage);
        }
        
        // FAQ 계산 예시 섹션 번역
        updateFAQExamples();
        
        // 출근율 계산 방식 섹션 번역
        updateAttendanceSection();
        
        // FAQ Q&A 섹션 번역
        updateFAQQASection();
        
        // TYPE-3 섹션 번역
        const type3SectionTitle = document.getElementById('type3SectionTitle');
        if (type3SectionTitle) {
            type3SectionTitle.textContent = getTranslation('incentiveCalculation.type3Section.title', currentLanguage);
        }
        
        document.querySelectorAll('.type3-position-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.position', currentLanguage);
        });
        document.querySelectorAll('.type3-standard-incentive-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.standardIncentive', currentLanguage);
        });
        document.querySelectorAll('.type3-calculation-method-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.calculationMethod', currentLanguage);
        });
        document.querySelectorAll('.type3-new-qip-member').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.newQipMember', currentLanguage);
        });
        document.querySelectorAll('.type3-no-incentive').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.noIncentive', currentLanguage);
        });
        document.querySelectorAll('.type3-one-month-training').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.oneMonthTraining', currentLanguage);
        });
        document.querySelectorAll('.type3-type-reclassification').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.type3Section.typeReclassification', currentLanguage);
        });
        
        // Good to Know 섹션 번역
        const goodToKnowTitleElem = document.getElementById('goodToKnowTitle');
        if (goodToKnowTitleElem) {
            goodToKnowTitleElem.innerHTML = '💡 ' + getTranslation('incentiveCalculation.goodToKnow.title', currentLanguage);
        }
        
        const corePrinciplesTitleElem = document.getElementById('corePrinciplesSubtitle');
        if (corePrinciplesTitleElem) {
            corePrinciplesTitleElem.textContent = getTranslation('incentiveCalculation.goodToKnow.corePrinciples', currentLanguage);
        }
        
        document.querySelectorAll('.failure-principle-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage).split(':')[0] + ':';
        });
        document.querySelectorAll('.failure-principle-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.failurePrinciple', currentLanguage);
        });
        
        document.querySelectorAll('.type2-principle-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage).split(':')[0] + ':';
        });
        document.querySelectorAll('.type2-principle-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.type2Principle', currentLanguage);
        });
        
        document.querySelectorAll('.consecutive-bonus-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage).split(':')[0] + ':';
        });
        document.querySelectorAll('.consecutive-bonus-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.consecutiveBonus', currentLanguage);
        });
        
        document.querySelectorAll('.special-calculation-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage).split(':')[0] + ':';
        });
        document.querySelectorAll('.special-calculation-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.specialCalculation', currentLanguage);
        });
        
        document.querySelectorAll('.condition-failure-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage).split(':')[0] + ':';
        });
        document.querySelectorAll('.condition-failure-text').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage).split(':')[1] || getTranslation('incentiveCalculation.goodToKnow.conditionFailure', currentLanguage);
        });
        
        // 월별 인센티브 변동 요인 테이블
        const monthlyChangeTitle = document.getElementById('monthlyIncentiveChangeReasonsTitle');
        if (monthlyChangeTitle) {
            monthlyChangeTitle.textContent = getTranslation('incentiveCalculation.goodToKnow.monthlyIncentiveChangeReasons', currentLanguage);
        }
        
        document.querySelectorAll('.change-factors-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.changeFactors', currentLanguage);
        });
        document.querySelectorAll('.impact-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.impact', currentLanguage);
        });
        document.querySelectorAll('.example-header').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.example', currentLanguage);
        });
        
        document.querySelectorAll('.minimum-days-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.minimumDays', currentLanguage);
        });
        document.querySelectorAll('.less-than-12-days').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan12Days', currentLanguage);
        });
        document.querySelectorAll('.november-11-days').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.november11Days', currentLanguage);
        });
        
        document.querySelectorAll('.attendance-rate-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.attendanceRate', currentLanguage);
        });
        document.querySelectorAll('.less-than-88-percent').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan88Percent', currentLanguage);
        });
        document.querySelectorAll('.attendance-example').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.attendanceExample', currentLanguage);
        });
        
        document.querySelectorAll('.unauthorized-absence-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.unauthorizedAbsence', currentLanguage);
        });
        document.querySelectorAll('.more-than-3-days').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.moreThan3Days', currentLanguage);
        });
        document.querySelectorAll('.unauthorized-example').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.unauthorizedExample', currentLanguage);
        });
        
        document.querySelectorAll('.aql-failure-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.aqlFailure', currentLanguage);
        });
        document.querySelectorAll('.current-month-failure').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.currentMonthFailure', currentLanguage);
        });
        document.querySelectorAll('.aql-failure-example').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.aqlFailureExample', currentLanguage);
        });
        
        document.querySelectorAll('.fprs-pass-rate-label').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.fprsPassRate', currentLanguage);
        });
        document.querySelectorAll('.less-than-95-percent').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.lessThan95Percent', currentLanguage);
        });
        document.querySelectorAll('.fprs-example').forEach(el => {
            el.textContent = getTranslation('incentiveCalculation.goodToKnow.fprsExample', currentLanguage);
        });
        
        // 조건 테이블 내용 업데이트
        updateConditionTablesContent();
    }
    
    // 조건 테이블 내용 동적 업데이트 함수
    function updateConditionTablesContent() {
        // 출근 조건 테이블 업데이트
        const attendanceTable = document.getElementById('attendanceTable');
        if (attendanceTable) {
            const tbody = attendanceTable.querySelector('tbody');
            if (tbody) {
                const rows = tbody.querySelectorAll('tr');
                if (rows.length >= 4) {
                    // 조건 1: 출근율
                    rows[0].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.name', currentLanguage);
                    rows[0].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.criteria', currentLanguage);
                    rows[0].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.attendanceRate.description', currentLanguage);
                    
                    // 조건 2: 무단결근
                    rows[1].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.name', currentLanguage);
                    rows[1].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.criteria', currentLanguage);
                    rows[1].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.unapprovedAbsence.description', currentLanguage);
                    
                    // 조건 3: 실제 근무일
                    rows[2].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.name', currentLanguage);
                    rows[2].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.criteria', currentLanguage);
                    rows[2].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.actualWorkingDays.description', currentLanguage);
                    
                    // 조건 4: 최소 근무일
                    rows[3].cells[1].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.name', currentLanguage);
                    rows[3].cells[2].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.criteria', currentLanguage);
                    rows[3].cells[3].textContent = getTranslation('criteria.conditions.attendance.items.minimumWorkingDays.description', currentLanguage);
                }
            }
        }
        
        // AQL 조건 테이블 업데이트
        const aqlTable = document.getElementById('aqlTable');
        if (aqlTable) {
            const tbody = aqlTable.querySelector('tbody');
            if (tbody) {
                const rows = tbody.querySelectorAll('tr');
                if (rows.length >= 4) {
                    // 조건 5: 개인 AQL (당월)
                    rows[0].cells[1].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.name', currentLanguage);
                    rows[0].cells[2].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.criteria', currentLanguage);
                    rows[0].cells[3].textContent = getTranslation('criteria.conditions.aql.items.personalFailure.description', currentLanguage);
                    
                    // 조건 6: 개인 AQL (연속성)
                    rows[1].cells[1].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.name', currentLanguage);
                    rows[1].cells[2].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.criteria', currentLanguage);
                    rows[1].cells[3].textContent = getTranslation('criteria.conditions.aql.items.personalContinuous.description', currentLanguage);
                    
                    // 조건 7: 팀/구역 AQL
                    rows[2].cells[1].textContent = getTranslation('criteria.conditions.aql.items.teamArea.name', currentLanguage);
                    rows[2].cells[2].textContent = getTranslation('criteria.conditions.aql.items.teamArea.criteria', currentLanguage);
                    rows[2].cells[3].textContent = getTranslation('criteria.conditions.aql.items.teamArea.description', currentLanguage);
                    
                    // 조건 8: 담당구역 reject
                    rows[3].cells[1].textContent = getTranslation('criteria.conditions.aql.items.areaReject.name', currentLanguage);
                    rows[3].cells[2].textContent = getTranslation('criteria.conditions.aql.items.areaReject.criteria', currentLanguage);
                    rows[3].cells[3].textContent = getTranslation('criteria.conditions.aql.items.areaReject.description', currentLanguage);
                }
            }
        }
        
        // 5PRS 조건 테이블 업데이트
        const prsTable = document.getElementById('prsTable');
        if (prsTable) {
            const tbody = prsTable.querySelector('tbody');
            if (tbody) {
                const rows = tbody.querySelectorAll('tr');
                if (rows.length >= 2) {
                    // 조건 9: 5PRS 통과율
                    rows[0].cells[1].textContent = getTranslation('criteria.conditions.5prs.items.passRate.name', currentLanguage);
                    rows[0].cells[2].textContent = getTranslation('criteria.conditions.5prs.items.passRate.criteria', currentLanguage);
                    rows[0].cells[3].textContent = getTranslation('criteria.conditions.5prs.items.passRate.description', currentLanguage);
                    
                    // 조건 10: 5PRS 검사량
                    rows[1].cells[1].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.name', currentLanguage);
                    rows[1].cells[2].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.criteria', currentLanguage);
                    rows[1].cells[3].textContent = getTranslation('criteria.conditions.5prs.items.inspectionQty.description', currentLanguage);
                }
            }
        }
        
        // 직급별 특이사항 업데이트
        updatePositionMatrixNotes();
    }
    
    // 직급별 특이사항 동적 업데이트
    function updatePositionMatrixNotes() {
        // TYPE-1 테이블의 특이사항 컬럼 업데이트
        const type1Tables = document.querySelectorAll('#criteria table');
        type1Tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (tbody) {
                const rows = tbody.querySelectorAll('tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length === 4) {
                        const noteText = cells[3].textContent.trim();
                        // 특이사항 매핑
                        if (noteText.includes('출근 조건만') || noteText.includes('Attendance only')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceOnly', currentLanguage);
                        } else if (noteText.includes('출근 + 팀/구역 AQL') && !noteText.includes('reject')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAql', currentLanguage);
                        } else if (noteText.includes('특별 계산') || noteText.includes('Special calculation')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceMonthAql', currentLanguage);
                        } else if (noteText.includes('출근 + 개인 AQL + 5PRS')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendancePersonalAql5prs', currentLanguage);
                        } else if (noteText.includes('출근 + 팀/구역 AQL + 담당구역 reject')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceTeamAreaReject', currentLanguage);
                        } else if (noteText.includes('출근 + 담당구역 reject')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.attendanceAreaReject', currentLanguage);
                        } else if (noteText.includes('모든 조건') || noteText.includes('All conditions')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.allConditions', currentLanguage);
                        } else if (noteText.includes('조건 없음') || noteText.includes('No conditions')) {
                            cells[3].textContent = getTranslation('criteria.positionMatrix.notes.noConditions', currentLanguage);
                        }
                    }
                });
            }
        });
    }
    
    // 차트 라벨 업데이트
    function updateChartLabels() {
        // 예제 차트 업데이트 코드
    }

    // Summary Cards 업데이트 함수
    function updateSummaryCards() {
        if (!window.employeeData || window.employeeData.length === 0) {
            console.warn('No employee data available');
            return;
        }

        // 인센티브를 받는 직원 수 계산
        const paidEmployees = window.employeeData.filter(emp =>
            getIncentiveAmount(emp) > 0
        );

        // 총 인센티브 금액 계산
        const totalAmount = window.employeeData.reduce((sum, emp) =>
            sum + getIncentiveAmount(emp), 0
        );

        // 지급률 계산
        const paymentRate = window.employeeData.length > 0 ?
            (paidEmployees.length / window.employeeData.length * 100).toFixed(1) : 0;

        // Summary card elements 업데이트 (ID에 Value suffix가 있는 경우와 없는 경우 모두 처리)
        // 전체 직원 수
        const totalEmpEl = document.getElementById('totalEmployeesValue') || document.getElementById('totalEmployees');
        if (totalEmpEl) totalEmpEl.textContent = window.employeeData.length + '명';

        // 수령 직원 수
        const paidEmpEl = document.getElementById('paidEmployeesValue') || document.getElementById('paidEmployees');
        if (paidEmpEl) paidEmpEl.textContent = paidEmployees.length + '명';

        // 지급률
        const paymentRateEl = document.getElementById('paymentRateValue') || document.getElementById('paymentRate');
        if (paymentRateEl) paymentRateEl.textContent = paymentRate + '%';

        // 총 지급액
        const totalAmountEl = document.getElementById('totalAmountValue') || document.getElementById('totalAmount');
        if (totalAmountEl) totalAmountEl.textContent = totalAmount.toLocaleString() + ' VND';

        console.log('Summary cards updated:', {
            total: window.employeeData.length,
            paid: paidEmployees.length,
            rate: paymentRate + '%',
            amount: totalAmount
        });
    }

    // Type별 요약 테이블 업데이트 함수
    function updateTypeSummaryTable() {
        // Type별 데이터 집계
        const typeData = {
            'TYPE-1': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-2': { total: 0, paid: 0, totalAmount: 0 },
            'TYPE-3': { total: 0, paid: 0, totalAmount: 0 }
        };

        // 전체 데이터 집계
        let grandTotal = 0;
        let grandPaid = 0;
        let grandAmount = 0;

        // 직원 데이터 순회하며 집계
        employeeData.forEach(emp => {
            // type 필드를 여러 가능한 이름에서 찾기
            const type = emp.type || emp['ROLE TYPE STD'] || emp['Type'] || 'UNKNOWN';
            if (typeData[type]) {
                typeData[type].total++;
                grandTotal++;

                // Check multiple possible field names for incentive amount
                const amount = getIncentiveAmount(emp) ||
                              parseInt(emp['September_Incentive']) || 0;
                if (amount > 0) {
                    typeData[type].paid++;
                    typeData[type].totalAmount += amount;
                    grandPaid++;
                    grandAmount += amount;
                }
            }
        });

        // 언어별 단위 설정
        const personUnit = currentLanguage === 'ko' ? '명' :
                          currentLanguage === 'en' ? ' people' :
                          ' người';

        // 테이블 tbody 업데이트
        const tbody = document.getElementById('typeSummaryBody');
        if (tbody) {
            let html = '';

            // 각 Type별 행 생성
            ['TYPE-1', 'TYPE-2', 'TYPE-3'].forEach(type => {
                const data = typeData[type];
                const paymentRate = data.total > 0 ? (data.paid / data.total * 100).toFixed(1) : '0.0';
                const avgPaid = data.paid > 0 ? Math.round(data.totalAmount / data.paid) : 0;
                const avgTotal = data.total > 0 ? Math.round(data.totalAmount / data.total) : 0;
                const typeClass = type.toLowerCase().replace('type-', '');

                html += '<tr>';
                html += '<td><span class="type-badge type-' + typeClass + '">' + type + '</span></td>';
                html += '<td>' + String(data.total) + personUnit + '</td>';
                html += '<td>' + String(data.paid) + personUnit + '</td>';
                html += '<td>' + paymentRate + '%</td>';
                html += '<td>' + data.totalAmount.toLocaleString() + ' VND</td>';
                html += '<td>' + avgPaid.toLocaleString() + ' VND</td>';
                html += '<td>' + avgTotal.toLocaleString() + ' VND</td>';
                html += '</tr>';
            });

            // 합계 행 생성
            const totalPaymentRate = grandTotal > 0 ? (grandPaid / grandTotal * 100).toFixed(1) : '0.0';
            const totalAvgPaid = grandPaid > 0 ? Math.round(grandAmount / grandPaid) : 0;
            const totalAvgTotal = grandTotal > 0 ? Math.round(grandAmount / grandTotal) : 0;

            html += '<tr style="font-weight: bold; background-color: #f3f4f6;">';
            html += '<td>Total</td>';
            html += '<td>' + String(grandTotal) + personUnit + '</td>';
            html += '<td>' + String(grandPaid) + personUnit + '</td>';
            html += '<td>' + totalPaymentRate + '%</td>';
            html += '<td>' + grandAmount.toLocaleString() + ' VND</td>';
            html += '<td>' + totalAvgPaid.toLocaleString() + ' VND</td>';
            html += '<td>' + totalAvgTotal.toLocaleString() + ' VND</td>';
            html += '</tr>';

            tbody.innerHTML = html;
        }
    }
    
    // 초기화
    // 조직도 관련 함수들
    let orgChartData = null;
    let orgChartRoot = null;

    // 검증 탭 관련 함수들
    function initValidationTab() {
        console.log('Initializing validation tab...');

        // 중간 보고서 여부 확인
        const generationDate = document.getElementById('generationDate');
        const reportDay = generationDate ? parseInt(generationDate.getAttribute('data-day')) : 0;
        const isInterimReport = reportDay < 20;

        // 중간 보고서 알림 표시
        if (isInterimReport) {
            const notice = document.getElementById('interimReportNotice');
            if (notice) {
                notice.style.display = 'block';
            }
        }

        // KPI 카드 값 계산 및 표시
        updateValidationKPIs(isInterimReport);

        // 탭 제목과 라벨 번역 업데이트
        updateValidationTexts();
    }

    function updateValidationKPIs(isInterimReport) {
        // 기존 employeeData에서 직접 값을 가져옴 (새로운 계산 없음)

        // 1. 총 근무일수 - config에서 가져온 값 사용 (employee별 데이터가 아님)
        const totalWorkingDays = null; // Python에서 주입된 값
        document.getElementById('kpiTotalWorkingDays').textContent = totalWorkingDays + '일';

        // 2. 무단결근 3일 이상 (unapproved_absences > 2)
        const ar1Over3 = employeeData.filter(emp =>
            parseFloat(emp['unapproved_absences'] || 0) > 2
        ).length;
        document.getElementById('kpiAbsentWithoutInform').textContent = ar1Over3 + '명';

        // 3. 실제 근무일 0일 (9월 현재 재직자만)
        const zeroWorkingDays = employeeData.filter(emp => {
            const actualDays = parseFloat(emp['Actual Working Days'] || emp['actual_working_days'] || 0);
            // employeeData는 이미 9월 기준 필터링된 401명
            return actualDays === 0;
        }).length;
        document.getElementById('kpiZeroWorkingDays').textContent = zeroWorkingDays + '명';

        // 4. 최소 근무일 미충족 (중간 보고서면 N/A)
        if (isInterimReport) {
            document.getElementById('kpiMinimumDaysNotMet').textContent = 'N/A';
            document.getElementById('kpiMinimumDaysNotMet').parentElement.style.opacity = '0.5';
        } else {
            const minimumDaysNotMet = employeeData.filter(emp => {
                // Excel의 Minimum_Days_Met 필드 사용 (Single Source of Truth)
                const minimumDaysMet = emp['Minimum_Days_Met'];
                if (minimumDaysMet !== undefined) {
                    return minimumDaysMet === false || minimumDaysMet === 'False' || minimumDaysMet === 0;
                }
                // 폴백: 이전 방식
                return emp['condition4'] === 'yes' || emp['attendancy condition 4 - minimum working days'] === 'yes';
            }).length;
            document.getElementById('kpiMinimumDaysNotMet').textContent = minimumDaysNotMet + '명';
        }

        
        
        // 5. 출근율 88% 미만
        const attendanceBelow88 = employeeData.filter(emp =>
            parseFloat(emp['attendance_rate'] || 0) < 88
        ).length;
        document.getElementById('kpiAttendanceBelow88').textContent = attendanceBelow88 + '명';

        // 6. AQL FAIL 보유자 (모든 직원 대상)
        const aqlFailEmployees = employeeData.filter(emp => {
            // September AQL Failures 컬럼 확인 (Excel 데이터에서 직접 가져옴)
            const aqlFailures = parseFloat(emp['September AQL Failures'] || emp['aql_failures'] || 0);
            return aqlFailures > 0;
        }).length;
        document.getElementById('kpiAqlFail').textContent = aqlFailEmployees + '명';

        // 7. 3개월 연속 AQL FAIL (Excel의 Continuous_FAIL 컬럼 사용)
        const consecutiveFail = employeeData.filter(emp => {
            const continuous_fail = emp['Continuous_FAIL'] || emp['continuous_fail'] || 'NO';
            return continuous_fail === 'YES_3MONTHS';
        }).length;
        document.getElementById('kpiConsecutiveAqlFail').textContent = consecutiveFail + '명';

        // 8. 구역 AQL Reject Rate 3% 초과 직원 수 (조건 8번만 카운트)
        const highRejectRate = employeeData.filter(emp => {
            // 조건 8번: 구역 reject rate > 3%만 체크 (조건 7번 제외)
            const cond8 = emp['cond_8_area_reject'] || 'PASS';
            const areaRejectRate = parseFloat(emp['Area_Reject_Rate'] || emp['area_reject_rate'] || 0);
            return cond8 === 'FAIL' || areaRejectRate > 3;
        }).length;
        document.getElementById('kpiAreaRejectRate').textContent = highRejectRate + '명';

        // 9. 5PRS 통과율 < 95% (TYPE-1 ASSEMBLY INSPECTOR만)
        const lowPassRate = employeeData.filter(emp => {
            const isType1 = emp['type'] === 'TYPE-1';
            const position = (emp['position'] || '').toUpperCase();
            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
            const passRate = parseFloat(emp['pass_rate'] || 100);
            return isType1 && isAssemblyInspector && passRate < 95 && passRate > 0;
        }).length;
        document.getElementById('kpiLowPassRate').textContent = lowPassRate + '명';

        // 10. 5PRS 검사량 < 100족 (TYPE-1 ASSEMBLY INSPECTOR만)
        const lowInspectionQty = employeeData.filter(emp => {
            const isType1 = emp['type'] === 'TYPE-1';
            const position = (emp['position'] || '').toUpperCase();
            const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
            const inspectionQty = parseFloat(emp['validation_qty'] || 0);
            return isType1 && isAssemblyInspector && inspectionQty < 100;
        }).length;
        document.getElementById('kpiLowInspectionQty').textContent = lowInspectionQty + '명';
    }

    function updateValidationTexts() {
        // 검증 탭 텍스트 번역 업데이트
        const tabTitle = document.getElementById('validationTabTitle');
        if (tabTitle) {
            tabTitle.textContent = getTranslation('validationTab.title', currentLanguage);
        }

        const interimText = document.getElementById('interimReportText');
        if (interimText) {
            interimText.textContent = getTranslation('validationTab.interimNotice', currentLanguage);
        }

        // KPI 카드 라벨 업데이트
        document.querySelectorAll('.kpi-label').forEach((label, index) => {
            const kpiKeys = [
                'totalWorkingDays', 'absentWithoutInform', 'zeroWorkingDays',
                'minimumDaysNotMet', 'attendanceBelow88', 'aqlFail', 'consecutiveAqlFail',
                'areaRejectRate', 'lowPassRate', 'lowInspectionQty'
            ];
            if (kpiKeys[index]) {
                label.textContent = getTranslation(`validationTab.kpiCards.${kpiKeys[index]}.title`, currentLanguage);
            }
        });
    }

    // 개선된 모달 함수들 추가
    null

    // 검증 모달 표시 함수
    function showValidationModal(conditionType) {
        console.log('Showing validation modal for:', conditionType);

        // 새로운 개선된 모달 함수 호출
        if (conditionType === 'totalWorkingDays') {
            showTotalWorkingDaysDetails();
            return;
        } else if (conditionType === 'zeroWorkingDays') {
            showZeroWorkingDaysDetails();
            return;
        } else if (conditionType === 'absentWithoutInform') {
            showAbsentWithoutInformDetails();
            return;
        } else if (conditionType === 'minimumDaysNotMet') {
            showMinimumDaysNotMetDetails();
            return;
        } else if (conditionType === 'attendanceBelow88') {
            showAttendanceBelow88Details();
            return;
        } else if (conditionType === 'aqlFail') {
            showAqlFailDetails();
            return;
        } else if (conditionType === 'consecutiveAqlFail') {
            showConsecutiveAqlFailDetails();
            return;
        } else if (conditionType === 'areaRejectRate') {
            showAreaRejectRateDetails();
            return;
        } else if (conditionType === 'lowPassRate') {
            showLowPassRateDetails();
            return;
        } else if (conditionType === 'lowInspectionQty') {
            showLowInspectionQtyDetails();
            return;
        }

        // 기존 모달 처리 (다른 타입의 경우)
        const modalHtml = createValidationModalContent(conditionType);

        // 기존 모달 제거
        const existingModal = document.getElementById('validationModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 모달 추가
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 모달 표시
        const modal = document.getElementById('validationModal');
        if (modal) {
            modal.style.display = 'block';

            // 테이블 정렬 기능 초기화
            initSortableTable('validationModalTable');

            // 검색 필터 초기화
            initTableFilter('validationModalSearch', 'validationModalTable');
        }
    }

    function createValidationModalContent(conditionType) {
        let modalTitle = '';
        let tableHeaders = [];
        let tableData = [];

        // 중간 보고서 여부 확인
        const generationDate = document.getElementById('generationDate');
        const reportDay = generationDate ? parseInt(generationDate.getAttribute('data-day')) : 0;
        const isInterimReport = reportDay < 20;

        switch(conditionType) {
            case 'totalWorkingDays':
                modalTitle = getTranslation('validationTab.modalTitles.totalWorkingDays', currentLanguage);
                tableHeaders = ['날짜', '요일', '근무 인원수'];
                // 실제로는 일별 데이터가 없으므로 총 근무일수만 표시
                const totalDays = employeeData[0]?.['Total Working Days'] || 13;
                tableData = [[
                    `$null년 $null월`,
                    '-',
                    `총 $null일`
                ]];
                break;

            case 'absentWithoutInform':
                modalTitle = getTranslation('validationTab.modalTitles.absentWithoutInform', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.ar1Days', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];
                tableData = employeeData
                    .filter(emp => parseFloat(emp['Unapproved Absences'] || 0) > 2)
                    .map(emp => [
                        emp['Employee No'],
                        emp['Full Name'],
                        emp['FINAL QIP POSITION NAME CODE'],
                        emp['Unapproved Absences'],
                        emp['attendancy condition 2 - unapproved Absence Day is more than 2 days'] || 'FAIL'
                    ]);
                break;

            case 'zeroWorkingDays':
                modalTitle = getTranslation('validationTab.modalTitles.zeroWorkingDays', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.totalDays', currentLanguage),
                    getTranslation('validationTab.tableHeaders.actualDays', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];
                tableData = employeeData
                    .filter(emp => parseFloat(emp['Actual Working Days'] || 0) === 0)
                    .map(emp => [
                        emp['Employee No'],
                        emp['Full Name'],
                        emp['FINAL QIP POSITION NAME CODE'],
                        emp['Total Working Days'] || 13,
                        emp['Actual Working Days'],
                        emp['attendancy condition 1 - acctual working days is zero'] || 'FAIL'
                    ]);
                break;

            case 'minimumDaysNotMet':
                modalTitle = getTranslation('validationTab.modalTitles.minimumDaysNotMet', currentLanguage);
                const isInterim = new Date().getDate() < 20;
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.actualDays', currentLanguage),
                    getTranslation('validationTab.tableHeaders.minimumRequired', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];

                // 중간보고 시에는 조건 4를 적용하지 않음
                if (isInterim) {
                    tableData = []; // 중간보고 시 표시 안함
                } else {
                    const totalWorkingDays = parseFloat(employeeData[0]?.['Total Working Days'] || 13);
                    const minDays = Math.ceil(totalWorkingDays / 2);
                    tableData = employeeData
                        .filter(emp => parseFloat(emp['Actual Working Days'] || 0) < minDays)
                        .map(emp => [
                            emp['Employee No'],
                            emp['Full Name'],
                            emp['FINAL QIP POSITION NAME CODE'],
                            emp['Actual Working Days'],
                            minDays,
                            emp['attendancy condition 4 - minimum working days'] || 'FAIL'
                        ]);
                }
                break;

            case 'aqlFail':
                modalTitle = getTranslation('validationTab.modalTitles.aqlFail', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.type', currentLanguage),
                    getTranslation('validationTab.tableHeaders.aqlFailures', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];

                // TYPE-1에서 조건 5가 적용되는 포지션만 필터링
                const aqlPositions = ['SUPERVISOR', 'A.MANAGER', 'MANAGER', 'S.MANAGER', 'AQL INSPECTOR'];
                tableData = employeeData
                    .filter(emp => {
                        const position = (emp['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();
                        const isType1 = emp['ROLE TYPE STD'] === 'TYPE-1';
                        const hasAqlCondition = aqlPositions.some(pos => position.includes(pos));
                        const hasAqlFail = parseFloat(emp['September AQL Failures'] || 0) > 0;
                        return isType1 && hasAqlCondition && hasAqlFail;
                    })
                    .map(emp => [
                        emp['Employee No'],
                        emp['Full Name'],
                        emp['FINAL QIP POSITION NAME CODE'],
                        emp['ROLE TYPE STD'] || 'TYPE-1',
                        emp['September AQL Failures'],
                        emp['cond_5_aql_personal_failure'] || 'FAIL'
                    ]);
                break;

            case 'consecutiveAqlFail':
                // This case is now handled by showConsecutiveAqlFailDetails()
                // But we still need to handle it here as a fallback
                modalTitle = getTranslation('validationTab.modalTitles.consecutiveAqlFail', currentLanguage);
                tableHeaders = ['직원번호', '이름', '직책', '연속 실패 개월'];
                tableData = employeeData
                    .filter(emp => emp['Consecutive_Fail_Months'] > 0)
                    .map(emp => [
                        emp['Employee No'],
                        emp['Full Name'],
                        emp['QIP POSITION 1ST  NAME'] || '-',
                        emp['Consecutive_Fail_Months'] + '개월'
                    ]);
                break;

            case 'areaRejectRate':
                modalTitle = getTranslation('validationTab.modalTitles.areaRejectRate', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.area', currentLanguage),
                    getTranslation('validationTab.tableHeaders.rejectRate', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];

                // Area AQL reject rate > 3% 필터링 (구역별 AQL Reject 3% 이상)
                tableData = employeeData
                    .filter(emp => parseFloat(emp['area_reject_rate'] || 0) > 3)
                    .map(emp => [
                        emp['Employee No'],
                        emp['Full Name'],
                        emp['area'] || '-',
                        (parseFloat(emp['area_reject_rate'] || 0).toFixed(2)) + '%',
                        emp['aql condition 7 - team area or reject'] || 'FAIL'
                    ]);
                break;

            case 'lowPassRate':
                modalTitle = getTranslation('validationTab.modalTitles.lowPassRate', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.type', currentLanguage),
                    getTranslation('validationTab.tableHeaders.passRate', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];

                // TYPE-1 ASSEMBLY INSPECTOR만 필터링
                tableData = employeeData
                    .filter(emp => {
                        const position = (emp['position'] || '').toUpperCase();
                        const isType1 = emp['type'] === 'TYPE-1';
                        const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
                        const lowPassRate = parseFloat(emp['pass_rate'] || 100) < 95;
                        return isType1 && isAssemblyInspector && lowPassRate;
                    })
                    .map(emp => [
                        emp['emp_no'],
                        emp['name'],
                        emp['position'],
                        emp['type'] || 'TYPE-1',
                        (parseFloat(emp['pass_rate'] || 0).toFixed(1)) + '%',
                        emp['cond_9_5prs_pass_rate'] || 'FAIL'
                    ]);
                break;

            case 'lowInspectionQty':
                modalTitle = getTranslation('validationTab.modalTitles.lowInspectionQty', currentLanguage);
                tableHeaders = [
                    getTranslation('validationTab.tableHeaders.employeeNo', currentLanguage),
                    getTranslation('validationTab.tableHeaders.name', currentLanguage),
                    getTranslation('validationTab.tableHeaders.position', currentLanguage),
                    getTranslation('validationTab.tableHeaders.type', currentLanguage),
                    getTranslation('validationTab.tableHeaders.inspectionQty', currentLanguage),
                    getTranslation('validationTab.tableHeaders.conditionStatus', currentLanguage)
                ];

                // TYPE-1 ASSEMBLY INSPECTOR만 필터링
                tableData = employeeData
                    .filter(emp => {
                        const position = (emp['position'] || '').toUpperCase();
                        const isType1 = emp['type'] === 'TYPE-1';
                        const isAssemblyInspector = position.includes('ASSEMBLY') && position.includes('INSPECTOR');
                        const lowQty = parseFloat(emp['validation_qty'] || 0) < 100;
                        return isType1 && isAssemblyInspector && lowQty;
                    })
                    .map(emp => [
                        emp['emp_no'],
                        emp['name'],
                        emp['position'],
                        emp['type'] || 'TYPE-1',
                        emp['validation_qty'] || '0',
                        emp['cond_10_5prs_inspection_qty'] || 'FAIL'
                    ]);
                break;

            default:
                modalTitle = 'Details';
                tableHeaders = ['No Data'];
                tableData = [['No data available']];
        }

        // 모달 HTML 생성
        return `
            <div id="validationModal" class="modal" onclick="if(event.target === this) closeValidationModal();" style="display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
                <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 0; border: 1px solid #888; width: 80%; max-width: 1200px; border-radius: 10px;">
                    <div class="modal-header" style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px 10px 0 0;">
                        <span class="close" onclick="closeValidationModal()" style="color: white; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
                        <h2>$null</h2>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
                        <div class="search-box" style="margin-bottom: 20px;">
                            <input type="text" id="validationModalSearch" placeholder="${getTranslation('validationTab.tableHeaders.searchPlaceholder', currentLanguage)}"
                                   style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        </div>
                        <div style="overflow-x: auto;">
                            <table id="validationModalTable" class="table" style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background-color: #f2f2f2;">
                                        ${tableHeaders.map((header, index) => `
                                            <th onclick="sortValidationTable($null)" style="cursor: pointer; padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">
                                                $null <span class="sort-icon">↕</span>
                                            </th>
                                        `).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableData.map(row => `
                                        <tr>
                                            ${row.map(cell => `<td style="padding: 10px; border-bottom: 1px solid #ddd;">${cell || '-'}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer" style="padding: 20px; text-align: right; border-top: 1px solid #ddd;">
                        <button onclick="closeValidationModal()" class="btn btn-secondary" style="padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            ${getTranslation('validationTab.tableHeaders.close', currentLanguage)}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function closeValidationModal() {
        const modal = document.getElementById('validationModal');
        if (modal) {
            modal.remove();
        }
    }

    function initSortableTable(tableId) {
        // 테이블 정렬 기능 초기화
        const table = document.getElementById(tableId);
        if (!table) return;

        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.setAttribute('data-sort-direction', 'none');
        });
    }

    function sortValidationTable(columnIndex) {
        const table = document.getElementById('validationModalTable');
        if (!table) return;

        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = table.querySelectorAll('th')[columnIndex];

        let sortDirection = header.getAttribute('data-sort-direction') || 'none';
        sortDirection = sortDirection === 'none' || sortDirection === 'desc' ? 'asc' : 'desc';

        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();

            // 숫자 비교
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }

            // 문자열 비교
            if (sortDirection === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });

        // 정렬된 행 다시 추가
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        // 정렬 방향 업데이트
        header.setAttribute('data-sort-direction', sortDirection);

        // 정렬 아이콘 업데이트
        table.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↕');
        header.querySelector('.sort-icon').textContent = sortDirection === 'asc' ? '↑' : '↓';
    }

    function initTableFilter(searchInputId, tableId) {
        const searchInput = document.getElementById(searchInputId);
        const table = document.getElementById(tableId);

        if (!searchInput || !table) return;

        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.querySelector('tbody').querySelectorAll('tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    // 인센티브 기준 탭 렌더링 함수
    function renderCriteriaTab() {
        console.log('인센티브 기준 탭 렌더링 시작...');
        const criteriaContent = document.getElementById('criteriaContent');

        if (!criteriaContent) {
            console.error('criteriaContent 요소를 찾을 수 없습니다.');
            return;
        }

        // HTML 내용 생성
        let html = `
            <div class="alert alert-info mb-4">
                <h5 class="alert-heading">📌 핵심 원칙</h5>
                <p class="mb-2">모든 직원은 해당 직급별로 지정된 <strong>모든 조건을 충족</strong>해야 인센티브를 받을 수 있습니다.</p>
                <p class="mb-0">조건은 출근(4개), AQL(4개), 5PRS(2개)로 구성되며, 직급별로 적용 조건이 다릅니다.</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5>TYPE-1 (관리자급)</h5>
                        </div>
                        <div class="card-body">
                            <ul>
                                <li>대상: Manager, Assistant Manager, Supervisor 등</li>
                                <li>인센티브: 100,000 ~ 200,000 VND</li>
                                <li>조건: 출근 (4개) + AQL (4개)</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5>TYPE-2 (검사원)</h5>
                        </div>
                        <div class="card-body">
                            <ul>
                                <li>대상: Inspector, Line Leader 등</li>
                                <li>인센티브: 50,000 ~ 100,000 VND</li>
                                <li>조건: 출근 (4개) + AQL (4개) + 5PRS (2개)</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h5>TYPE-3 (신입)</h5>
                        </div>
                        <div class="card-body">
                            <ul>
                                <li>대상: 신규 QIP 멤버</li>
                                <li>인센티브: 0 VND</li>
                                <li>조건: 정책 제외 (조건 검증 없음)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <h4>조건 세부사항</h4>
                <table class="table table-bordered">
                    <thead>
                        <tr class="table-dark">
                            <th>조건 카테고리</th>
                            <th>조건명</th>
                            <th>설명</th>
                            <th>기준</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td rowspan="4" class="align-middle bg-light"><strong>출근 조건</strong></td>
                            <td>ATTENDANCE_RATE</td>
                            <td>출근율</td>
                            <td>≥ 0.9 (90%)</td>
                        </tr>
                        <tr>
                            <td>ATTENDANCE_WARNING</td>
                            <td>출근 경고</td>
                            <td>경고 없음</td>
                        </tr>
                        <tr>
                            <td>ATTENDANCE_STRAIGHT_5_DAYS</td>
                            <td>연속 5일 출근</td>
                            <td>주당 연속 5일</td>
                        </tr>
                        <tr>
                            <td>ATTENDANCE_LATE_LEAVE_6_TIMES</td>
                            <td>지각/조퇴 제한</td>
                            <td>< 6회</td>
                        </tr>
                        <tr>
                            <td rowspan="4" class="align-middle bg-light"><strong>AQL 조건</strong></td>
                            <td>AQL_GENERAL_SR</td>
                            <td>일반 AQL 등급</td>
                            <td>SR 등급 이하</td>
                        </tr>
                        <tr>
                            <td>AQL_APPEARANCE</td>
                            <td>외관 품질</td>
                            <td>SR 등급 이하</td>
                        </tr>
                        <tr>
                            <td>AQL_MEASUREMENT</td>
                            <td>측정 품질</td>
                            <td>SR 등급 이하</td>
                        </tr>
                        <tr>
                            <td>AQL_SOP</td>
                            <td>SOP 준수</td>
                            <td>SR 등급 이하</td>
                        </tr>
                        <tr>
                            <td rowspan="2" class="align-middle bg-light"><strong>5PRS 조건</strong></td>
                            <td>FIVE_PRS_OUTPUT</td>
                            <td>산출량 달성</td>
                            <td>≥ 100%</td>
                        </tr>
                        <tr>
                            <td>FIVE_PRS_QUALITY</td>
                            <td>품질 달성</td>
                            <td>≥ 95%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;

        criteriaContent.innerHTML = html;
        console.log('인센티브 기준 탭 렌더링 완료');
    }

    // renderCriteriaTab 함수를 window 객체에 추가하여 전역 사용 가능하도록
    window.renderCriteriaTab = renderCriteriaTab;

    // 통합된 초기화 함수
    function initializeDashboard() {
        console.log('=== 대시보드 초기화 시작 ===');
        console.log('Total employees:', employeeData ? employeeData.length : 'No data');

        // 1. Bootstrap 툴팁 초기화
        try {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            console.log('Bootstrap tooltips initialized:', tooltipList.length);
        } catch(e) {
            console.error('Tooltip 초기화 오류:', e);
        }

        // 2. D3.js 라이브러리 확인
        if (typeof d3 === 'undefined') {
            console.error('D3.js library not loaded!');
            setTimeout(initializeDashboard, 500); // 재시도
            return;
        }
        console.log('D3.js version:', d3.version);

        // 3. 언어 설정 복원
        const savedLang = localStorage.getItem('dashboardLanguage') || 'ko';
        currentLanguage = savedLang;
        const langSelector = document.getElementById('languageSelector');
        if (langSelector) {
            langSelector.value = savedLang;
        }

        // 4. 요약 탭 초기화 (중요!)
        console.log('요약 탭 초기화...');
        updateSummaryCards();
        updateTypeSummaryTable();

        // 5. 직급별 테이블 초기화
        console.log('직급별 테이블 초기화...');
        try {
            generatePositionTables();
        } catch(e) {
            console.error('직급별 테이블 오류:', e);
        }

        // 6. 전체 직원 테이블 초기화
        console.log('전체 직원 테이블 초기화...');
        try {
            generateEmployeeTable();
        } catch(e) {
            console.error('직원 테이블 오류:', e);
        }

        // 7. 인센티브 기준 탭 초기화
        console.log('인센티브 기준 탭 초기화...');
        try {
            if (typeof renderCriteriaTab === 'function') {
                renderCriteriaTab();
            } else {
                console.warn('renderCriteriaTab 함수가 없습니다.');
                // Fallback: 기본 내용 표시
                const criteriaContent = document.getElementById('criteriaContent');
                if (criteriaContent && typeof conditionData !== 'undefined') {
                    criteriaContent.innerHTML = '<h5>인센티브 조건 매트릭스</h5>' +
                        '<pre>' + JSON.stringify(conditionData, null, 2) + '</pre>';
                }
            }
        } catch(e) {
            console.error('인센티브 기준 탭 오류:', e);
        }

        // 8. 시스템 검증 탭 초기화
        console.log('시스템 검증 탭 초기화...');
        try {
            initValidationTab();
        } catch(e) {
            console.error('검증 탭 오류:', e);
        }

        // 9. Talent Pool 섹션 업데이트
        console.log('Talent Pool 초기화...');
        try {
            updateTalentPoolSection();
        } catch(e) {
            console.error('Talent Pool 오류:', e);
        }

        // 10. 필터 초기화
        try {
            updatePositionFilter();
        } catch(e) {
            console.error('필터 초기화 오류:', e);
        }

        // 11. 탭 이벤트 리스너 등록
        setupTabEventListeners();

        // 12. Individual Details 탭 Observer 설정
        setupIndividualDetailsObserver();

        // 13. 텍스트 업데이트
        updateAllTexts();

        // 14. 기본 탭 표시
        showTab('summary');

        console.log('=== 대시보드 초기화 완료 ===');
    }

    // 탭 이벤트 리스너 설정 함수
    function setupTabEventListeners() {
        console.log('탭 이벤트 리스너 설정...');

        // 조직도 탭 이벤트
        const orgChartTabButton = document.querySelector('[data-bs-target="#orgchart"]') ||
                                  document.querySelectorAll('.nav-link')[3];

        if (orgChartTabButton) {
            console.log('조직도 탭 버튼 발견');
            orgChartTabButton.addEventListener('shown.bs.tab', function() {
                console.log('조직도 탭 활성화 - 차트 그리기');
                drawOrgChart();
            });

            orgChartTabButton.addEventListener('click', function() {
                setTimeout(() => {
                    const orgTab = document.getElementById('orgchart');
                    if (orgTab && orgTab.classList.contains('active')) {
                        drawOrgChart();
                    }
                }, 100);
            });
        }

        // 다른 탭 이벤트도 필요시 여기에 추가
    }

    // Individual Details 탭 Observer 설정
    function setupIndividualDetailsObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.id === 'detail' && mutation.target.classList.contains('active')) {
                    renderIndividualDetailsTab();
                }
            });
        });

        const detailTab = document.getElementById('detail');
        if (detailTab) {
            observer.observe(detailTab, { attributes: true, attributeFilter: ['class'] });
        }
    }

    // 단일 DOMContentLoaded 이벤트로 통합
    document.addEventListener('DOMContentLoaded', function() {
        console.log('=== DOMContentLoaded 이벤트 발생 ===');

        // 데이터 로딩 확인 후 초기화
        if (typeof employeeData === 'undefined') {
            console.warn('employeeData가 아직 로드되지 않았습니다. 500ms 후 재시도...');
            setTimeout(initializeDashboard, 500);
        } else {
            initializeDashboard();
        }
    });

    // 직급 계층 레벨 정의
    function getPositionLevel(position) {
        const pos = position.toUpperCase();
        // S.Manager가 최상위
        if (pos.includes('S.MANAGER') || pos.includes('SENIOR MANAGER')) return 1;
        // Manager가 S.Manager의 부하
        if (pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT')) return 2;
        // A.Manager가 Manager의 부하
        if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT MANAGER')) return 3;
        // Supervisor가 A.Manager의 부하
        if (pos.includes('SUPERVISOR')) return 4;
        // Group Leader
        if (pos.includes('GROUP') && pos.includes('LEADER')) return 5;
        // Line Leader
        if (pos.includes('LINE') && pos.includes('LEADER')) return 6;
        // Inspector
        if (pos.includes('INSPECTOR')) return 7;
        // Others
        return 8;
    }

    // Breadcrumb 업데이트 함수
    function updateBreadcrumb(current) {
        const breadcrumb = document.getElementById('orgBreadcrumb');
        if (breadcrumb) {
            breadcrumb.innerHTML = `
                <span style="color: #666;">조직도</span>
                <span style="color: #999;"> › </span>
                <span style="color: #333; font-weight: bold;">$null</span>
            `;
        }
    }

    // 줌 컨트롤 함수들
    let currentZoomBehavior = null;

    function zoomIn() {
        const svg = d3.select("#orgChartSvg");
        if (currentZoomBehavior && svg.node()) {
            svg.transition().duration(300).call(
                currentZoomBehavior.scaleBy, 1.3
            );
        }
    }

    function zoomOut() {
        const svg = d3.select("#orgChartSvg");
        if (currentZoomBehavior && svg.node()) {
            svg.transition().duration(300).call(
                currentZoomBehavior.scaleBy, 0.7
            );
        }
    }

    function resetZoom() {
        const svg = d3.select("#orgChartSvg");
        if (currentZoomBehavior && svg.node()) {
            svg.transition().duration(500).call(
                currentZoomBehavior.transform,
                d3.zoomIdentity
            );
        }
    }

    // 인센티브 값을 안전하게 파싱하는 헬퍼 함수
    function parseIncentive(value) {
        if (!value) return 0;
        // 문자열 형태의 값 처리
        const strValue = String(value).trim();
        // 쉼표 제거 후 파싱
        const parsed = parseInt(strValue.replace(/,/g, ''), 10);
        return isNaN(parsed) ? 0 : parsed;
    }

    // 인센티브 수령 여부 확인 함수
    function hasIncentive(data) {
        const amount = parseIncentive(data.incentive || data[dashboardMonth + '_incentive'] || 0);
        return amount > 0;
    }

    // 직급별 색상 정의
    function getPositionColor(position) {
        if (!position) return '#8c564b'; // Others (brown)
        const pos = position.toUpperCase();

        if (pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT')) {
            return '#1f77b4'; // Manager (blue)
        }
        if (pos.includes('SUPERVISOR')) {
            return '#2ca02c'; // Supervisor (green)
        }
        if (pos.includes('GROUP') && pos.includes('LEADER')) {
            return '#ff7f0e'; // Group Leader (orange)
        }
        if (pos.includes('LINE') && pos.includes('LEADER')) {
            return '#d62728'; // Line Leader (red)
        }
        if (pos.includes('INSPECTOR')) {
            return '#9467bd'; // Inspector (purple)
        }
        return '#8c564b'; // Others (brown)
    }

    // 새로운 접이식 조직도 그리기 함수
    function drawOrgChart() {
        console.log('Drawing new collapsible org chart...');
        drawCollapsibleOrgChart();
    }

    function drawCollapsibleOrgChart() {
        console.log('🏗️ === 조직도 그리기 시작 ===');
        console.log('   Employee Data 수:', employeeData ? employeeData.length : 0);
        console.log('   Dashboard Month:', dashboardMonth);

        const container = document.getElementById('orgTreeContent');
        if (!container) {
            console.error('orgTreeContent container not found!');
            return;
        }

        // 로딩 표시
        container.innerHTML = `<div class="org-loading"><div class="org-loading-spinner"></div><p>${getTranslation('orgChart.loadingMessage')}</p></div>`;

        // 계층 구조 데이터 생성
        const hierarchyData = buildHierarchyData();
        if (!hierarchyData || hierarchyData.length === 0) {
            container.innerHTML = `<div class="alert alert-warning">${getTranslation('orgChart.noDataMessage')}</div>`;
            return;
        }

        // HTML 트리 생성
        const treeHTML = buildTreeHTML(hierarchyData);
        container.innerHTML = treeHTML;

        // 이벤트 리스너 추가
        attachTreeEventListeners();

        // 통계 업데이트

        // UI 텍스트 업데이트
        updateOrgChartUIText();
    }

    // 계층 구조 데이터 빌드
    function buildHierarchyData() {
        console.log('Building TYPE-1 manager hierarchy data...');

        if (!employeeData || employeeData.length === 0) {
            console.error('No employee data available');
            return null;
        }

        // Special calculation positions 확인 함수
        function hasSpecialCalculation(position) {
            if (!position || !positionMatrix) return false;
            const pos = position.toUpperCase();

            // TYPE-1 positions 확인
            const type1Positions = positionMatrix.position_matrix?.['TYPE-1'] || {};

            // 각 직급 체크
            for (const [key, config] of Object.entries(type1Positions)) {
                if (key === 'default') continue;

                // patterns 매칭 확인
                if (config.patterns) {
                    for (const pattern of config.patterns) {
                        if (pos.includes(pattern.toUpperCase())) {
                            // special_calculation 필드 확인
                            if (config.special_calculation) {
                                return true;
                            }
                        }
                    }
                }
            }

            return false;
        }

        // TYPE-1 직원 중 관리자 포지션만 필터링 (special calculation 제외)
        const filteredEmployees = employeeData.filter(emp => {
            // TYPE-1이 아닌 경우 제외
            if (emp.type !== 'TYPE-1') {
                return false;
            }

            const position = (emp.position || '').toUpperCase();

            // Special calculation positions 제외 (AQL INSPECTOR, AUDIT & TRAINING, MODEL MASTER)
            if (hasSpecialCalculation(emp.position)) {
                console.log(`Excluding special calculation position: ${emp.position} - ${emp.name}`);
                return false;
            }

            // 관리자 포지션 확인 (부하 기반 계산하는 포지션)
            const isManager = position.includes('MANAGER') ||
                             position.includes('SUPERVISOR') ||
                             position.includes('GROUP LEADER') ||
                             position.includes('LINE LEADER');

            return isManager;
        });

        console.log(`Filtered employees: ${filteredEmployees.length} (excluded ${employeeData.length - filteredEmployees.length})`);

        // 직원 ID로 매핑
        const employeeMap = {};
        const rootNodes = [];

        // 먼저 필터된 직원을 맵에 저장
        filteredEmployees.forEach(emp => {
            // 인센티브 계산 방법 결정
            let calculationMethod = '';
            const pos = (emp.position || '').toUpperCase();

            if (pos.includes('LINE LEADER')) {
                calculationMethod = getTranslation('orgChart.calculationFormulas.lineLeader');
            } else if (pos.includes('GROUP LEADER')) {
                calculationMethod = getTranslation('orgChart.calculationFormulas.groupLeader');
            } else if (pos.includes('SUPERVISOR')) {
                calculationMethod = getTranslation('orgChart.calculationFormulas.supervisor');
            } else if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT')) {
                calculationMethod = getTranslation('orgChart.calculationFormulas.assistantManager');
            } else if (pos.includes('MANAGER')) {
                calculationMethod = getTranslation('orgChart.calculationFormulas.manager');
            }

            employeeMap[emp.emp_no] = {
                id: emp.emp_no,
                name: emp.name,
                position: emp.position,
                type: emp.type,
                incentive: emp[dashboardMonth + '_incentive'] || 0,
                boss_id: emp.boss_id,
                calculationMethod: calculationMethod,
                children: []
            };
        });

        // 부모-자식 관계 설정
        filteredEmployees.forEach(emp => {
            if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== '0') {
                const boss = employeeMap[emp.boss_id];
                if (boss) {
                    boss.children.push(employeeMap[emp.emp_no]);
                } else {
                    // 보스가 없으면 루트 노드로 추가
                    rootNodes.push(employeeMap[emp.emp_no]);
                }
            } else {
                // 보스 ID가 없으면 루트 노드
                rootNodes.push(employeeMap[emp.emp_no]);
            }
        });

        console.log(`Hierarchy built: ${rootNodes.length} root nodes`);
        return rootNodes;
    }

    // HTML 트리 생성
    function buildTreeHTML(nodes, depth = 0) {
        if (!nodes || nodes.length === 0) return '';

        let html = '<ul>';

        nodes.forEach(node => {
            const hasChildren = node.children && node.children.length > 0;
            const liClass = hasChildren ? 'expanded' : 'no-children';
            const nodeClass = getNodeClass(node.position);
            const incentiveClass = node.incentive > 0 ? 'has-incentive' : 'no-incentive';
            const incentiveDot = node.incentive > 0 ? 'received' : 'not-received';

            html += `<li class="$null">`;
            html += `<div class="org-node $null $null">`;

            // 인센티브 표시 점
            html += `<div class="node-incentive $null"></div>`;

            // 노드 내용
            html += `<div class="node-position">${node.position || 'N/A'}</div>`;
            html += `<div class="node-name">${node.name}</div>`;
            html += `<div class="node-id">ID: ${node.id}</div>`;

            // 인센티브 정보 (모든 경우 클릭 가능)
            const incentiveAmount = Number(node.incentive) || 0;
            const incentiveFormatted = incentiveAmount.toLocaleString('ko-KR');
            html += `<div class="node-incentive-info" data-node-id="${node.id}">`;
            html += `<div style="display: flex; align-items: center;">`;
            if (incentiveAmount > 0) {
                html += `<span class="incentive-amount">₫$null</span>`;
            } else {
                html += `<span class="incentive-amount" style="color: #dc3545;">₫0</span>`;
            }
            html += `</div>`;
            html += `<span class="incentive-detail-btn"
                        data-node-id="${node.id}"
                        title="클릭하여 상세 정보 보기"
                        role="button"
                        tabindex="0"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top">ℹ️</span>`;
            html += '</div>';

            // LINE LEADER의 경우 부하직원 표시
            if (node.position && node.position.toUpperCase().includes('LINE LEADER')) {
                // 부하직원 찾기 (인센티브 계산에 영향을 미치는 TYPE-1 부하만)
                const subordinates = employeeData.filter(emp =>
                    emp.boss_id === node.id &&
                    emp.type === 'TYPE-1'
                );

                const receivingCount = subordinates.filter(sub => {
                    const incentive = sub[dashboardMonth + '_incentive'] || 0;
                    return Number(incentive) > 0;
                }).length;

                if (subordinates.length > 0) {
                    html += `<div class="subordinate-info">`;
                    html += `<span class="subordinate-label">인센티브 계산 기반:</span>`;
                    html += `<span class="subordinate-count">TYPE-1 부하 $null/${subordinates.length}명</span>`;
                    html += '</div>';
                }
            }

            // 자식이 있으면 접기/펼치기 버튼과 자식 수 표시
            if (hasChildren) {
                html += `<span class="child-count">${node.children.length}</span>`;
                html += `<span class="toggle-btn"></span>`;
            }

            html += '</div>';

            // 재귀적으로 자식 노드 추가
            if (hasChildren) {
                html += buildTreeHTML(node.children, depth + 1);
            }

            html += '</li>';
        });

        html += '</ul>';
        return html;
    }

    // 노드 클래스 결정
    function getNodeClass(position) {
        if (!position) return 'default';
        const pos = position.toUpperCase();

        if (pos.includes('MANAGER') && !pos.includes('ASSISTANT')) return 'manager';
        if (pos.includes('SUPERVISOR')) return 'supervisor';
        if (pos.includes('GROUP LEADER')) return 'group-leader';
        if (pos.includes('LINE LEADER')) return 'line-leader';
        if (pos.includes('INSPECTOR')) return 'inspector';
        return 'default';
    }

    // 트리 이벤트 리스너
    function attachTreeEventListeners() {
        console.log('📎 attachTreeEventListeners 호출됨');

        // 정보 버튼 클릭 이벤트 - 이벤트 위임 방식으로 변경
        const treeContent = document.getElementById('orgTreeContent');
        if (treeContent) {
            // 기존 리스너 제거 (중복 방지)
            if (window.incentiveButtonHandler) {
                treeContent.removeEventListener('click', window.incentiveButtonHandler, true);
            }

            // 핸들러 함수를 전역에 저장하여 나중에 제거 가능
            window.incentiveButtonHandler = function(e) {
                console.log('🖱️ 클릭 이벤트 발생:', e.target.className);

                // 정보 버튼이 클릭된 경우
                if (e.target && e.target.classList && e.target.classList.contains('incentive-detail-btn')) {
                    console.log('ℹ️ 정보 버튼 클릭됨 (이벤트 위임)');
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();

                    const nodeId = e.target.getAttribute('data-node-id');
                    console.log('📌 노드 ID:', nodeId);
                    console.log('📌 모달 함수 존재:', typeof window.showIncentiveModal);

                    if (window.showIncentiveModal && nodeId) {
                        console.log('🎯 모달 함수 호출 시도:', nodeId);
                        try {
                            window.showIncentiveModal(nodeId);
                            console.log('✅ 모달 함수 호출 성공');
                        } catch(error) {
                            console.error('❌ 모달 함수 호출 중 오류:', error);
                        }
                    } else {
                        console.error('❌ 모달 함수가 없거나 노드 ID가 없음');
                        console.error('   - showIncentiveModal:', typeof window.showIncentiveModal);
                        console.error('   - nodeId:', nodeId);
                    }
                    return false;
                }
            };

            // 이벤트 위임으로 처리 (동적으로 생성되는 버튼도 처리 가능)
            treeContent.addEventListener('click', window.incentiveButtonHandler, true); // capture 단계에서 처리
            console.log('✅ 인센티브 버튼 이벤트 리스너 등록 완료');
        } else {
            console.error('❌ orgTreeContent 요소를 찾을 수 없음');
        }

        // 토글 버튼 클릭 이벤트
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const li = this.closest('li');
                if (li.classList.contains('collapsed')) {
                    li.classList.remove('collapsed');
                    li.classList.add('expanded');
                } else {
                    li.classList.remove('expanded');
                    li.classList.add('collapsed');
                }
            });
        });

        // 인센티브 정보 클릭 이벤트 (이벤트 위임 방식)
        console.log('📌 인센티브 클릭 이벤트 리스너 등록 중...');
        const orgContainer = document.getElementById('orgTreeContent');
        if (orgContainer) {
            // 기존 리스너 제거 (중복 방지)
            orgContainer.removeEventListener('click', handleIncentiveClick);
            // 새 리스너 추가
            orgContainer.addEventListener('click', handleIncentiveClick);
            console.log('✅ 이벤트 위임 리스너 등록 완료');
        }

        // 인센티브 클릭 핸들러 함수
        function handleIncentiveClick(e) {
            const incentiveInfo = e.target.closest('.node-incentive-info');
            if (incentiveInfo) {
                e.preventDefault();
                e.stopPropagation();
                const nodeId = incentiveInfo.getAttribute('data-node-id');
                console.log('💰 인센티브 클릭 감지 - Node ID:', nodeId);

                if (window.showIncentiveModal) {
                    window.showIncentiveModal(nodeId);
                } else {
                    console.error('❌ showIncentiveModal 함수가 없습니다');
                }
            }
        }

        // 조직도가 그려진 후 툴팁 재초기화
        setTimeout(() => {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
            console.log('✅ 조직도 툴팁 초기화 완료:', tooltipTriggerList.length, '개');
        }, 500);

        // 검색 기능
        const searchInput = document.getElementById('orgSearchInput');
        const searchClear = document.getElementById('orgSearchClear');

        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                searchInTree(searchTerm);
            });
        }

        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                searchInTree('');
            });
        }

        // 모두 펼치기/접기 버튼
        const expandAllBtn = document.getElementById('expandAllBtn');
        const collapseAllBtn = document.getElementById('collapseAllBtn');

        if (expandAllBtn) {
            expandAllBtn.addEventListener('click', function() {
                document.querySelectorAll('.collapsible-tree li').forEach(li => {
                    if (li.querySelector('.toggle-btn')) {
                        li.classList.remove('collapsed');
                        li.classList.add('expanded');
                    }
                });
            });
        }

        if (collapseAllBtn) {
            collapseAllBtn.addEventListener('click', function() {
                document.querySelectorAll('.collapsible-tree li').forEach(li => {
                    if (li.querySelector('.toggle-btn')) {
                        li.classList.remove('expanded');
                        li.classList.add('collapsed');
                    }
                });
            });
        }

        // 노드 클릭 이벤트 (인센티브 정보 클릭 제외)
        document.querySelectorAll('.org-node').forEach(node => {
            node.addEventListener('click', function(e) {
                // 인센티브 정보를 클릭한 경우는 제외
                if (e.target.closest('.node-incentive-info')) {
                    console.log('🚫 인센티브 클릭이므로 expand/collapse 무시');
                    return;
                }
                const toggleBtn = this.querySelector('.toggle-btn');
                if (toggleBtn) {
                    console.log('📂 노드 expand/collapse 토글');
                    toggleBtn.click();
                }
            });
        });
    }

    // 전체 펼치기
    function expandAll() {
        document.querySelectorAll('.collapsible-tree li.collapsed').forEach(li => {
            li.classList.remove('collapsed');
            li.classList.add('expanded');
        });
    }

    // 전체 접기
    function collapseAll() {
        document.querySelectorAll('.collapsible-tree li.expanded').forEach(li => {
            if (li.querySelector('ul')) { // 자식이 있는 경우만
                li.classList.remove('expanded');
                li.classList.add('collapsed');
            }
        });
    }

    // 검색 기능
    function searchInTree(searchTerm) {
        const nodes = document.querySelectorAll('.org-node');
        const allLis = document.querySelectorAll('.collapsible-tree li');

        if (!searchTerm) {
            // 검색어가 없으면 모두 표시
            nodes.forEach(node => {
                node.classList.remove('search-hidden');
                node.classList.remove('search-highlight');
            });
            return;
        }

        // 모든 노드 숨기기
        nodes.forEach(node => {
            node.classList.add('search-hidden');
            node.classList.remove('search-highlight');
        });

        // 검색어와 일치하는 노드 찾기
        nodes.forEach(node => {
            const name = node.querySelector('.node-name')?.textContent.toLowerCase() || '';
            const id = node.querySelector('.node-id')?.textContent.toLowerCase() || '';
            const position = node.querySelector('.node-position')?.textContent.toLowerCase() || '';

            if (name.includes(searchTerm) || id.includes(searchTerm) || position.includes(searchTerm)) {
                node.classList.remove('search-hidden');
                node.classList.add('search-highlight');

                // 부모 노드들도 표시
                let parent = node.closest('li');
                while (parent) {
                    const parentNode = parent.querySelector(':scope > .org-node');
                    if (parentNode) {
                        parentNode.classList.remove('search-hidden');
                    }
                    // 부모 li를 펼치기
                    if (parent.classList.contains('collapsed')) {
                        parent.classList.remove('collapsed');
                        parent.classList.add('expanded');
                    }
                    parent = parent.parentElement?.closest('li');
                }
            }
        });
    }

    // 모달 테스트 함수 (전역 스코프)
    // 모달 강제 닫기 함수 (전역 스코프)
    window.forceCloseModal = function() {
        console.log('🚨 모달 강제 닫기 실행');
        const modal = document.getElementById('incentiveModal');
        if (modal) {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
                modalInstance.dispose();
            }
            modal.remove();
        }
        // 백드롭과 body 상태 정리
        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    };

    // 팀 내 모든 LINE LEADER 찾기 (재귀적) - Excel 로직과 동일
    function findTeamLineLeaders(managerId, depth = 0, visited = null) {
        if (depth > 5) return []; // 무한 루프 방지

        if (!visited) {
            visited = new Set();
        }

        // managerId를 문자열로 통일
        managerId = String(managerId || '');
        if (!managerId || managerId === 'nan' || managerId === '0' || managerId === '') {
            return [];
        }

        if (visited.has(managerId)) {
            return [];
        }
        visited.add(managerId);

        let lineLeaders = [];

        // boss_id를 문자열로 비교하여 직접 부하들 찾기
        const directSubordinates = employeeData.filter(emp => {
            const bossId = String(emp.boss_id || '');
            return bossId === managerId && bossId !== '';
        });

        directSubordinates.forEach(sub => {
            const position = (sub.position || '').toUpperCase();

            // TYPE-1 LINE LEADER인 경우 추가
            if (sub.type === 'TYPE-1' && position.includes('LINE') && position.includes('LEADER')) {
                lineLeaders.push(sub);
            }

            // 재귀적으로 부하의 부하 탐색 (emp_no를 문자열로 변환)
            const subLineLeaders = findTeamLineLeaders(String(sub.emp_no || ''), depth + 1, visited);
            lineLeaders = lineLeaders.concat(subLineLeaders);
        });

        return lineLeaders;
    }

    // 인센티브 미지급 사유 분석 함수
    function getIncentiveFailureReasons(employee) {
        const reasons = [];
        const position = (employee.position || '').toUpperCase();

        // 출근 조건 체크 (모든 직급 공통)
        if (employee['attendancy condition 1 - acctual working days is zero'] === 'yes') {
            reasons.push('실제 근무일 0일 (출근 조건 1번 미충족)');
        }
        if (employee['attendancy condition 2 - unapproved Absence Day is more than 2 days'] === 'yes') {
            reasons.push('무단결근 2일 초과 (출근 조건 2번 미충족)');
        }
        if (employee['attendancy condition 3 - absent % is over 12%'] === 'yes') {
            reasons.push('결근율 12% 초과 (출근 조건 3번 미충족)');
        }
        if (employee['attendancy condition 4 - minimum working days'] === 'yes') {
            reasons.push('최소 근무일 미달 (출근 조건 4번 미충족)');
        }

        // LINE LEADER의 경우 AQL 조건 추가 체크
        if (position.includes('LINE') && position.includes('LEADER')) {
            if (employee['aql condition 7 - team/area fail AQL'] === 'yes') {
                reasons.push('팀/구역 AQL 실패 (AQL 조건 7번 미충족)');
            }
            if (employee['September AQL Failures'] > 0) {
                reasons.push(`9월 AQL 실패 ${employee['September AQL Failures']}건`);
            }
            if (employee['Continuous_FAIL'] === 'YES_3MONTHS') {
                reasons.push('3개월 연속 AQL 실패');
            } else if (employee['Continuous_FAIL'] && employee['Continuous_FAIL'].includes('2MONTHS')) {
                reasons.push('2개월 연속 AQL 실패');
            }
        }

        // 5PRS 조건 체크 (해당 직급만)
        if (employee['5prs condition 1 - there is  enough 5 prs validation qty or pass rate is over 95%'] === 'no') {
            reasons.push('5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)');
        }
        if (employee['5prs condition 2 - Total Valiation Qty is zero'] === 'yes') {
            reasons.push('5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)');
        }

        // 조건 통과율 체크
        if (employee['conditions_pass_rate'] !== undefined && employee['conditions_pass_rate'] < 100) {
            const passRate = parseFloat(employee['conditions_pass_rate'] || 0).toFixed(1);
            const passed = employee['conditions_passed'] || 0;
            const applicable = employee['conditions_applicable'] || 0;
            if (reasons.length === 0 && passRate < 100) {
                reasons.push(`조건 통과율 부족: $null/$null ($null%)`);
            }
        }

        // 사유가 없는 경우 기본 메시지
        if (reasons.length === 0) {
            if (employee[dashboardMonth + '_incentive'] === 0) {
                reasons.push('조건 정보를 확인할 수 없습니다');
            }
        }

        return reasons;
    }

    // 인센티브 상세 모달 (전역 스코프)
    window.showIncentiveModal = function(nodeId) {
        console.log('🔍 모달 함수 호출됨 - Node ID:', nodeId);

        try {
            // 기존 모달이 있으면 강제 닫기
            window.forceCloseModal();

            const employee = employeeData.find(emp => emp.emp_no === nodeId);
            if (!employee) {
                console.error('❌ 직원 데이터를 찾을 수 없음:', nodeId);
                alert('직원 데이터를 찾을 수 없습니다. ID: ' + nodeId);
                return;
            }
            console.log('✅ 직원 발견:', employee.name, employee.position);

            const position = (employee.position || '').toUpperCase();
            const employeeIncentive = Number(employee[dashboardMonth + '_incentive'] || 0);

            // 부하 직원 찾기 (TYPE-1만)
            const subordinates = employeeData.filter(emp => emp.boss_id === nodeId && emp.type === 'TYPE-1');
            const receivingSubordinates = subordinates.filter(sub => {
                const incentive = sub[dashboardMonth + '_incentive'] || 0;
                return Number(incentive) > 0;
            });

            // 계산 과정 상세 내용 생성
            let calculationDetails = '';

            if (position.includes('LINE LEADER')) {
            // LINE LEADER 계산 상세 - 부하직원 합계 × 12% × 수령율
            const assemblyInspectors = subordinates.filter(sub =>
                sub.position && sub.position.toUpperCase().includes('ASSEMBLY INSPECTOR')
            );
            const totalSubIncentive = assemblyInspectors.reduce((sum, sub) => {
                return sum + Number(sub[dashboardMonth + '_incentive'] || 0);
            }, 0);
            const receivingInspectors = assemblyInspectors.filter(ai =>
                Number(ai[dashboardMonth + '_incentive'] || 0) > 0
            );
            const receivingRatio = assemblyInspectors.length > 0 ? receivingInspectors.length / assemblyInspectors.length : 0;
            const expectedIncentive = Math.round(totalSubIncentive * 0.12 * receivingRatio);

            // ASSEMBLY INSPECTOR 상세 내역 생성
            let inspectorDetails = '';
            if (assemblyInspectors.length > 0) {
                inspectorDetails = `
                    <div class="mt-3">
                        <h6>📋 ASSEMBLY INSPECTOR 인센티브 내역 (합계 계산 대상)</h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>이름</th>
                                    <th>ID</th>
                                    <th class="text-end">인센티브</th>
                                    <th class="text-center">수령 여부</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${assemblyInspectors.map(ai => {
                                    const aiIncentive = Number(ai[dashboardMonth + '_incentive'] || 0);
                                    const isReceiving = aiIncentive > 0;
                                    return `
                                        <tr class="${isReceiving ? '' : 'text-muted'}">
                                            <td>${ai.name || ai.employee_name || 'Unknown'}</td>
                                            <td>${ai.emp_no || ai.employee_id || ''}</td>
                                            <td class="text-end">₫${aiIncentive.toLocaleString('ko-KR')}</td>
                                            <td class="text-center">${isReceiving ? '✅' : '❌'}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="2">합계</th>
                                    <th class="text-end">₫${totalSubIncentive.toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="2">평균 (수령자 ${receivingInspectors.length}명 / 전체 ${assemblyInspectors.length}명)</th>
                                    <th class="text-end">₫${receivingInspectors.length > 0 ? Math.round(totalSubIncentive / receivingInspectors.length).toLocaleString('ko-KR') : '0'}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }

            calculationDetails = `
                <div class="calculation-details">
                    <h6>📊 계산 과정 상세 (LINE LEADER)</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>계산 공식:</td>
                            <td class="text-end"><strong>부하직원 합계 × 12% × 수령율</strong></td>
                        </tr>
                        <tr>
                            <td>ASSEMBLY INSPECTOR 수:</td>
                            <td class="text-end">${assemblyInspectors.length}명 (수령: ${receivingInspectors.length}명)</td>
                        </tr>
                        <tr>
                            <td>인센티브 합계:</td>
                            <td class="text-end">₫${totalSubIncentive.toLocaleString('ko-KR')}</td>
                        </tr>
                        <tr>
                            <td>수령 비율:</td>
                            <td class="text-end">${receivingInspectors.length}/${assemblyInspectors.length} = ${(receivingRatio * 100).toFixed(1)}%</td>
                        </tr>
                        <tr>
                            <td>계산식:</td>
                            <td class="text-end">₫${totalSubIncentive.toLocaleString('ko-KR')} × 12% × ${(receivingRatio * 100).toFixed(1)}%</td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>${getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${expectedIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                        <tr class="${Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}">
                            <td><strong>${getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${employeeIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                    </table>
                    $null
                </div>
            `;
            } else if (position.includes('GROUP LEADER')) {
            // GROUP LEADER 계산 상세 - 팀 내 LINE LEADER 평균 × 2
            const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
            const receivingLineLeaders = teamLineLeaders.filter(ll =>
                Number(ll[dashboardMonth + '_incentive'] || 0) > 0
            );
            const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
            const expectedIncentive = Math.round(avgLineLeaderIncentive * 2);

            // LINE LEADER별 상세 내역 생성
            let lineLeaderDetails = '';
            if (teamLineLeaders.length > 0) {
                lineLeaderDetails = `
                    <div class="mt-3">
                        <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>이름</th>
                                    <th>ID</th>
                                    <th class="text-end">인센티브</th>
                                    <th class="text-center">평균 계산 포함</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${teamLineLeaders.map(ll => {
                                    const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                    const included = llIncentive > 0;
                                    return `
                                        <tr class="${included ? '' : 'text-muted'}">
                                            <td>${ll.name}</td>
                                            <td>${ll.emp_no}</td>
                                            <td class="text-end">${included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}</td>
                                            <td class="text-center">${included ? '✅' : '❌'}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="2">합계</th>
                                    <th class="text-end">₫${receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="2">평균 (수령자 ${receivingLineLeaders.length}명 / 전체 ${teamLineLeaders.length}명)</th>
                                    <th class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }

            calculationDetails = `
                <div class="calculation-details">
                    <h6>📊 계산 과정 상세 (GROUP LEADER)</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>계산 공식:</td>
                            <td class="text-end"><strong>LINE LEADER 평균 × 2</strong></td>
                        </tr>
                        <tr>
                            <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                            <td class="text-end">${teamLineLeaders.length}명 (수령: ${receivingLineLeaders.length}명)</td>
                        </tr>
                        <tr>
                            <td>LINE LEADER 평균 인센티브:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</td>
                        </tr>
                        <tr>
                            <td>계산식:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')} × 2</td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>${getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${expectedIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                        <tr class="${Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}">
                            <td><strong>${getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${employeeIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                    </table>
                    $null
                </div>
            `;
            } else if (position.includes('SUPERVISOR')) {
            // SUPERVISOR 계산 상세 - 팀 내 LINE LEADER만
            const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
            const receivingLineLeaders = teamLineLeaders.filter(ll =>
                Number(ll[dashboardMonth + '_incentive'] || 0) > 0
            );
            const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
            const expectedIncentive = Math.round(avgLineLeaderIncentive * 2.5);

            // 팀 내 LINE LEADER 상세 내역 생성
            let allLineLeaderDetails = '';
            if (teamLineLeaders.length > 0) {
                // LINE LEADER를 GROUP별로 그룹화
                const lineLeadersByGroup = {};
                teamLineLeaders.forEach(ll => {
                    const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                    const groupName = groupLeader ? groupLeader.name : 'Unknown';
                    if (!lineLeadersByGroup[groupName]) {
                        lineLeadersByGroup[groupName] = [];
                    }
                    lineLeadersByGroup[groupName].push(ll);
                });

                allLineLeaderDetails = `
                    <div class="mt-3">
                        <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>GROUP</th>
                                    <th>LINE LEADER</th>
                                    <th>ID</th>
                                    <th class="text-end">인센티브</th>
                                    <th class="text-center">평균 계산 포함</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {
                                    return leaders.map((ll, idx) => {
                                        const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                        const included = llIncentive > 0;
                                        return `
                                            <tr class="${included ? '' : 'text-muted'}">
                                                ${idx === 0 ? `<td rowspan="${leaders.length}">$null</td>` : ''}
                                                <td>${ll.name}</td>
                                                <td>${ll.emp_no}</td>
                                                <td class="text-end">${included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}</td>
                                                <td class="text-center">${included ? '✅' : '❌'}</td>
                                            </tr>
                                        `;
                                    }).join('');
                                }).join('')}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="3">합계</th>
                                    <th class="text-end">₫${receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="3">평균 (수령자 ${receivingLineLeaders.length}명 / 전체 ${teamLineLeaders.length}명)</th>
                                    <th class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }

            calculationDetails = `
                <div class="calculation-details">
                    <h6>📊 계산 과정 상세 (SUPERVISOR)</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>계산 공식:</td>
                            <td class="text-end"><strong>LINE LEADER 평균 × 2.5</strong></td>
                        </tr>
                        <tr>
                            <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                            <td class="text-end">${teamLineLeaders.length}명 (수령: ${receivingLineLeaders.length}명)</td>
                        </tr>
                        <tr>
                            <td>LINE LEADER 평균 인센티브:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</td>
                        </tr>
                        <tr>
                            <td>계산식:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')} × 2.5</td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>${getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${expectedIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                        <tr class="${Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}">
                            <td><strong>${getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${employeeIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                    </table>
                    $null
                </div>
            `;
            } else if (position.includes('A.MANAGER') || position.includes('ASSISTANT')) {
            // A.MANAGER 계산 상세 - 팀 내 LINE LEADER 평균 × 3
            let teamLineLeaders = [];
            let receivingLineLeaders = [];
            let avgLineLeaderIncentive = 0;
            let expectedIncentive = 0;

            // 에러 핸들링을 추가한 팀 LINE LEADER 찾기
            try {
                teamLineLeaders = findTeamLineLeaders(employee.emp_no);
                receivingLineLeaders = teamLineLeaders.filter(ll =>
                    Number(ll[dashboardMonth + '_incentive'] || 0) > 0
                );
                avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                    receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
                expectedIncentive = Math.round(avgLineLeaderIncentive * 3);
            } catch (err) {
                console.error('❌ A.MANAGER 계산 중 오류:', err);
                teamLineLeaders = [];
                receivingLineLeaders = [];
            }

            // LINE LEADER 인센티브 합계 계산
            const lineLeaderTotal = receivingLineLeaders.reduce((sum, ll) =>
                sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0);

            // 팀 내 LINE LEADER 상세 내역 생성
            let lineLeaderBreakdown = '';
            if (teamLineLeaders.length > 0) {
                // LINE LEADER를 GROUP별로 그룹화
                const lineLeadersByGroup = {};
                teamLineLeaders.forEach(ll => {
                    const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                    const groupName = groupLeader ? groupLeader.name : 'Unknown';
                    if (!lineLeadersByGroup[groupName]) {
                        lineLeadersByGroup[groupName] = [];
                    }
                    lineLeadersByGroup[groupName].push(ll);
                });

                lineLeaderBreakdown = `
                    <div class="mt-3">
                        <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>GROUP LEADER</th>
                                    <th>LINE LEADER</th>
                                    <th>ID</th>
                                    <th class="text-end">인센티브</th>
                                    <th class="text-center">평균 계산 포함</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {
                                    return leaders.map((ll, idx) => {
                                        const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                        const included = llIncentive > 0;
                                        return `
                                            <tr class="${included ? '' : 'text-muted'}">
                                                ${idx === 0 ? `<td rowspan="${leaders.length}">$null</td>` : ''}
                                                <td>${ll.name || ll.employee_name || 'Unknown'}</td>
                                                <td>${ll.emp_no || ll.employee_id || ''}</td>
                                                <td class="text-end">₫${llIncentive.toLocaleString('ko-KR')}</td>
                                                <td class="text-center">${included ? '✅' : '❌'}</td>
                                            </tr>
                                        `;
                                    }).join('');
                                }).join('')}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="3">합계</th>
                                    <th class="text-end">₫${lineLeaderTotal.toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="3">평균 (수령자 ${receivingLineLeaders.length}명 / 전체 ${teamLineLeaders.length}명)</th>
                                    <th class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }

            calculationDetails = `
                <div class="calculation-details">
                    <h6>📊 계산 과정 상세 (A.MANAGER)</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>계산 공식:</td>
                            <td class="text-end"><strong>LINE LEADER 평균 × 3</strong></td>
                        </tr>
                        <tr>
                            <td>LINE LEADER 수:</td>
                            <td class="text-end">${teamLineLeaders.length}명 (수령: ${receivingLineLeaders.length}명)</td>
                        </tr>
                        <tr>
                            <td>LINE LEADER 평균 인센티브:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</td>
                        </tr>
                        <tr>
                            <td>계산식:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')} × 3</td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>${getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${expectedIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                        <tr class="${Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}">
                            <td><strong>${getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${employeeIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                    </table>
                    $null
                </div>
            `;
            } else if (position.includes('MANAGER') && !position.includes('A.MANAGER') && !position.includes('ASSISTANT')) {
            // MANAGER 계산 상세 - 팀 내 LINE LEADER 평균 기준
            const teamLineLeaders = findTeamLineLeaders(employee.emp_no);
            const receivingLineLeaders = teamLineLeaders.filter(ll =>
                Number(ll[dashboardMonth + '_incentive'] || 0) > 0
            );
            const avgLineLeaderIncentive = receivingLineLeaders.length > 0 ?
                receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0) / receivingLineLeaders.length : 0;
            const expectedIncentive = Math.round(avgLineLeaderIncentive * 3.5);

            // 팀 내 LINE LEADER 상세 내역 생성
            let lineLeaderBreakdown = '';
            if (teamLineLeaders.length > 0) {
                // LINE LEADER를 GROUP별로 그룹화
                const lineLeadersByGroup = {};
                teamLineLeaders.forEach(ll => {
                    const groupLeader = employeeData.find(emp => emp.emp_no === ll.boss_id);
                    const groupName = groupLeader ? groupLeader.name : 'Unknown';
                    if (!lineLeadersByGroup[groupName]) {
                        lineLeadersByGroup[groupName] = [];
                    }
                    lineLeadersByGroup[groupName].push(ll);
                });

                lineLeaderBreakdown = `
                    <div class="mt-3">
                        <h6>📋 <span class="modal-team-line-leader-list">팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)</span></h6>
                        <table class="table table-sm table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>GROUP LEADER</th>
                                    <th>LINE LEADER</th>
                                    <th>ID</th>
                                    <th class="text-end">인센티브</th>
                                    <th class="text-center">평균 계산 포함</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(lineLeadersByGroup).map(([groupName, leaders]) => {
                                    return leaders.map((ll, idx) => {
                                        const llIncentive = Number(ll[dashboardMonth + '_incentive'] || 0);
                                        const included = llIncentive > 0;
                                        return `
                                            <tr class="${included ? '' : 'text-muted'}">
                                                ${idx === 0 ? `<td rowspan="${leaders.length}">$null</td>` : ''}
                                                <td>${ll.name}</td>
                                                <td>${ll.emp_no}</td>
                                                <td class="text-end">${included ? '₫' + llIncentive.toLocaleString('ko-KR') : '-'}</td>
                                                <td class="text-center">${included ? '✅' : '❌'}</td>
                                            </tr>
                                        `;
                                    }).join('');
                                }).join('')}
                            </tbody>
                            <tfoot class="table-secondary">
                                <tr>
                                    <th colspan="3">합계</th>
                                    <th class="text-end">₫${receivingLineLeaders.reduce((sum, ll) => sum + Number(ll[dashboardMonth + '_incentive'] || 0), 0).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                                <tr>
                                    <th colspan="3">평균 (수령자 ${receivingLineLeaders.length}명 / 전체 ${teamLineLeaders.length}명)</th>
                                    <th class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                `;
            }

            calculationDetails = `
                <div class="calculation-details">
                    <h6>📊 계산 과정 상세 (MANAGER)</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><span class="modal-team-line-leader-count">팀 내 LINE LEADER 수:</span></td>
                            <td class="text-end">${teamLineLeaders.length}명</td>
                        </tr>
                        <tr>
                            <td>인센티브 받은 LINE LEADER:</td>
                            <td class="text-end">${receivingLineLeaders.length}명</td>
                        </tr>
                        <tr>
                            <td>LINE LEADER 평균 인센티브:</td>
                            <td class="text-end">₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')}</td>
                        </tr>
                        <tr class="table-warning">
                            <td><strong>계산식:</strong></td>
                            <td class="text-end"><strong>₫${Math.round(avgLineLeaderIncentive).toLocaleString('ko-KR')} × 3.5</strong></td>
                        </tr>
                        <tr class="table-primary">
                            <td><strong>${getTranslation('modal.expectedIncentive', currentLanguage) || '예상 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${expectedIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                        <tr class="${Math.abs(employeeIncentive - expectedIncentive) < 1000 ? 'table-success' : 'table-warning'}">
                            <td><strong>${getTranslation('modal.actualIncentive', currentLanguage) || '실제 인센티브'}:</strong></td>
                            <td class="text-end"><strong>₫${employeeIncentive.toLocaleString('ko-KR')}</strong></td>
                        </tr>
                    </table>
                    $null
                </div>
            `;
            }

            // 모달 HTML 생성
            const monthNumber = dashboardMonth === 'september' ? '9' : dashboardMonth === 'august' ? '8' : dashboardMonth === 'july' ? '7' : '?';
            const modalHtml = `
            <div class="modal fade" id="incentiveModal" tabindex="-1" style="z-index: 1055;">
                <div class="modal-dialog modal-xl" style="z-index: 1056;">
                    <div class="modal-content" style="z-index: 1057; position: relative; user-select: text; -webkit-user-select: text; -moz-user-select: text; -ms-user-select: text;">
                        <div class="modal-header">
                            <h5 class="modal-title" id="modalTitle">${getTranslation('modal.modalTitle', currentLanguage)} - $null년 $null월</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="employee-info mb-3">
                                <h5>${employee.name}</h5>
                                <p class="mb-1"><strong>직급:</strong> ${employee.position}</p>
                                <p class="mb-1"><strong>ID:</strong> ${employee.emp_no}</p>
                                <p class="mb-1"><strong>Type:</strong> ${employee.type}</p>
                            </div>
                            <hr>
                            <div class="incentive-summary mb-3">
                                <h5 class="${employeeIncentive > 0 ? 'text-success' : 'text-danger'}">
                                    <span class="modal-actual-incentive">${getTranslation('orgChart.modalLabels.actualIncentive', currentLanguage)}</span>: ₫${employeeIncentive.toLocaleString('ko-KR')}
                                </h5>
                                <p class="text-muted"><span class="modal-calc-method">${getTranslation('orgChart.modalLabels.calculationMethod', currentLanguage)}</span>: ${getCalculationFormula(employee.position) || '특별 계산'}</p>
                                ${(() => {
                                    if (employeeIncentive === 0) {
                                        const failureReasons = getIncentiveFailureReasons(employee);
                                        if (failureReasons.length > 0) {
                                            return `
                                                <div class="alert alert-warning mt-3">
                                                    <h6 class="alert-heading">📋 <span class="modal-no-payment-reason">${getTranslation('orgChart.modalLabels.noPaymentReason', currentLanguage)}</span></h6>
                                                    <ul class="mb-0">
                                                        ${failureReasons.map(reason => `<li>$null</li>`).join('')}
                                                    </ul>
                                                </div>
                                            `;
                                        }
                                    }
                                    return '';
                                })()}
                            </div>
                            $null
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"><span class="modal-close-btn">${getTranslation('buttons.close', currentLanguage) || '닫기'}</span></button>
                        </div>
                    </div>
                </div>
            </div>
        `;

            // 기존 모달 제거 (인스턴스 포함)
            const existingModal = document.getElementById('incentiveModal');
            if (existingModal) {
                try {
                    // 기존 Bootstrap 모달 인스턴스 제거
                    const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
                    if (existingModalInstance) {
                        existingModalInstance.dispose();
                    }
                    existingModal.remove();
                } catch (e) {
                    console.error('기존 모달 제거 중 오류:', e);
                    existingModal.remove();
                }
            }

            // 모달 추가
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modalElement = document.getElementById('incentiveModal');

            // Bootstrap 모달 인스턴스 생성 및 표시
            try {
                // 모달을 보여주기 전에 tabindex 설정
                modalElement.setAttribute('tabindex', '-1');
                modalElement.setAttribute('aria-hidden', 'true');

                // 모달 컨텐츠에 텍스트 선택 가능하도록 설정
                const modalContent = modalElement.querySelector('.modal-content');
                if (modalContent) {
                    modalContent.style.userSelect = 'text';
                    modalContent.style.webkitUserSelect = 'text';
                    modalContent.style.mozUserSelect = 'text';
                    modalContent.style.msUserSelect = 'text';
                    modalContent.style.position = 'relative';
                    modalContent.style.zIndex = '1057';
                }

                const modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,      // 배경 클릭으로 닫기 가능
                    keyboard: true,      // ESC 키로 닫기 가능
                    focus: true
                });

                // 모달 표시
                modal.show();

                // 수동으로 백드롭 클릭 이벤트 추가 (Bootstrap이 제대로 처리 안 될 경우 대비)
                setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.style.cursor = 'pointer';
                    backdrop.style.zIndex = '1050';  // 모달보다 낮은 z-index
                    backdrop.addEventListener('click', function() {
                        console.log('백드롭 클릭 감지');
                        modal.hide();
                    });
                }

                // 모달 자체의 z-index 확인
                if (modalElement) {
                    modalElement.style.zIndex = '1055';
                    const modalDialog = modalElement.querySelector('.modal-dialog');
                    if (modalDialog) {
                        modalDialog.style.zIndex = '1056';
                    }
                }

                // ESC 키 이벤트도 수동 추가
                document.addEventListener('keydown', function escHandler(e) {
                    if (e.key === 'Escape') {
                        console.log('ESC 키 감지');
                        modal.hide();
                        document.removeEventListener('keydown', escHandler);
                    }
                });
                }, 100);

                // 모달이 완전히 닫힌 후 정리
                modalElement.addEventListener('hidden.bs.modal', function onHidden() {
                console.log('모달 완전히 닫힘 - 정리 작업 실행');

                // 이벤트 리스너 제거
                modalElement.removeEventListener('hidden.bs.modal', onHidden);

                try {
                    // 모달 인스턴스 정리
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.dispose();
                    }
                } catch (e) {
                    console.error('모달 dispose 오류:', e);
                }

                // 모달 DOM 요소 제거
                setTimeout(() => {
                    if (modalElement && modalElement.parentNode) {
                        modalElement.parentNode.removeChild(modalElement);
                    }
                    // 백드롭이 남아있다면 제거
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                    // body 상태 초기화
                    document.body.classList.remove('modal-open');
                    document.body.style.removeProperty('overflow');
                    document.body.style.removeProperty('padding-right');
                    // 추가로 body의 padding도 제거
                    document.body.style.paddingRight = '';
                    document.body.style.overflow = '';
                }, 300);  // Bootstrap 애니메이션이 완료될 때까지 대기
                });

                // 모달이 표시된 후 포커스 설정
                modalElement.addEventListener('shown.bs.modal', function() {
                console.log('모달 표시 완료');
                // 닫기 버튼에 포커스 설정
                const closeBtn = modalElement.querySelector('[data-bs-dismiss="modal"]');
                if (closeBtn) {
                        closeBtn.focus();
                    }
                });

            } catch (error) {
                console.error('모달 생성 오류:', error);
                // 오류 발생 시 정리 작업
                if (modalElement) {
                    modalElement.remove();
                }
                // 백드롭도 제거
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
                // body 상태 초기화
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
                document.body.style.paddingRight = '';
                document.body.style.overflow = '';
            }
        } catch (mainError) {
            console.error('showIncentiveModal 메인 오류:', mainError);
            alert('모달을 표시하는 중 오류가 발생했습니다.');
        }
    }

    // 계산 공식 가져오기
    function getCalculationFormula(position) {
        const pos = (position || '').toUpperCase();

        if (pos.includes('LINE LEADER')) {
            return getTranslation('orgChart.calculationFormulas.lineLeader');
        } else if (pos.includes('GROUP LEADER')) {
            return getTranslation('orgChart.calculationFormulas.groupLeader');
        } else if (pos.includes('SUPERVISOR')) {
            return getTranslation('orgChart.calculationFormulas.supervisor');
        } else if (pos.includes('A.MANAGER') || pos.includes('ASSISTANT')) {
            return getTranslation('orgChart.calculationFormulas.assistantManager');
        } else if (pos.includes('MANAGER')) {
            return getTranslation('orgChart.calculationFormulas.manager');
        }
        return '';
    }

    // UI 텍스트 업데이트
    function updateOrgChartUIText() {
        // 제목 및 설명 업데이트
        const titleEl = document.getElementById('orgChartTitle');
        if (titleEl) titleEl.textContent = getTranslation('tabs.orgChart', currentLanguage) || getTranslation('tabs.orgchart', currentLanguage);

        const subtitleEl = document.getElementById('orgChartSubtitle');
        if (subtitleEl) subtitleEl.textContent = getTranslation('orgChart.subtitle', currentLanguage);

        // 메인 제목 업데이트
        const titleMainEl = document.getElementById('orgChartTitleMain');
        if (titleMainEl) titleMainEl.textContent = getTranslation('orgChart.title', currentLanguage);

        const subtitleMainEl = document.getElementById('orgChartSubtitleMain');
        if (subtitleMainEl) subtitleMainEl.textContent = getTranslation('orgChart.subtitle', currentLanguage);

        // 참고 레이블 및 제외된 직급 안내
        const noteLabelEl = document.getElementById('orgChartNoteLabel');
        if (noteLabelEl) noteLabelEl.textContent = getTranslation('orgChart.noteLabel', currentLanguage);

        const excludedEl = document.getElementById('orgChartExcludedPositions');
        if (excludedEl) excludedEl.textContent = getTranslation('orgChart.excludedPositions', currentLanguage);

        // 빵 부스러기 (전체 조직)
        const breadcrumbEl = document.getElementById('orgBreadcrumbText');
        if (breadcrumbEl) breadcrumbEl.textContent = getTranslation('orgChart.entireOrganization', currentLanguage);

        // 검색 placeholder
        const searchEl = document.getElementById('orgSearchInput');
        if (searchEl) searchEl.placeholder = getTranslation('orgChart.searchPlaceholder', currentLanguage);

        // 버튼 텍스트
        const expandEl = document.getElementById('expandAllText');
        if (expandEl) expandEl.textContent = getTranslation('orgChart.expandAll', currentLanguage);

        const collapseEl = document.getElementById('collapseAllText');
        if (collapseEl) collapseEl.textContent = getTranslation('orgChart.collapseAll', currentLanguage);

        // 범례
        const legendTitleEl = document.getElementById('legendTitle');
        if (legendTitleEl) legendTitleEl.textContent = getTranslation('orgChart.legendTitle', currentLanguage);

        const legendReceivedEl = document.getElementById('legendIncentiveReceived');
        if (legendReceivedEl) legendReceivedEl.textContent = getTranslation('orgChart.incentiveReceived', currentLanguage);

        const legendNoIncentiveEl = document.getElementById('legendNoIncentive');
        if (legendNoIncentiveEl) legendNoIncentiveEl.textContent = getTranslation('orgChart.noIncentive', currentLanguage);
    }

    // 조직도 초기화 함수
    function resetOrgChart() {
        drawCollapsibleOrgChart();
    }

    // 이전 drawCollapsibleTree 함수는 제거
    function drawCollapsibleTree() {
        console.log('This function is deprecated. Using drawCollapsibleOrgChart instead.');
        drawCollapsibleOrgChart();
        const containerWidth = container.node().getBoundingClientRect().width;
        const width = Math.max(1200, containerWidth);
        const height = 800;
        const margin = { top: 20, right: 120, bottom: 20, left: 200 };

        // SVG 초기화
        d3.select("#orgChartSvg").selectAll("*").remove();

        const svg = d3.select("#orgChartSvg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${height / 2})`);

        const tree = d3.tree()
            .size([height - margin.top - margin.bottom, width - margin.left - margin.right - 200]);

        const hierarchyData = prepareHierarchyData();
        if (!hierarchyData || hierarchyData.length === 0) {
            console.log('No hierarchy data available');
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .text("조직도 데이터를 불러올 수 없습니다.");
            return;
        }

        try {
            const root = d3.stratify()
                .id(d => d.id)
                .parentId(d => d.parentId)(hierarchyData);

            root.x0 = (height - margin.top - margin.bottom) / 2;
            root.y0 = 0;

            // 초기에 2레벨까지만 펼치기
            root.descendants().forEach((d, i) => {
                d.id = i;
                d._children = d.children;
                if (d.depth && d.depth > 1) {
                    d.children = null;
                }
            });

            function update(source) {
                const treeData = tree(root);
                const nodes = treeData.descendants();
                const links = treeData.descendants().slice(1);

                // 노드 위치 조정
                nodes.forEach(d => { d.y = d.depth * 180; });

                // 노드 업데이트
                const node = g.selectAll("g.node")
                    .data(nodes, d => d.id || (d.id = ++i));

                // 새 노드 추가
                const nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${source.y0},${source.x0})`)
                    .on("click", click);

                nodeEnter.append("circle")
                    .attr("class", "node")
                    .attr("r", 1e-6)
                    .style("fill", d => d._children ? "lightsteelblue" : "#ff")
                    .style("stroke", d => getPositionColor(d.data.position))
                    .style("stroke-width", "2px");

                nodeEnter.append("text")
                    .attr("dy", ".35em")
                    .attr("x", d => d.children || d._children ? -13 : 13)
                    .attr("text-anchor", d => d.children || d._children ? "end" : "start")
                    .style("font-size", "12px")
                    .text(d => d.data.name);

                // 노드 위치 업데이트
                const nodeUpdate = nodeEnter.merge(node);

                nodeUpdate.transition()
                    .duration(750)
                    .attr("transform", d => `translate(${d.y},${d.x})`);

                nodeUpdate.select("circle.node")
                    .attr("r", 10)
                    .style("fill", d => d._children ? "lightsteelblue" : "#ff")
                    .attr("cursor", "pointer");

                // 노드 제거
                const nodeExit = node.exit().transition()
                    .duration(750)
                    .attr("transform", d => `translate(${source.y},${source.x})`)
                    .remove();

                nodeExit.select("circle")
                    .attr("r", 1e-6);

                nodeExit.select("text")
                    .style("fill-opacity", 1e-6);

                // 링크 업데이트
                const link = g.selectAll("path.link")
                    .data(links, d => d.id);

                const linkEnter = link.enter().insert("path", "g")
                    .attr("class", "link")
                    .style("fill", "none")
                    .style("stroke", "#ccc")
                    .style("stroke-width", "2px")
                    .attr("d", d => {
                        const o = { x: source.x0, y: source.y0 };
                        return diagonal(o, o);
                    });

                const linkUpdate = linkEnter.merge(link);

                linkUpdate.transition()
                    .duration(750)
                    .attr("d", d => diagonal(d, d.parent));

                const linkExit = link.exit().transition()
                    .duration(750)
                    .attr("d", d => {
                        const o = { x: source.x, y: source.y };
                        return diagonal(o, o);
                    })
                    .remove();

                // 이전 위치 저장
                nodes.forEach(d => {
                    d.x0 = d.x;
                    d.y0 = d.y;
                });

                // 대각선 링크 생성 함수
                function diagonal(s, d) {
                    const path = `M ${s.y} ${s.x}
                            C ${(s.y + d.y) / 2} ${s.x},
                              ${(s.y + d.y) / 2} ${d.x},
                              ${d.y} ${d.x}`;
                    return path;
                }

                // 클릭 이벤트 핸들러
                function click(event, d) {
                    if (d.children) {
                        d._children = d.children;
                        d.children = null;
                    } else {
                        d.children = d._children;
                        d._children = null;
                    }
                    update(d);
                }
            }

            var i = 0;
            update(root);

            // Breadcrumb 업데이트
            updateBreadcrumb("접을 수 있는 트리");

            // 범례 추가
            const legend = svg.append("g")
                .attr("class", "legend")
                .attr("transform", `translate(${width - 200}, 20)`);

            const legendItems = [
                { color: "#1f77b4", label: "Manager" },
                { color: "#2ca02c", label: "Supervisor" },
                { color: "#ff7f0e", label: "Group Leader" },
                { color: "#d62728", label: "Line Leader" },
                { color: "#9467bd", label: "Inspector" },
                { color: "#8c564b", label: "Others" }
            ];

            legendItems.forEach((item, i) => {
                const legendItem = legend.append("g")
                    .attr("transform", `translate(0, ${i * 20})`);

                legendItem.append("circle")
                    .attr("r", 6)
                    .style("fill", "white")
                    .style("stroke", item.color)
                    .style("stroke-width", "2px");

                legendItem.append("text")
                    .attr("x", 15)
                    .attr("y", 5)
                    .style("font-size", "12px")
                    .text(item.label);
            });

        } catch (error) {
            console.error("조직도 생성 오류:", error);
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
        }
    }

    function drawRadialTree() {
        const container = d3.select("#orgChartContainer");
        const containerWidth = container.node().getBoundingClientRect().width;
        const radius = Math.min(containerWidth, 1200) / 2; // 더 큰 반경
        const width = radius * 2;
        const height = radius * 2;

        const svg = d3.select("#orgChartSvg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2},${height / 2})`);

        const tree = d3.tree()
            .size([2 * Math.PI, radius - 150]) // 더 큰 반경
            .separation((a, b) => {
                // 레벨별로 다른 간격 적용
                if (a.depth <= 2) return 2;
                if (a.depth === 3) return 1.5;
                if (a.depth >= 4) return 1.2;
                return (a.parent == b.parent ? 1 : 2) / a.depth;
            });

        const hierarchyData = prepareHierarchyData();
        if (!hierarchyData || hierarchyData.length === 0) {
            console.log('No hierarchy data available');
            return;
        }

        try {
            const root = d3.stratify()
                .id(d => d.id)
                .parentId(d => d.parentId)(hierarchyData);

            tree(root);

            // 링크 그리기
            const link = g.selectAll(".link")
                .data(root.links())
                .enter().append("path")
                .attr("class", "link")
                .style("fill", "none")
                .style("stroke", "#ccc")
                .style("stroke-width", d => Math.max(1, 3 - d.target.depth)) // 깊이에 따라 두께 조정
                .style("opacity", d => Math.max(0.3, 1 - d.target.depth * 0.15)) // 깊이에 따라 투명도
                .attr("d", d3.linkRadial()
                    .angle(d => d.x)
                    .radius(d => d.y));

            // 노드 그리기
            const node = g.selectAll(".node")
                .data(root.descendants())
                .enter().append("g")
                .attr("class", d => "node" + (d.children ? " node--internal" : " node--lea"))
                .attr("transform", d => `
                    rotate(${(d.x * 180 / Math.PI - 90)})
                    translate(${d.y},0)
                `);

            // 노드 원 (크기를 깊이에 따라 조정, 인센티브 여부에 따라 색상)
            node.append("circle")
                .attr("r", d => Math.max(4, 8 - d.depth)) // 깊이에 따라 크기 조정
                .style("fill", d => {
                    const baseColor = getPositionColor(d.data.position);
                    // 인센티브 여부에 따라 채우기 색상
                    if (hasIncentive(d.data)) {
                        return d.children ? "#ff" : baseColor + "30";
                    } else {
                        return "#ffcccc"; // 연한 빨간색
                    }
                })
                .style("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                .style("stroke-width", d => Math.max(2, 4 - d.depth * 0.5))
                .style("cursor", "pointer")
                .on("mouseover", function(event, d) {
                    // 툴팁 표시
                    const tooltip = d3.select("body").append("div")
                        .attr("class", "radial-tooltip")
                        .style("position", "absolute")
                        .style("padding", "10px")
                        .style("background", "rgba(0, 0, 0, 0.8)")
                        .style("color", "white")
                        .style("border-radius", "5px")
                        .style("pointer-events", "none")
                        .style("opacity", 0);

                    tooltip.transition()
                        .duration(200)
                        .style("opacity", 0.9);

                    tooltip.html(`
                        <strong>${d.data.name}</strong><br/>
                        ID: ${d.data.id}<br/>
                        ${d.data.position}<br/>
                        타입: ${d.data.type || 'N/A'}<br/>
                        인센티브: ${hasIncentive(d.data) ? '수령' : '미수령'}
                    `)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", function() {
                    d3.selectAll(".radial-tooltip").remove();
                });

            // 텍스트 라벨 (깊이에 따라 크기와 표시 조정)
            node.append("text")
                .attr("dy", "0.31em")
                .attr("x", d => d.x < Math.PI === !d.children ? 10 : -10) // 더 큰 간격
                .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
                .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
                .style("font-size", d => {
                    // 깊이에 따라 폰트 크기 조정
                    if (d.depth === 0) return "16px";
                    if (d.depth === 1) return "14px";
                    if (d.depth === 2) return "12px";
                    if (d.depth === 3) return "11px";
                    return "10px";
                })
                .style("font-weight", d => d.depth <= 1 ? "bold" : "normal")
                .text(d => {
                    // 깊이가 깊을수록 텍스트 줄이기
                    if (d.depth >= 4) {
                        // Inspector 레벨에서는 이름만 표시하고 줄임
                        const names = d.data.name.split(' ');
                        return names[names.length - 1]; // 성만 표시
                    }
                    return d.data.name;
                });

            // 깊이가 얕은 노드에 대해 포지션 텍스트 추가
            node.filter(d => d.depth < 3)
                .append("text")
                .attr("dy", "1.5em")
                .attr("x", d => d.x < Math.PI === !d.children ? 10 : -10)
                .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
                .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
                .style("font-size", "9px")
                .style("fill", "#666")
                .text(d => d.data.position);

            // 줌 기능 추가 (개선된 초기 줌)
            const zoom = d3.zoom()
                .scaleExtent([0.3, 4])
                .on("zoom", (event) => {
                    g.attr("transform", `translate(${width / 2},${height / 2}) scale(${event.transform.k})`);
                });

            svg.call(zoom);

            // 초기 줌을 전체가 잘 보이도록 설정
            svg.call(zoom.transform, d3.zoomIdentity.scale(0.8));

            // Breadcrumb 업데이트
            updateBreadcrumb("방사형 트리");

        } catch (error) {
            console.error("방사형 조직도 생성 오류:", error);
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
        }
    }

    // Old D3.js visualization functions - replaced with collapsible tree
    function drawHorizontalTree() {
        console.log('Horizontal tree deprecated - using collapsible tree');
        return;

        const container = d3.select("#orgChartContainer");
        const containerWidth = container.node().getBoundingClientRect().width;
        const width = Math.max(2000, containerWidth); // 더 넓게
        const height = 3000; // 더 높게
        const margin = { top: 50, right: 300, bottom: 50, left: 150 };
        const duration = 750; // 애니메이션 지속 시간

        const svg = d3.select("#orgChartSvg")
            .style("display", "block")  // SVG 다시 표시
            .attr("width", width)
            .attr("height", height);

        svg.selectAll("*").remove(); // 기존 내용 제거

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // nodeSize를 사용하여 고정된 노드 간격 설정
        const treeLayout = d3.tree()
            .nodeSize([50, 200]) // [수직 간격, 수평 간격] 늘림
            .separation((a, b) => {
                // 같은 부모를 가진 노드들 사이의 간격
                if (a.parent === b.parent) {
                    // Inspector 레벨에서는 더 넓은 간격
                    if (a.data.position && a.data.position.includes('INSPECTOR')) {
                        return 2;
                    }
                    return 1.2;
                }
                return 1.5;
            });

        const hierarchyData = prepareHierarchyData();
        if (!hierarchyData || hierarchyData.length === 0) {
            console.log('No hierarchy data available');
            return;
        }

        try {
            const root = d3.stratify()
                .id(d => d.id)
                .parentId(d => d.parentId)(hierarchyData);

            // 초기 위치 설정
            root.x0 = height / 2;
            root.y0 = 0;

            // 처음에는 1단계 깊이까지만 열어둠
            root.descendants().forEach((d, i) => {
                d.id = i; // 고유 ID 할당
                if (d.depth > 1) {
                    d._children = d.children;
                    d.children = null;
                }
            });

            // 업데이트 함수 정의
            function update(source) {
                // 트리 레이아웃 계산
                const treeData = treeLayout(root);
                const nodes = treeData.descendants();
                const links = treeData.links();

                // 노드 위치 조정 (중앙 정렬)
                const minY = Math.min(...nodes.map(d => d.x));
                const maxY = Math.max(...nodes.map(d => d.x));
                const centerY = (height - margin.top - margin.bottom) / 2;
                const offsetY = centerY - (maxY + minY) / 2;

                nodes.forEach(d => {
                    d.x += offsetY;
                });

                // 노드 업데이트
                const node = g.selectAll("g.node")
                    .data(nodes, d => d.id || (d.id = ++i));

                // 새로운 노드 추가
                const nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${source.y0},${source.x0})`)
                    .style("cursor", d => d._children || d.children ? "pointer" : "default")
                    .on("click", (event, d) => {
                        if (d.children) {
                            d._children = d.children;
                            d.children = null;
                        } else if (d._children) {
                            d.children = d._children;
                            d._children = null;
                        }
                        update(d);
                    });

                // 노드 박스 및 내용 추가
                let boxWidth = 140;
                let boxHeight = 45;
                let fontSize = 11;
                let positionFontSize = 9;

                // 깊이에 따라 크기 조정
                if (d.data.depth === 0) {
                    boxWidth = 160;
                    boxHeight = 50;
                    fontSize = 13;
                    positionFontSize = 10;
                } else if (d.data.depth === 1) {
                    boxWidth = 150;
                    boxHeight = 48;
                    fontSize = 12;
                    positionFontSize = 10;
                } else if (d.data.depth >= 4) {
                    boxWidth = 100;
                    boxHeight = 35;
                    fontSize = 9;
                    positionFontSize = 8;
                }

                // 배경 사각형
                nodeEnter.append("rect")
                    .attr("x", -boxWidth / 2)
                    .attr("y", -boxHeight / 2)
                    .attr("width", boxWidth)
                    .attr("height", boxHeight)
                    .attr("rx", 5)
                    .style("fill", () => {
                        const color = getPositionColor(d.data.position);
                        return hasIncentive(d.data) ? color + "30" : color + "10";
                    })
                    .style("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                    .style("stroke-width", "2px");

                // 접기/펼치기 심볼
                nodeEnter.append("circle")
                    .attr("class", "expand-symbol")
                    .attr("r", 8)
                    .attr("cx", boxWidth / 2 + 10)
                    .attr("cy", 0)
                    .style("fill", d => d._children ? "#ff7f0e" : "#2ca02c")
                    .style("stroke", "#333")
                    .style("stroke-width", "1.5px")
                    .style("display", d => d._children || d.children ? "block" : "none");

                nodeEnter.append("text")
                    .attr("class", "expand-text")
                    .attr("x", boxWidth / 2 + 10)
                    .attr("dy", "0.35em")
                    .attr("text-anchor", "middle")
                    .style("font-size", "12px")
                    .style("font-weight", "bold")
                    .style("fill", "white")
                    .style("pointer-events", "none")
                    .style("display", d => d._children || d.children ? "block" : "none")
                    .text(d => d._children ? "+" : "−");

                // 텍스트 추가
                const nameText = d => d.data.depth >= 4 ?
                    d.data.name.split(' ').slice(-1)[0] :
                    d.data.name;

                // 포지션
                nodeEnter.append("text")
                    .attr("class", "position-text")
                    .attr("dy", "-0.7em")
                    .attr("text-anchor", "middle")
                    .style("font-size", positionFontSize + "px")
                    .style("fill", "#333")
                    .style("font-weight", "bold")
                    .text(d => d.data.depth < 4 ? d.data.position : "");

                // 이름
                nodeEnter.append("text")
                    .attr("class", "name-text")
                    .attr("dy", d => d.data.depth < 4 ? "0.3em" : "0em")
                    .attr("text-anchor", "middle")
                    .style("font-size", fontSize + "px")
                    .style("font-weight", d => d.data.depth <= 1 ? "bold" : "normal")
                    .text(nameText);

                // ID
                nodeEnter.append("text")
                    .attr("class", "id-text")
                    .attr("dy", "1.4em")
                    .attr("text-anchor", "middle")
                    .style("font-size", (positionFontSize - 1) + "px")
                    .style("fill", "#666")
                    .text(d => d.data.depth < 4 && boxWidth >= 140 ? `ID: ${d.data.id}` : "");

                // 노드 위치 업데이트 (애니메이션)
                const nodeUpdate = nodeEnter.merge(node);

                nodeUpdate.transition()
                    .duration(duration)
                    .attr("transform", d => `translate(${d.y},${d.x})`);

                // 종료 노드 처리
                const nodeExit = node.exit().transition()
                    .duration(duration)
                    .attr("transform", d => `translate(${source.y},${source.x})`)
                    .remove();

                nodeExit.select("rect")
                    .style("opacity", 0);

                nodeExit.selectAll("text")
                    .style("opacity", 0);

                // 링크 업데이트
                const link = g.selectAll("path.link")
                    .data(links, d => d.target.id);

                // 새로운 링크 추가
                const linkEnter = link.enter().insert("path", "g")
                    .attr("class", "link")
                    .style("fill", "none")
                    .style("stroke", "#ccc")
                    .style("stroke-width", 2)
                    .style("opacity", 0.7)
                    .attr("d", d => {
                        const o = {x: source.x0, y: source.y0};
                        return diagonal(o, o);
                    });

                // 링크 위치 업데이트
                const linkUpdate = linkEnter.merge(link);

                linkUpdate.transition()
                    .duration(duration)
                    .attr("d", d => diagonal(d.source, d.target));

                // 종료 링크 처리
                const linkExit = link.exit().transition()
                    .duration(duration)
                    .attr("d", d => {
                        const o = {x: source.x, y: source.y};
                        return diagonal(o, o);
                    })
                    .remove();

                // 이전 위치 저장
                nodes.forEach(d => {
                    d.x0 = d.x;
                    d.y0 = d.y;
                });

                // 대각선 경로 생성 함수
                function diagonal(s, d) {
                    return `M ${s.y} ${s.x}
                            C ${(s.y + d.y) / 2} ${s.x},
                              ${(s.y + d.y) / 2} ${d.x},
                              ${d.y} ${d.x}`;
                }
            }

            // 초기 렌더링
            update(root);

            // 줌 기능 추가
            currentZoomBehavior = d3.zoom()
                .scaleExtent([0.2, 3])
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });

            svg.call(currentZoomBehavior);

            // 초기 줌 설정 (전체가 보이도록)
            setTimeout(() => {
                const bounds = g.node().getBBox();
                const fullWidth = width - margin.left - margin.right;
                const fullHeight = height - margin.top - margin.bottom;
                const midX = bounds.x + bounds.width / 2;
                const midY = bounds.y + bounds.height / 2;
                const scale = Math.min(fullWidth / bounds.width, fullHeight / bounds.height) * 0.8;

                svg.call(currentZoomBehavior.transform, d3.zoomIdentity
                    .translate(width / 2, height / 2)
                    .scale(scale)
                    .translate(-midX, -midY));
            }, 100);

            // Breadcrumb 업데이트
            updateBreadcrumb("수평 트리 (클릭하여 접기/펼치기)");

        } catch (error) {
            console.error("수평 조직도 생성 오류:", error);
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
        }
    }

    function drawTreemap() {
        console.log('Treemap deprecated - using collapsible tree');
        return;
        const containerWidth = container.node().getBoundingClientRect().width;
        const width = Math.max(1200, containerWidth);
        const height = 800;

        // 기존 SVG 숨기고 내용 제거
        d3.select("#orgChartSvg")
            .style("display", "none")
            .selectAll("*").remove();

        // 기존 treemap div 제거
        d3.select("#treemapDiv").remove();

        // treemap을 위한 컨테이너 div 생성
        const treemapDiv = d3.select("#orgChartContainer")
            .append("div")
            .attr("id", "treemapDiv")
            .style("width", width + "px")
            .style("height", height + "px")
            .style("position", "relative")
            .style("margin", "20px auto")
            .style("border", "1px solid #dee2e6")
            .style("border-radius", "8px")
            .style("overflow", "hidden")
            .style("background", "#f8f9fa");

        const hierarchyData = prepareHierarchyData();
        if (!hierarchyData || hierarchyData.length === 0) {
            console.log('No hierarchy data available for treemap');
            return;
        }

        try {
            // 계층 구조 생성
            const root = d3.stratify()
                .id(d => d.id)
                .parentId(d => d.parentId)(hierarchyData);

            // 각 노드의 value 계산 (자식이 없으면 1, 있으면 자식 수)
            root.sum(d => d.children ? 0 : 1)
                .sort((a, b) => b.value - a.value);

            // Treemap 레이아웃 생성
            d3.treemap()
                .size([width, height])
                .padding(2)
                .round(true)(root);

            // 색상 맵핑
            const colorScale = d3.scaleOrdinal()
                .domain(['MANAGER', 'SUPERVISOR', 'GROUP LEADER', 'LINE LEADER', 'INSPECTOR', 'Others'])
                .range(['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']);

            // 노드 생성
            const nodes = treemapDiv.selectAll(".treemap-node")
                .data(root.leaves())
                .enter().append("div")
                .attr("class", "treemap-node")
                .style("position", "absolute")
                .style("left", d => d.x0 + "px")
                .style("top", d => d.y0 + "px")
                .style("width", d => Math.max(0, d.x1 - d.x0 - 1) + "px")
                .style("height", d => Math.max(0, d.y1 - d.y0 - 1) + "px")
                .style("background", d => {
                    const color = getPositionColor(d.data.position);
                    // 인센티브 여부에 따라 그라데이션 조정
                    if (hasIncentive(d.data)) {
                        return `linear-gradient(135deg, $null, ${d3.color(color).darker(0.3)})`;
                    } else {
                        // 인센티브 미수령자는 더 어두운 색상
                        return `linear-gradient(135deg, ${d3.color(color).darker(0.5)}, ${d3.color(color).darker(0.8)})`;
                    }
                })
                .style("border", d => {
                    // 인센티브 여부에 따라 테두리 색상
                    return hasIncentive(d.data) ? "3px solid #28a745" : "3px solid #dc3545";
                })
                .style("overflow", "hidden")
                .style("cursor", "pointer")
                .style("transition", "all 0.3s ease")
                .on("mouseover", function(event, d) {
                    d3.select(this)
                        .style("z-index", 100)
                        .style("transform", "scale(1.02)")
                        .style("box-shadow", "0 4px 20px rgba(0,0,0,0.3)");

                    // Tooltip 표시
                    showTooltip(event, d);
                })
                .on("mouseout", function() {
                    d3.select(this)
                        .style("z-index", 1)
                        .style("transform", "scale(1)")
                        .style("box-shadow", "none");

                    hideTooltip();
                });

            // 라벨 추가
            nodes.append("div")
                .style("padding", "8px")
                .style("color", "white")
                .style("font-size", d => {
                    const width = d.x1 - d.x0;
                    const height = d.y1 - d.y0;
                    if (width > 100 && height > 60) return "14px";
                    if (width > 60 && height > 40) return "12px";
                    return "10px";
                })
                .style("text-shadow", "1px 1px 2px rgba(0,0,0,0.5)")
                .style("line-height", "1.3")
                .html(d => {
                    const width = d.x1 - d.x0;
                    const height = d.y1 - d.y0;

                    if (width > 100 && height > 100) {
                        return `
                            <div style="font-weight: bold; font-size: 14px;">${d.data.name}</div>
                            <div style="font-size: 10px; margin-top: 2px;">ID: ${d.data.id}</div>
                            <div style="font-size: 11px; margin-top: 2px;">${d.data.position}</div>
                            <div style="font-size: 10px; opacity: 0.9; margin-top: 2px;">
                                ${hasIncentive(d.data) ? `✅ ${getTranslation('orgChart.incentiveReceived', currentLanguage)}` : `❌ ${getTranslation('orgChart.incentiveNotReceived', currentLanguage)}`}
                            </div>
                        `;
                    } else if (width > 60 && height > 60) {
                        return `
                            <div style="font-weight: bold; font-size: 11px;">${d.data.name}</div>
                            <div style="font-size: 9px;">ID: ${d.data.id}</div>
                        `;
                    } else if (width > 40 && height > 40) {
                        const names = d.data.name.split(' ');
                        return `<div style="font-size: 10px;">${names[names.length - 1]}</div>`;
                    }
                    return '';
                });

            // Tooltip 함수들
            function showTooltip(event, d) {
                const tooltip = d3.select("body").append("div")
                    .attr("class", "treemap-tooltip")
                    .style("position", "absolute")
                    .style("padding", "12px")
                    .style("background", "rgba(0, 0, 0, 0.9)")
                    .style("color", "white")
                    .style("border-radius", "8px")
                    .style("font-size", "14px")
                    .style("pointer-events", "none")
                    .style("opacity", 0)
                    .style("z-index", 1000);

                tooltip.transition()
                    .duration(200)
                    .style("opacity", 0.9);

                tooltip.html(`
                    <strong>${d.data.name}</strong><br/>
                    ID: ${d.data.id}<br/>
                    직위: ${d.data.position}<br/>
                    타입: ${d.data.type}<br/>
                    인센티브: ${hasIncentive(d.data) ?
                        parseIncentive(d.data.incentive).toLocaleString() + ' VND ✅' :
                        '미수령 ❌'}
                `)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
            }

            function hideTooltip() {
                d3.selectAll(".treemap-tooltip").remove();
            }

            // Breadcrumb 업데이트
            updateBreadcrumb("Treemap 시각화");

        } catch (error) {
            console.error("트리맵 생성 오류:", error);
            treemapDiv.append("div")
                .style("text-align", "center")
                .style("padding", "20px")
                .text("트리맵 생성 중 오류가 발생했습니다: " + error.message);
        }
    }

    function drawVerticalTree() {
        console.log('Vertical tree deprecated - using collapsible tree');
        return;

        const container = d3.select("#orgChartContainer");
        if (!container.node()) {
            console.error('Container not found in drawVerticalTree');
            return;
        }
        const containerWidth = container.node().getBoundingClientRect().width;
        console.log('Container width in drawVerticalTree:', containerWidth);
        const width = Math.max(6000, containerWidth); // 더 넓게 설정하여 오버랩 방지
        const height = 3000; // 더 높게 설정하여 충분한 공간 확보
        const margin = { top: 120, right: 200, bottom: 200, left: 200 };

        const svg = d3.select("#orgChartSvg")
            .style("display", "block")  // SVG 다시 표시
            .attr("width", width)
            .attr("height", height);

        // Breadcrumb 업데이트
        updateBreadcrumb("수직 트리 (기본)");

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2},${margin.top})`); // 중앙 정렬

        // 데이터 준비
        let hierarchyData;
        try {
            hierarchyData = prepareHierarchyData();
            console.log('Hierarchy data prepared:', hierarchyData ? hierarchyData.length : 0, 'nodes');
        } catch (error) {
            console.error('Error preparing hierarchy data:', error);
            console.error('Stack trace:', error.stack);
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .style("fill", "#dc3545")
                .text("데이터 준비 중 오류: " + error.message);
            return;
        }

        if (!hierarchyData || hierarchyData.length === 0) {
            console.error('No hierarchy data available');
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .style("fill", "#dc3545")
                .text("조직도 데이터를 불러올 수 없습니다. 데이터를 확인해주세요.");
            return;
        }

        // D3 계층 구조 생성
        try {
            console.log('Creating D3 hierarchy...');
            console.log('Hierarchy data length:', hierarchyData.length);
            if (hierarchyData.length > 0) {
                console.log('Sample nodes:', hierarchyData.slice(0, 3));
            }

            const stratify = d3.stratify()
                .id(d => d.id)
                .parentId(d => d.parentId);

            orgChartRoot = stratify(hierarchyData);
            console.log('Root created with', orgChartRoot.descendants().length, 'descendants');

            // 수직 트리 레이아웃 생성 - nodeSize 사용으로 더 유연한 간격
            const treeLayout = d3.tree()
                .nodeSize([250, 200]) // [수평 간격, 수직 간격] - 크게 증가시켜 오버랩 방지
                .separation((a, b) => {
                    // Inspector 레벨에서는 훨씬 더 넓은 간격
                    const aIsInspector = a.data.position && a.data.position.includes('INSPECTOR');
                    const bIsInspector = b.data.position && b.data.position.includes('INSPECTOR');

                    if (aIsInspector || bIsInspector) {
                        return 3.0; // Inspector는 3배 간격으로 더 넓게
                    }

                    // Line Leader도 더 넓게
                    const aIsLineLeader = a.data.position && a.data.position.includes('LINE LEADER');
                    const bIsLineLeader = b.data.position && b.data.position.includes('LINE LEADER');

                    if (aIsLineLeader || bIsLineLeader) {
                        return 2.5; // Line Leader는 2.5배 간격
                    }

                    // Supervisor 레벨
                    const aIsSupervisor = a.data.position && a.data.position.includes('SUPERVISOR');
                    const bIsSupervisor = b.data.position && b.data.position.includes('SUPERVISOR');

                    if (aIsSupervisor || bIsSupervisor) {
                        return 2.0;
                    }

                    if (a.parent === b.parent) return 1.8; // 같은 부모 노드들도 간격 증가
                    return 2.0; // 기본 간격도 증가
                });

            treeLayout(orgChartRoot);

            // Inspector 레벨 노드들을 그리드 형태로 재배치
            const inspectorNodes = orgChartRoot.descendants().filter(d =>
                d.data.position && d.data.position.includes('INSPECTOR')
            );

            if (inspectorNodes.length > 0) {
                // Inspector들을 부모별로 그룹화
                const inspectorsByParent = {};
                inspectorNodes.forEach(node => {
                    const parentId = node.parent ? node.parent.data.id : 'root';
                    if (!inspectorsByParent[parentId]) {
                        inspectorsByParent[parentId] = [];
                    }
                    inspectorsByParent[parentId].push(node);
                });

                // 각 그룹 내에서 Inspector들을 여러 줄로 배치
                Object.keys(inspectorsByParent).forEach(parentId => {
                    const group = inspectorsByParent[parentId];
                    const maxPerRow = 8; // 한 줄에 최대 8명

                    group.forEach((node, index) => {
                        const row = Math.floor(index / maxPerRow);
                        const col = index % maxPerRow;
                        const groupCenter = group[0].parent ? group[0].parent.x : 0;

                        // 수평 위치: 그룹 중앙을 기준으로 배치
                        const totalWidth = Math.min(maxPerRow, group.length) * 100;
                        const startX = groupCenter - totalWidth / 2;
                        node.x = startX + col * 100;

                        // 수직 위치: 행에 따라 조정
                        if (row > 0) {
                            node.y = node.y + row * 100;
                        }
                    });
                });
            }

            // 링크 그리기 - 수직 연결선
            const link = g.selectAll(".link")
                .data(orgChartRoot.links())
                .enter().append("g")
                .attr("class", "link");

            // 계단식 연결선 (더 명확한 계층 표현)
            link.append("path")
                .attr("fill", "none")
                .attr("stroke", "#999")
                .attr("stroke-width", 2)
                .attr("d", d => {
                    // 수직 계단식 경로
                    const sourceX = d.source.x - width / 2 + margin.left;
                    const sourceY = d.source.y;
                    const targetX = d.target.x - width / 2 + margin.left;
                    const targetY = d.target.y;
                    const midY = (sourceY + targetY) / 2;

                    return `M $null $null
                            L $null $null
                            L $null $null
                            L $null $null`;
                });

            // 노드 그룹 생성
            const node = g.selectAll(".node")
                .data(orgChartRoot.descendants())
                .enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${d.x - width / 2 + margin.left},${d.y})`)
                .on("mouseover", showTooltip)
                .on("mouseout", hideTooltip)
                .on("click", nodeClick);

            // 노드 박스 그리기 (인센티브 여부에 따라 색상 변경)
            node.append("rect")
                .attr("width", 180)  // 박스 폭 더 크게 (ID 추가를 위해)
                .attr("height", 90)  // 박스 높이 더 크게
                .attr("x", -90)
                .attr("y", -45)
                .attr("fill", d => {
                    const baseColor = getNodeColor(d.data);
                    // 인센티브 수령 여부에 따라 색상 조정
                    if (hasIncentive(d.data)) {
                        return baseColor; // 원래 색상 유지
                    } else {
                        return baseColor + "40"; // 40% 투명도로 희미하게
                    }
                })
                .attr("stroke", d => hasIncentive(d.data) ? "#28a745" : "#dc3545")
                .attr("stroke-width", 3)
                .attr("rx", 5)
                .attr("ry", 5)
                .style("filter", "drop-shadow(2px 2px 4px rgba(0,0,0,0.2))");

            // 직급 텍스트
            node.append("text")
                .attr("dy", "-22px")  // 상단 위치
                .attr("text-anchor", "middle")
                .style("font-size", "11px")
                .style("font-weight", "bold")
                .style("fill", "white")
                .text(d => d.data.position);

            // 이름 텍스트
            node.append("text")
                .attr("dy", "0px")  // 중간 위치
                .attr("text-anchor", "middle")
                .style("font-size", "12px")
                .style("fill", "white")
                .style("font-weight", "bold")
                .text(d => d.data.name);

            // ID 텍스트 추가
            node.append("text")
                .attr("dy", "22px")  // 하단 위치
                .attr("text-anchor", "middle")
                .style("font-size", "10px")
                .style("fill", "white")
                .text(d => `ID: ${d.data.id}`);

            // 줌 및 패닝 기능 추가
            currentZoomBehavior = d3.zoom()
                .scaleExtent([0.1, 3])  // 더 작게 축소 가능
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });

            svg.call(currentZoomBehavior);

            // 초기 줌 레벨 설정 (전체가 보이도록) - 더 작게
            const initialScale = 0.4;  // 더 작은 초기 줌 (전체 조직도가 보이도록)
            svg.call(currentZoomBehavior.transform, d3.zoomIdentity
                .translate(width / 2, margin.top)
                .scale(initialScale));

        } catch (error) {
            console.error("조직도 생성 오류:", error);
            console.error("Error details:", error.message);
            console.error("Error stack:", error.stack);
            console.error("Problematic data sample:", hierarchyData ? hierarchyData.slice(0, 5) : 'No data');

            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .text("조직도 생성 중 오류가 발생했습니다: " + error.message);
        }
    }

    function prepareHierarchyData() {
        console.log('Preparing organization hierarchy data...');
        console.log('Total employees:', employeeData.length);

        // 먼저 데이터가 비어있는지 확인
        if (!employeeData || employeeData.length === 0) {
            console.error('No employee data available!');
            return [];
        }

        // 첫 몇 명의 직원 데이터 확인
        console.log('First employee sample:', employeeData[0]);

        // 제외할 포지션 정의
        const excludedPositions = ['MODEL MASTER', 'AUDIT & TRAINING TEAM', 'AQL INSPECTOR'];

        // TYPE-1 직원 중 특정 포지션 제외
        const type1Employees = employeeData.filter(e =>
            e.type === 'TYPE-1' &&
            !excludedPositions.includes(e.position)
        );
        console.log('TYPE-1 employees (excluding excluded positions):', type1Employees.length);

        // 전략 결정: TYPE-1이 너무 적으면 전체 조직도 표시
        let useAllEmployees = false;
        let requiredIds = new Set();

        if (type1Employees.length < 5) {
            console.log('Too few TYPE-1 employees, showing full organization chart');
            useAllEmployees = true;

            // 모든 직원 추가 (제외 포지션 제외)
            employeeData.forEach(emp => {
                if (!excludedPositions.includes(emp.position)) {
                    requiredIds.add(emp.emp_no);
                }
            });
        } else {
            // TYPE-1 직원들을 먼저 추가
            type1Employees.forEach(emp => {
                requiredIds.add(emp.emp_no);
            });

            // 상사 체인을 재귀적으로 추가 (실제 존재하는 직원만)
            const addBossChain = (empId) => {
                const emp = employeeData.find(e => e.emp_no === empId);
                if (!emp) return;

                if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== '0') {
                    // 상사가 실제로 employeeData에 존재하는지 확인
                    const bossExists = employeeData.some(e => e.emp_no === emp.boss_id);

                    if (bossExists && !requiredIds.has(emp.boss_id)) {
                        requiredIds.add(emp.boss_id);
                        addBossChain(emp.boss_id); // 재귀적으로 상사의 상사 추가
                    } else if (!bossExists) {
                        console.log(`Boss ID ${emp.boss_id} not found in data for employee ${emp.name} (${emp.emp_no})`);
                    }
                }
            };

            // 모든 TYPE-1 직원의 상사 체인 추가
            type1Employees.forEach(emp => {
                addBossChain(emp.emp_no);
            });
        }

        console.log('Total required nodes:', requiredIds.size, useAllEmployees ? '(showing all employees)' : '(TYPE-1 + bosses)');

        // 디버깅: 첫 5개 직원 데이터 확인
        if (employeeData.length > 0) {
            console.log('Sample employee data:', employeeData.slice(0, 5).map(e => ({
                name: e.name,
                position: e.position,
                boss_id: e.boss_id,
                boss_name: e.boss_name
            })));
        }

        const data = [];
        const employeeById = {};

        // 직원 ID 맵 생성 (빈 데이터 필터링)
        employeeData.forEach(emp => {
            // nan이거나 빈 emp_no는 제외
            if (emp.emp_no && emp.emp_no !== 'nan' && emp.emp_no !== '') {
                employeeById[emp.emp_no] = emp;
            }
        });

        // 모든 직원을 노드로 추가 (실제 boss_id 사용)
        let noParentCount = 0;
        let hasParentCount = 0;

        employeeData.forEach(emp => {
            // 빈 데이터 건너뛰기
            if (!emp.emp_no || emp.emp_no === 'nan' || emp.emp_no === '') {
                return;
            }

            // 제외할 포지션이면 건너뛰기
            if (excludedPositions.includes(emp.position)) {
                console.log(`Excluding ${emp.name} (${emp.position}) from org chart`);
                return;
            }

            // 필요한 직원이 아니면 건너뛰기 (TYPE-1이거나 TYPE-1의 상사 체인에 포함)
            if (!requiredIds.has(emp.emp_no)) {
                return;
            }

            // boss_id가 있으면 사용, 없으면 boss_name으로 찾기
            let parentId = null;

            if (emp.boss_id && emp.boss_id !== '' && emp.boss_id !== 'nan' && emp.boss_id !== 'None' && emp.boss_id !== '0') {
                // boss_id가 직원 목록에 있고 requiredIds에도 포함되어 있는지 확인
                if (employeeById[emp.boss_id] && requiredIds.has(emp.boss_id)) {
                    parentId = emp.boss_id;
                } else if (employeeById[emp.boss_id]) {
                    // 상사가 존재하지만 TYPE-1 체인에 포함되지 않음
                    console.log(`Boss ${emp.boss_id} exists but not in TYPE-1 chain for ${emp.name}`);
                } else {
                    console.log(`Warning: Boss ${emp.boss_id} not found in data for ${emp.name}`);
                    // 상사가 목록에 없으면 parent 없음으로 처리
                }
            }

            if (!parentId && emp.boss_name && emp.boss_name !== '') {
                // boss_name으로 boss 찾기
                const boss = employeeData.find(e => e.name === emp.boss_name);
                if (boss) {
                    parentId = boss.emp_no;
                }
            }

            if (parentId) {
                hasParentCount++;
            } else {
                noParentCount++;
            }

            data.push({
                id: emp.emp_no,
                name: emp.name,
                position: emp.position || 'Unknown',
                type: emp.type || '',
                incentive: emp[dashboardMonth + '_incentive'] || '0',
                parentId: parentId
            });
        });

        console.log(`Created ${data.length} nodes: $null with parent, $null without parent`);

        // 루트 노드 확인
        const rootNodes = data.filter(d => !d.parentId);
        console.log('Root nodes found:', rootNodes.length);

        // 항상 가상 루트 생성 (조직도의 시작점)
        const rootTitle = requiredIds.size > 100 ? "Hwaseung Organization" : "Hwaseung TYPE-1 Organization";
        const rootSubtitle = requiredIds.size > 100 ? "Full Organization Chart" : "TYPE-1 Management";
        data.unshift({
            id: "root",
            name: rootTitle,
            position: rootSubtitle,
            type: "ROOT",
            incentive: "0",
            parentId: null
        });

        if (rootNodes.length === 0) {
            console.log('No natural root found, connecting managers to virtual root...');
            // Manager 레벨 직원들을 루트에 연결
            const managers = data.filter(d => {
                if (d.id === "root") return false;
                const pos = (d.position || '').toUpperCase();
                return pos.includes('MANAGER') && !pos.includes('A.') && !pos.includes('ASSISTANT');
            });

            if (managers.length === 0) {
                // Manager가 없으면 A.Manager를 찾음
                const aManagers = data.filter(d => {
                    if (d.id === "root") return false;
                    const pos = (d.position || '').toUpperCase();
                    return pos.includes('A.MANAGER') || pos.includes('ASSISTANT MANAGER');
                });

                aManagers.forEach(manager => {
                    const idx = data.findIndex(d => d.id === manager.id);
                    if (idx !== -1) {
                        data[idx].parentId = "root";
                    }
                });
            } else {
                managers.forEach(manager => {
                    const idx = data.findIndex(d => d.id === manager.id);
                    if (idx !== -1) {
                        data[idx].parentId = "root";
                    }
                });
            }
        } else {
            console.log(`${rootNodes.length} natural root nodes found, connecting to virtual root...`);

            // 루트 노드들을 가상 루트에 연결
            rootNodes.forEach(node => {
                // Manager 또는 상위 직급만 루트에 직접 연결
                const pos = (node.position || '').toUpperCase();
                if (pos.includes('MANAGER') || pos.includes('SUPERVISOR') || rootNodes.length <= 5) {
                    const idx = data.findIndex(d => d.id === node.id);
                    if (idx !== -1) {
                        data[idx].parentId = "root";
                    }
                }
                // 그 외는 적절한 상위 직급 찾기
                else {
                    // 같은 타입의 상위 직급 찾기
                    const superiors = data.filter(d => {
                        if (d.id === "root" || d.id === node.id) return false;
                        const dPos = (d.position || '').toUpperCase();
                        return dPos.includes('MANAGER') || dPos.includes('SUPERVISOR');
                    });

                    if (superiors.length > 0) {
                        const idx = data.findIndex(d => d.id === node.id);
                        if (idx !== -1) {
                            data[idx].parentId = superiors[0].id;
                        }
                    } else {
                        // 상위 직급이 없으면 루트에 연결
                        const idx = data.findIndex(d => d.id === node.id);
                        if (idx !== -1) {
                            data[idx].parentId = "root";
                        }
                    }
                }
            });
        }




        // 필터 적용
        const typeFilterElement = document.getElementById('orgTypeFilter');
        const incentiveFilterElement = document.getElementById('orgIncentiveFilter');

        const typeFilter = typeFilterElement ? typeFilterElement.value : '';
        const incentiveFilter = incentiveFilterElement ? incentiveFilterElement.value : '';

        let filteredData = data;

        if (typeFilter) {
            filteredData = filteredData.filter(d => d.type === typeFilter || d.id === "root");
        }

        if (incentiveFilter === 'paid') {
            filteredData = filteredData.filter(d => parseIncentive(d.incentive) > 0 || d.id === "root");
        } else if (incentiveFilter === 'unpaid') {
            filteredData = filteredData.filter(d => parseIncentive(d.incentive) === 0 || d.id === "root");
        }

        console.log('Hierarchy data prepared:', filteredData.length, 'nodes');
        return filteredData;
    }

    function getNodeColor(node) {
        const position = node.position.toUpperCase();
        if (position.includes('MANAGER')) return '#1f77b4';
        if (position.includes('SUPERVISOR')) return '#2ca02c';
        if (position.includes('GROUP') && position.includes('LEADER')) return '#ff7f0e';
        if (position.includes('LINE') && position.includes('LEADER')) return '#d62728';
        if (position.includes('INSPECTOR')) return '#9467bd';
        return '#8c564b';
    }

    function showTooltip(event, d) {
        const tooltip = d3.select("#orgTooltip");
        const incentive = parseIncentive(d.data.incentive);

        tooltip.html(`
            <strong>${d.data.name}</strong><br/>
            사번: ${d.data.id}<br/>
            직급: ${d.data.position}<br/>
            Type: ${d.data.type}<br/>
            인센티브: ${incentive.toLocaleString()} VND<br/>
            상사: ${d.data.boss_name || '없음'}
        `);

        tooltip.style("visibility", "visible")
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    }

    function hideTooltip() {
        d3.select("#orgTooltip").style("visibility", "hidden");
    }

    function nodeClick(event, d) {
        // 노드 클릭시 해당 직원 상세 정보 표시
        const emp = employeeData.find(e => e.emp_no === d.data.id);
        if (emp) {
            showEmployeeDetail(emp);
        }
    }

    function updateOrgChart() {
        drawOrgChart();
    }

    function resetOrgChart() {
        const typeFilterElement = document.getElementById('orgTypeFilter');
        const incentiveFilterElement = document.getElementById('orgIncentiveFilter');

        if (typeFilterElement) typeFilterElement.value = '';
        if (incentiveFilterElement) incentiveFilterElement.value = '';
        drawOrgChart();
    }

    function exportOrgChart() {
        // SVG를 이미지로 저장
        const svg = document.getElementById('orgChartSvg');
        const serializer = new XMLSerializer();
        const svgStr = serializer.serializeToString(svg);
        const svgBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `organization_chart_${new Date().toISOString().slice(0,10)}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // window.onload removed - integrated into DOMContentLoaded
    
    // Talent Program 텍스트 업데이트 함수
    function updateTalentProgramTexts() {
        const lang = currentLanguage;
        
        // 메인 제목
        const programTitle = document.getElementById('talentProgramTitle');
        if (programTitle) {
            programTitle.innerHTML = getTranslation('talentProgram.title', lang) || '🌟 QIP Talent Pool 인센티브 프로그램';
        }
        
        // 소개 텍스트
        const programIntro = document.getElementById('talentProgramIntro');
        if (programIntro) {
            programIntro.innerHTML = `<strong>QIP Talent Pool</strong> ${getTranslation('talentProgram.intro', lang) || 'QIP Talent Pool은 우수한 성과를 보이는 인원들을 대상으로 하는 특별 인센티브 프로그램입니다. 선정된 인원은 6개월간 매월 추가 보너스를 받게 됩니다.'}`;
        }
        
        // 선정 기준 제목
        const qualificationTitle = document.getElementById('talentProgramQualificationTitle');
        if (qualificationTitle) {
            qualificationTitle.textContent = getTranslation('talentProgram.qualificationTitle', lang) || '🎯 선정 기준';
        }
        
        // 선정 기준 목록
        const qualifications = document.getElementById('talentProgramQualifications');
        if (qualifications) {
            const items = [
                lang === 'en' ? 'Outstanding work performance' : 
                lang === 'vi' ? 'Hiệu suất làm việc xuất sắc' : '업무 성과 우수자',
                
                lang === 'en' ? 'Top 10% in quality target achievement' :
                lang === 'vi' ? 'Top 10% đạt mục tiêu chất lượng' : '품질 목표 달성률 상위 10%',
                
                lang === 'en' ? 'Demonstrated teamwork and leadership' :
                lang === 'vi' ? 'Thể hiện tinh thần đồng đội và lãnh đạo' : '팀워크 및 리더십 발휘',
                
                lang === 'en' ? 'Active participation in continuous improvement' :
                lang === 'vi' ? 'Tham gia tích cực vào hoạt động cải tiến liên tục' : '지속적인 개선 활동 참여'
            ];
            qualifications.innerHTML = items.map(item => `<li>$null</li>`).join('');
        }
        
        // 혜택 제목
        const benefitsTitle = document.getElementById('talentProgramBenefitsTitle');
        if (benefitsTitle) {
            benefitsTitle.textContent = getTranslation('talentProgram.benefitsTitle', lang) || '💰 혜택';
        }
        
        // 월 보너스 제목
        const monthlyBonusTitle = document.getElementById('talentProgramMonthlyBonusTitle');
        if (monthlyBonusTitle) {
            monthlyBonusTitle.textContent = getTranslation('talentProgram.monthlyBonusTitle', lang) || '월 특별 보너스';
        }
        
        // 총 보너스 제목
        const totalBonusTitle = document.getElementById('talentProgramTotalBonusTitle');
        if (totalBonusTitle) {
            totalBonusTitle.textContent = getTranslation('talentProgram.totalBonusTitle', lang) || '총 지급 예정액 (6개월)';
        }
        
        // 프로세스 제목
        const processTitle = document.getElementById('talentProgramProcessTitle');
        if (processTitle) {
            processTitle.textContent = getTranslation('talentProgram.processTitle', lang) || '📋 평가 프로세스 (6개월 주기)';
        }
        
        // 6단계 프로세스 업데이트
        const steps = [
            {
                titleId: 'talentStep1Title',
                descId: 'talentStep1Desc',
                titleKo: '후보자 추천',
                titleEn: 'Candidate Nomination',
                titleVi: 'Đề cử ứng viên',
                descKo: '각 부서에서 우수 인원 추천',
                descEn: 'Departments nominate outstanding employees',
                descVi: 'Các phòng ban đề cử nhân viên xuất sắc'
            },
            {
                titleId: 'talentStep2Title',
                descId: 'talentStep2Desc',
                titleKo: '성과 평가',
                titleEn: 'Performance Evaluation',
                titleVi: 'Đánh giá hiệu suất',
                descKo: '최근 3개월간 성과 데이터 분석',
                descEn: 'Analysis of last 3 months performance data',
                descVi: 'Phân tích dữ liệu hiệu suất 3 tháng gần nhất'
            },
            {
                titleId: 'talentStep3Title',
                descId: 'talentStep3Desc',
                titleKo: '위원회 심사',
                titleEn: 'Committee Review',
                titleVi: 'Xét duyệt của ủy ban',
                descKo: 'QIP 운영위원회 최종 심사',
                descEn: 'Final review by QIP committee',
                descVi: 'Xét duyệt cuối cùng bởi ủy ban QIP'
            },
            {
                titleId: 'talentStep4Title',
                descId: 'talentStep4Desc',
                titleKo: '최종 선정',
                titleEn: 'Final Selection',
                titleVi: 'Lựa chọn cuối cùng',
                descKo: 'Talent Pool 멤버 확정 및 공지',
                descEn: 'Confirmation and announcement of Talent Pool members',
                descVi: 'Xác nhận và thông báo thành viên Talent Pool'
            },
            {
                titleId: 'talentStep5Title',
                descId: 'talentStep5Desc',
                titleKo: '보너스 지급',
                titleEn: 'Bonus Payment',
                titleVi: 'Thanh toán thưởng',
                descKo: '매월 정기 인센티브와 함께 지급',
                descEn: 'Paid together with regular monthly incentives',
                descVi: 'Thanh toán cùng với khen thưởng định kỳ hàng tháng'
            },
            {
                titleId: 'talentStep6Title',
                descId: 'talentStep6Desc',
                titleKo: '재평가',
                titleEn: 'Re-evaluation',
                titleVi: 'Đánh giá lại',
                descKo: '6개월 후 재평가 실시',
                descEn: 'Re-evaluation after 6 months',
                descVi: 'Đánh giá lại sau 6 tháng'
            }
        ];
        
        steps.forEach(step => {
            const titleEl = document.getElementById(step.titleId);
            if (titleEl) {
                titleEl.textContent = lang === 'en' ? step.titleEn : lang === 'vi' ? step.titleVi : step.titleKo;
            }
            const descEl = document.getElementById(step.descId);
            if (descEl) {
                descEl.textContent = lang === 'en' ? step.descEn : lang === 'vi' ? step.descVi : step.descKo;
            }
        });
        
        // 중요 사항 제목
        const importantTitle = document.getElementById('talentProgramImportantTitle');
        if (importantTitle) {
            importantTitle.textContent = getTranslation('talentProgram.importantTitle', lang) || '⚠️ 중요 사항';
        }
        
        // 중요 사항 목록
        const importantNotes = document.getElementById('talentProgramImportantNotes');
        if (importantNotes) {
            const notes = [
                lang === 'en' ? 'Talent Pool bonus is paid separately from regular incentives' :
                lang === 'vi' ? 'Thưởng Talent Pool được thanh toán riêng biệt với khen thưởng thường xuyên' :
                'Talent Pool 보너스는 기본 인센티브와 별도로 지급됩니다',
                
                lang === 'en' ? 'Eligibility is automatically lost upon resignation during the payment period' :
                lang === 'vi' ? 'Tư cách sẽ tự động mất khi nghỉ việc trong thời gian thanh toán' :
                '지급 기간 중 퇴사 시 자격이 자동 상실됩니다',
                
                lang === 'en' ? 'May be terminated early if performance is insufficient' :
                lang === 'vi' ? 'Có thể kết thúc sớm nếu hiệu suất không đủ' :
                '성과 미달 시 조기 종료될 수 있습니다',
                
                lang === 'en' ? 'Renewal is determined through re-evaluation every 6 months' :
                lang === 'vi' ? 'Việc gia hạn được quyết định thông qua đánh giá lại mỗi 6 tháng' :
                '매 6개월마다 재평가를 통해 갱신 여부가 결정됩니다'
            ];
            importantNotes.innerHTML = notes.map(note => `<li>$null</li>`).join('');
        }
        
        // 현재 멤버 제목
        const currentTitle = document.getElementById('talentProgramCurrentTitle');
        if (currentTitle) {
            currentTitle.textContent = getTranslation('talentProgram.currentTitle', lang) || '🎉 현재 Talent Pool 멤버';
        }
        
        // 멤버가 없을 때 메시지 업데이트
        const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
        if (currentMembersDiv && currentMembersDiv.innerHTML.includes('현재 Talent Pool 멤버가 없습니다')) {
            currentMembersDiv.innerHTML = `<p>${getTranslation('talentProgram.noMembers', lang) || '현재 Talent Pool 멤버가 없습니다.'}</p>`;
        }
    }
    
    // Talent Pool 섹션 업데이트
    function updateTalentPoolSection() {
        const talentPoolMembers = employeeData.filter(emp => emp.Talent_Pool_Member === 'Y' || emp.Talent_Pool_Member === true);
        
        if (talentPoolMembers.length > 0) {
            // Talent Pool 섹션 표시
            document.getElementById('talentPoolSection').style.display = 'block';
            
            // 통계 업데이트
            const totalBonus = talentPoolMembers.reduce((sum, emp) => sum + parseInt(emp.Talent_Pool_Bonus || 0), 0);
            const monthlyBonus = talentPoolMembers[0]?.Talent_Pool_Bonus || 0; // 첫 번째 멤버의 월 보너스
            
            document.getElementById('talentPoolCount').textContent = talentPoolMembers.length + '명';
            document.getElementById('talentPoolMonthlyBonus').textContent = parseInt(monthlyBonus).toLocaleString() + ' VND';
            document.getElementById('talentPoolTotalBonus').textContent = totalBonus.toLocaleString() + ' VND';
            document.getElementById('talentPoolPeriod').textContent = '2025.07 - 2025.12';
            
            // 멤버 목록 생성
            const membersLabel = getTranslation('talentPool.membersList', currentLanguage) || 'Talent Pool 멤버:';
            let membersHtml = `<div class="mt-2"><small style="opacity: 0.9;">$null</small><br>`;
            talentPoolMembers.forEach(emp => {
                membersHtml += `
                    <span class="badge" style="background: rgba(255,255,255,0.3); margin: 2px; padding: 5px 10px;">
                        ${emp.name} (${emp.emp_no}) - ${emp.position}
                    </span>
                `;
            });
            membersHtml += '</div>';
            document.getElementById('talentPoolMembers').innerHTML = membersHtml;
            
            // 인센티브 기준 탭의 Talent Program 현재 멤버 섹션도 업데이트
            const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
            if (currentMembersDiv) {
                let currentMembersHtml = '';
                talentPoolMembers.forEach(emp => {
                    currentMembersHtml += `
                        <div class="badge" style="background: rgba(255,255,255,0.3); font-size: 1.1em; margin: 5px; padding: 8px 15px;">
                            <i class="fas fa-star"></i> ${emp.name} (${emp.emp_no}) - ${emp.position}
                        </div>
                    `;
                });
                if (currentMembersHtml === '') {
                    currentMembersHtml = '<p>현재 Talent Pool 멤버가 없습니다.</p>';
                }
                currentMembersDiv.innerHTML = currentMembersHtml;
            }
        } else {
            // Talent Pool 멤버가 없는 경우
            const currentMembersDiv = document.getElementById('talentProgramCurrentMembers');
            if (currentMembersDiv) {
                currentMembersDiv.innerHTML = '<p>현재 Talent Pool 멤버가 없습니다.</p>';
            }
        }
    }
    
    // 탭 전환 - Make it globally accessible
    window.showTab = function showTab(tabName) {
        // 모든 탭과 컨텐츠 숨기기
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // 선택된 탭과 컨텐츠 표시
        const tabElement = document.querySelector(`[data-tab="${tabName}"]`);
        if (tabElement) {
            tabElement.classList.add('active');
        }
        const contentElement = document.getElementById(tabName);
        if (contentElement) {
            contentElement.classList.add('active');
        }

        // 직급별 상세 탭이면 테이블 생성
        if (tabName === 'position') {
            console.log('Position tab selected');
            setTimeout(() => {
                generatePositionTables();
            }, 100);
        }

        // 조직도 탭이면 조직도 그리기
        if (tabName === 'orgchart') {
            console.log('Organization chart tab selected');
            setTimeout(() => {
                console.log('Calling drawOrgChart from showTab...');
                drawOrgChart();
            }, 100);
        }

        // 검증 탭이면 KPI 카드 초기화
        if (tabName === 'validation') {
            console.log('Validation tab selected');
            setTimeout(() => {
                initValidationTab();
            }, 100);
        }
    }
    
    // 직원 테이블 생성
    function generateEmployeeTable() {
        const tbody = document.getElementById('employeeTableBody');
        tbody.innerHTML = '';
        
        employeeData.forEach(emp => {
            const amount = getIncentiveAmount(emp);
            const isPaid = amount > 0;
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer';
            tr.onclick = () => showEmployeeDetail(emp.emp_no);
            
            // Talent Pool 멤버인 경우 특별 스타일 적용
            if (emp.Talent_Pool_Member === 'Y') {
                tr.className = 'talent-pool-row';
            }
            
            // Talent Pool 정보 HTML 생성
            let talentPoolHTML = '-';
            if (emp.Talent_Pool_Member === 'Y') {
                talentPoolHTML = `
                    <div class="talent-pool-tooltip">
                        <span class="talent-pool-star">🌟</span>
                        <strong>${parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()} VND</strong>
                        <span class="tooltiptext">
                            <strong>${getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}</strong><br>
                            ${getTranslation('talentPool.monthlyBonus', currentLanguage) || '월 특별 보너스'}: ${parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()} VND<br>
                            ${getTranslation('talentPool.period', currentLanguage) || '지급 기간'}: 2025.07 - 2025.12
                        </span>
                    </div>
                `;
            }
            
            tr.innerHTML = `
                <td>${emp.emp_no}</td>
                <td>${emp.name}${emp.Talent_Pool_Member === 'Y' ? '<span class="talent-pool-badge">TALENT</span>' : ''}</td>
                <td>${emp.position}</td>
                <td><span class="type-badge type-${emp.type.toLowerCase().replace('type-', '')}">${emp.type}</span></td>
                <td>${parseInt(emp.july_incentive).toLocaleString()}</td>
                <td><strong>${amount.toLocaleString()}</strong></td>
                <td>$null</td>
                <td>${isPaid ? '✅ ' + getTranslation('status.paid') : '❌ ' + getTranslation('status.unpaid')}</td>
                <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${emp.emp_no}')">${getTranslation('individual.table.detailButton')}</button></td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    // 직급별 테이블 생성 (dashboard_version4.html과 동일한 UI)
    function generatePositionTables() {
        const positionData = {};
        
        // Type-직급별 데이터 집계
        employeeData.forEach(emp => {
            const key = `${emp.type}_${emp.position}`;
            if (!positionData[key]) {
                positionData[key] = {
                    type: emp.type,
                    position: emp.position,
                    total: 0,
                    paid: 0,
                    totalAmount: 0,
                    employees: []
                };
            }
            
            positionData[key].total++;
            positionData[key].employees.push(emp);
            // Use the helper function to get incentive amount
            const amount = getIncentiveAmount(emp);
            if (amount > 0) {
                positionData[key].paid++;
                positionData[key].totalAmount += amount;
            }
        });
        
        // Type별로 그룹핑
        const groupedByType = {};
        Object.values(positionData).forEach(data => {
            if (!groupedByType[data.type]) {
                groupedByType[data.type] = [];
            }
            groupedByType[data.type].push(data);
        });
        
        // HTML 생성
        const container = document.getElementById('positionContent');
        if (container) {
            container.innerHTML = '';
            
            // Type별로 섹션 생성
            Object.entries(groupedByType).sort().forEach(([type, positions]) => {
                const typeClass = type.toLowerCase().replace('type-', '');
                
                // 섹션 제목 번역
                const sectionTitle = type === 'TYPE-1' ? getTranslation('position.sectionTitles.type1', currentLanguage) :
                                   type === 'TYPE-2' ? getTranslation('position.sectionTitles.type2', currentLanguage) :
                                   type === 'TYPE-3' ? getTranslation('position.sectionTitles.type3', currentLanguage) : 
                                   `${type} 직급별 현황`;
                
                // 칼럼 헤더 번역 먼저 준비
                const colPosition = getTranslation('position.positionTable.columns.position', currentLanguage);
                const colTotal = getTranslation('position.positionTable.columns.total', currentLanguage);
                const colPaid = getTranslation('position.positionTable.columns.paid', currentLanguage);
                const colPaymentRate = getTranslation('position.positionTable.columns.paymentRate', currentLanguage);
                const colTotalAmount = getTranslation('position.positionTable.columns.totalAmount', currentLanguage);
                const colAvgAmount = getTranslation('position.positionTable.columns.avgAmount', currentLanguage);
                const colDetails = getTranslation('position.positionTable.columns.details', currentLanguage);
                
                let html = '';
                html += '<div class="mb-5">';
                html += '<h4 class="mb-3">';
                html += '<span class="type-badge type-' + typeClass + '">' + type + '</span> ';
                html += sectionTitle.replace(type + ' ', '');
                html += '</h4>';
                html += '<table class="table table-hover">';
                html += '<thead>';
                html += '<tr>';
                html += '<th>' + colPosition + '</th>';
                html += '<th>' + colTotal + '</th>';
                html += '<th>' + colPaid + '</th>';
                html += '<th>' + colPaymentRate + '</th>';
                html += '<th>' + colTotalAmount + '</th>';
                html += '<th>' + colAvgAmount + '</th>';
                html += '<th>' + colDetails + '</th>';
                html += '</tr>';
                html += '</thead>';
                html += '<tbody>';
                
                // 직급별 행 추가
                positions.sort((a, b) => a.position.localeCompare(b.position)).forEach(posData => {
                    const paymentRate = posData.total > 0 ? (posData.paid / posData.total * 100).toFixed(1) : '0.0';
                    const avgAmount = posData.paid > 0 ? Math.round(posData.totalAmount / posData.paid) : 0;
                    const peopleUnit = getTranslation('common.people', currentLanguage);
                    const viewBtnText = getTranslation('position.viewButton', currentLanguage);
                    
                    html += '<tr>';
                    html += '<td>' + posData.position + '</td>';
                    html += '<td>' + posData.total + ' ' + peopleUnit + '</td>';
                    html += '<td>' + posData.paid + ' ' + peopleUnit + '</td>';
                    html += '<td>' + paymentRate + '%</td>';
                    html += '<td>' + posData.totalAmount.toLocaleString() + ' VND</td>';
                    html += '<td>' + avgAmount.toLocaleString() + ' VND</td>';
                    html += '<td>';
                    html += '<button class="btn btn-sm btn-outline-primary" ';
                    html += `onclick="showPositionDetail('${type}', '${posData.position}')">`;
                    html += viewBtnText;
                    html += '</button>';
                    html += '</td>';
                    html += '</tr>';
                });
                
                // Type별 소계
                const typeTotal = positions.reduce((acc, p) => acc + p.total, 0);
                const typePaid = positions.reduce((acc, p) => acc + p.paid, 0);
                const typeAmount = positions.reduce((acc, p) => acc + p.totalAmount, 0);
                const typeRate = typeTotal > 0 ? (typePaid / typeTotal * 100).toFixed(1) : '0.0';
                const typeAvg = typePaid > 0 ? Math.round(typeAmount / typePaid) : 0;
                
                // 푸터 텍스트 준비
                const footerTitle = type === 'TYPE-1' ? getTranslation('position.sectionTitles.type1Total', currentLanguage) :
                                  type === 'TYPE-2' ? getTranslation('position.sectionTitles.type2Total', currentLanguage) :
                                  type === 'TYPE-3' ? getTranslation('position.sectionTitles.type3Total', currentLanguage) :
                                  type + ' 합계';
                const peopleUnit2 = getTranslation('common.people', currentLanguage);
                
                html += '</tbody>';
                html += '<tfoot>';
                html += '<tr style="font-weight: bold; background-color: #f8f9fa;">';
                html += '<td>' + footerTitle + '</td>';
                html += '<td>' + typeTotal + ' ' + peopleUnit2 + '</td>';
                html += '<td>' + typePaid + ' ' + peopleUnit2 + '</td>';
                html += '<td>' + typeRate + '%</td>';
                html += '<td>' + typeAmount.toLocaleString() + ' VND</td>';
                html += '<td>' + typeAvg.toLocaleString() + ' VND</td>';
                html += '<td></td>';
                html += '</tr>';
                html += '</tfoot>';
                html += '</table>';
                html += '</div>';
                
                const div = document.createElement('div');
                div.innerHTML = html;
                container.appendChild(div);
            });
        }
    }
    
    // 직급별 상세 팝업 - 완전 새로운 UI
    function showPositionDetail(type, position) {
        const employees = employeeData.filter(e => e.type === type && e.position === position);
        if (employees.length === 0) return;

        // 각 직원의 condition_results가 없으면 평가 수행
        employees.forEach(emp => {
            // 먼저 Excel의 평가 결과를 확인 (Single Source of Truth)
            const hasExcelResults = emp.All_Conditions_Met !== undefined ||
                                   emp.condition_1_met !== undefined ||
                                   emp.condition_results?.length > 0;

            // 실제 인센티브 지급 여부 확인 (이것이 진실의 소스)
            const actualIncentive = getIncentiveAmount(emp);
            const isPaid = actualIncentive > 0;

            if (!hasExcelResults || !emp.condition_results || emp.condition_results.length === 0) {
                const evaluationResults = evaluateEmployeeConditions(emp);
                // evaluateEmployeeConditions의 결과를 Position Details 모달이 기대하는 형식으로 변환
                // 중요: 실제 지급 여부와 일치하도록 조정
                emp.condition_results = evaluationResults.map(result => {
                    // TYPE-3는 모든 조건이 충족된 것으로 표시
                    if (type === 'TYPE-3') {
                        return {
                            id: result.id,
                            is_met: true,
                            is_na: result.notApplicable,
                            actual: result.notApplicable ? 'N/A' : result.value,
                            name: result.name,
                            threshold: result.threshold
                        };
                    }

                    // 지급된 경우: 적용 가능한 모든 조건을 충족한 것으로 표시
                    if (isPaid && !result.notApplicable) {
                        return {
                            id: result.id,
                            is_met: true,  // 지급되었으므로 충족
                            is_na: result.notApplicable,
                            actual: result.notApplicable ? 'N/A' : result.value,
                            name: result.name,
                            threshold: result.threshold
                        };
                    }

                    // 미지급된 경우: 실제 평가 결과 사용
                    return {
                        id: result.id,
                        is_met: result.met,
                        is_na: result.notApplicable,
                        actual: result.notApplicable ? 'N/A' : result.value,
                        name: result.name,
                        threshold: result.threshold
                    };
                });
            }

            // TYPE-3는 조건 없음
            if (type === 'TYPE-3') {
                emp.all_conditions_met = true;
            } else {
                // 실제 지급 여부를 기준으로 조건 충족 상태 설정
                emp.all_conditions_met = isPaid;
            }
        });

        // 기존 모달이 있으면 제거
        const existingModal = document.getElementById('employeeModal');
        if (existingModal) {
            existingModal.remove();
        }
        const existingBackdrop = document.querySelector('.modal-backdrop');
        if (existingBackdrop) {
            existingBackdrop.remove();
        }

        // 백드롭 먼저 추가 (모달 뒤에 위치하도록)
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.style.zIndex = '1040'; // 명시적 z-index 설정
        document.body.appendChild(backdrop);
        document.body.classList.add('modal-open');

        // 새 모달 생성
        const modalHTML = `
            <div class="modal fade show" id="employeeModal" tabindex="-1" style="display: block; z-index: 1050;" aria-modal="true" role="dialog">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title" id="modalTitle"></h5>
                            <button type="button" class="btn-close" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="modalBody" style="max-height: 70vh; overflow-y: auto;"></div>
                    </div>
                </div>
            </div>
        `;

        const modalDiv = document.createElement('div');
        modalDiv.innerHTML = modalHTML;
        document.body.appendChild(modalDiv.firstElementChild);

        // 모달 요소 참조
        const modal = document.getElementById('employeeModal');
        const modalBody = document.getElementById('modalBody');
        const modalTitle = document.getElementById('modalTitle');

        // 닫기 버튼 이벤트 추가
        const closeBtn = modal.querySelector('.btn-close');
        closeBtn.onclick = function(e) {
            e.stopPropagation();
            modal.remove();
            backdrop.remove();
            document.body.classList.remove('modal-open');
        };

        // 백드롭 클릭으로 닫기
        backdrop.onclick = function(e) {
            e.stopPropagation();
            modal.remove();
            backdrop.remove();
            document.body.classList.remove('modal-open');
        };

        // 모달 자체 클릭 시 닫히지 않도록 처리
        modal.onclick = function(e) {
            // 모달 다이얼로그 바깥 영역 클릭 시에만 닫기
            if (e.target === modal) {
                modal.remove();
                backdrop.remove();
                document.body.classList.remove('modal-open');
            }
        };

        // 모달 콘텐츠 클릭 시 이벤트 전파 중단
        modal.querySelector('.modal-content').onclick = function(e) {
            e.stopPropagation();
        };

        modalTitle.innerHTML = `${type} - ${position} ` + getTranslation('modal.modalTitle', currentLanguage);
        
        // 요약 통계 계산
        const totalEmployees = employees.length;
        const paidEmployees = employees.filter(e => getIncentiveAmount(e) > 0).length;
        const avgIncentive = Math.round(employees.reduce((sum, e) => sum + getIncentiveAmount(e), 0) / totalEmployees);
        const paidRate = Math.round(paidEmployees/totalEmployees*100);
        
        // 조건 ID를 번역 키로 매핑
        const conditionTranslationMap = {
            '1': 'modal.tenConditions.1',
            '2': 'modal.tenConditions.2',
            '3': 'modal.tenConditions.3',
            '4': 'modal.tenConditions.4',
            '5': 'modal.tenConditions.5',
            '6': 'modal.tenConditions.6',
            '7': 'modal.tenConditions.7',
            '8': 'modal.tenConditions.8',
            '9': 'modal.tenConditions.9',
            '10': 'modal.tenConditions.10'
        };
        
        // 실제 인센티브 기준으로 통계 계산 (Single Source of Truth)
        const actualPassCount = employees.filter(emp => getIncentiveAmount(emp) > 0).length;
        const actualFailCount = employees.filter(emp => getIncentiveAmount(emp) === 0).length;
        const paidEmployees = actualPassCount;  // 실제 지급된 인원수 일치시키기

        // 각 직원의 조건 충족 통계 계산 (실제 지급 상태 기반)
        const conditionStats = {};

        // 먼저 기본 조건 구조를 정의 (TYPE별로 다른 조건 적용)
        // position_condition_matrix.json에 따른 정확한 조건 매핑

        // TYPE-1의 경우 position에 따라 세분화된 조건 적용
        let applicableConditions = [];

        if (type === 'TYPE-1') {
            // TYPE-1 직급별 세분화된 조건 매핑
            const positionUpper = position.toUpperCase();

            if (positionUpper.includes('(V) SUPERVISOR') || positionUpper.includes('V.SUPERVISOR') || positionUpper.includes('V SUPERVISOR')) {
                applicableConditions = [1, 2, 3, 4];  // 출근 조건만
            } else if (positionUpper.includes('GROUP LEADER')) {
                applicableConditions = [1, 2, 3, 4];  // 출근 조건만
            } else if (positionUpper.includes('LINE LEADER')) {
                applicableConditions = [1, 2, 3, 4, 7];  // 출근 + 팀/구역 AQL
            } else if (positionUpper.includes('AQL INSPECTOR') || positionUpper.includes('AQL') || positionUpper.includes('CFA CERTIFIED')) {
                applicableConditions = [1, 2, 3, 4, 5];  // 출근 + 당월 AQL
            } else if (positionUpper.includes('ASSEMBLY INSPECTOR')) {
                applicableConditions = [1, 2, 3, 4, 5, 6, 9, 10];  // 출근 + 개인 AQL + 5PRS
            } else if (positionUpper.includes('AUDIT & TRAINING') || positionUpper.includes('AUDITOR') || positionUpper.includes('TRAINER')) {
                applicableConditions = [1, 2, 3, 4, 7, 8];  // 출근 + 팀/구역 AQL + 담당구역 reject
            } else if (positionUpper.includes('MODEL MASTER') || positionUpper.includes('SAMPLE')) {
                applicableConditions = [1, 2, 3, 4, 8];  // 출근 + 담당구역 reject
            } else {
                // 기본 TYPE-1 (매칭되지 않는 경우 모든 조건)
                applicableConditions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
            }
        } else if (type === 'TYPE-2') {
            applicableConditions = [1, 2, 3, 4];  // TYPE-2는 출근 조건만
        } else if (type === 'TYPE-3') {
            applicableConditions = [];  // TYPE-3는 조건 없음
        }
        applicableConditions.forEach(condId => {
            const translationKey = conditionTranslationMap[String(condId)];
            const translatedName = translationKey ? getTranslation(translationKey, currentLanguage) : `Condition ${condId}`;
            conditionStats[condId] = {
                name: translatedName,
                met: 0,
                total: 0,
                na_count: 0
            };
        });

        // 직원별 조건 평가 결과 계산
        console.log('Evaluating conditions for', employees.length, 'employees of type', type);
        console.log('Applicable conditions for', type, ':', applicableConditions);
        if (employees.length > 0) {
            console.log('First employee data sample:', employees[0]);
            console.log('Available fields:', Object.keys(employees[0]));
            // Check specific fields for debugging
            console.log('Sample field values:', {
                attendance_rate: employees[0]['attendance_rate'],
                'Attendance Rate': employees[0]['Attendance Rate'],
                unapproved_absences: employees[0]['unapproved_absences'],
                'Unapproved Absences': employees[0]['Unapproved Absences'],
                actual_working_days: employees[0]['actual_working_days'],
                'Actual Working Days': employees[0]['Actual Working Days'],
                condition_results: employees[0]['condition_results']
            });
        }

        // 모든 직원에 대해 조건 평가
        employees.forEach(emp => {
            // 실제 지급 여부 확인
            const actualIncentive = getIncentiveAmount(emp);
            const isPaid = actualIncentive > 0;

            // 조건 결과가 배열로 저장되어 있는지 확인
            if (emp.condition_results && Array.isArray(emp.condition_results) && emp.condition_results.length > 0) {
                console.log('Found condition_results for employee', emp.emp_no, 'isPaid:', isPaid);
                emp.condition_results.forEach(cond => {
                    const condId = parseInt(cond.id);
                    if (!isNaN(condId) && conditionStats[condId]) {
                        if (cond.is_na || cond.actual === 'N/A') {
                            conditionStats[condId].na_count++;
                        } else {
                            conditionStats[condId].total++;
                            // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                            if (isPaid || cond.is_met) {
                                conditionStats[condId].met++;
                            }
                        }
                    }
                });
            } else {
                // condition_results가 없는 경우 - 각 조건별로 개별 평가
                applicableConditions.forEach(condId => {

                    // 조건별 개별 평가 - 실제 필드명 사용
                    switch(condId) {
                        case 1: // 출근율 ≥88% (TYPE-1) 또는 ≥96% (TYPE-2)
                            const attendanceThreshold = type === 'TYPE-1' ? 88 : 96;
                            // 다양한 필드명 시도 - Excel에서 실제 사용하는 필드명들
                            const attendanceField = emp['attendance_rate'] || emp['Attendance Rate'] || emp['attendance_rate_%'] || emp['출근율'];
                            if (attendanceField !== undefined && attendanceField !== '' && attendanceField !== null) {
                                conditionStats[1].total++;
                                const rate = parseFloat(String(attendanceField).replace('%', ''));
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || rate >= attendanceThreshold) {
                                    conditionStats[1].met++;
                                }
                            } else {
                                conditionStats[1].na_count++;
                            }
                            break;

                        case 2: // 무단결근 2일 이하
                            const absenceField = emp['Unapproved Absences'] || emp['unapproved_absences'] || emp['unexcused_absence'] || emp['무단결근'];
                            if (absenceField !== undefined && absenceField !== '' && absenceField !== null) {
                                conditionStats[2].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || parseInt(absenceField) <= 2) {
                                    conditionStats[2].met++;
                                }
                            } else {
                                conditionStats[2].na_count++;
                            }
                            break;

                        case 3: // 실제근무일 0일 초과
                            const workdaysField = emp['Actual Working Days'] || emp['actual_working_days'] || emp['worked_days'] || emp['실제근무일수'];
                            if (workdaysField !== undefined && workdaysField !== '' && workdaysField !== null) {
                                conditionStats[3].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || parseInt(workdaysField) > 0) {
                                    conditionStats[3].met++;
                                }
                            } else {
                                conditionStats[3].na_count++;
                            }
                            break;

                        case 4: // 최소 근무일: 전체 근무일의 절반 이상
                            const actualDaysField = emp['Actual Working Days'] || emp['actual_working_days'] || emp['worked_days'];
                            const totalDaysField = emp['Total Working Days'] || emp['total_working_days'] || 13; // 기본값 13
                            if (actualDaysField !== undefined && actualDaysField !== '' && actualDaysField !== null) {
                                conditionStats[4].total++;
                                const actualDays = parseInt(actualDaysField);
                                const totalDays = parseInt(totalDaysField);
                                const minRequired = Math.ceil(totalDays / 2);
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || actualDays >= minRequired) {
                                    conditionStats[4].met++;
                                }
                            } else {
                                conditionStats[4].na_count++;
                            }
                            break;

                        case 5: // 개인AQL: 당월실패 0건
                            // Use September AQL Failures column or condition result
                            const aqlFailures = emp['September AQL Failures'] || emp[`${dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1)} AQL Failures`];
                            const condResult = emp['cond_5_aql_personal_failure'];

                            if (condResult !== undefined && condResult !== '' && condResult !== null && condResult !== 'N/A') {
                                conditionStats[5].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || condResult === 'PASS') {
                                    conditionStats[5].met++;
                                }
                            } else if (aqlFailures !== undefined && aqlFailures !== '' && aqlFailures !== null) {
                                conditionStats[5].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || aqlFailures === 0 || aqlFailures === '0') {
                                    conditionStats[5].met++;
                                }
                            } else {
                                conditionStats[5].na_count++;
                            }
                            break;

                        case 6: // 연속선 체크: 3개월 연속 실패 없음
                            const condResult6 = emp['cond_6_aql_continuous'];
                            const consecutiveFailField = emp['AQL_3months_fail'] || emp['consecutive_aql_fail'] || emp['연속AQL실패'];

                            if (condResult6 !== undefined && condResult6 !== '' && condResult6 !== null && condResult6 !== 'N/A') {
                                conditionStats[6].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || condResult6 === 'PASS') {
                                    conditionStats[6].met++;
                                }
                            } else if (consecutiveFailField !== undefined && consecutiveFailField !== null) {
                                conditionStats[6].total++;
                                // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                if (isPaid || (consecutiveFailField !== 'Y' && consecutiveFailField !== true && consecutiveFailField !== '있음')) {
                                    conditionStats[6].met++;
                                }
                            } else {
                                conditionStats[6].na_count++;
                            }
                            break;

                        case 7: // 팀/구역 AQL: 3개월 연속 실패 없음
                            // TYPE-1에만 적용되는 조건
                            if (type === 'TYPE-1') {
                                const teamAqlField = emp['team_aql_fail'] || emp['Team AQL'] || emp['팀AQL'];
                                if (teamAqlField !== undefined && teamAqlField !== null) {
                                    conditionStats[7].total++;
                                    // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                    if (isPaid || (teamAqlField !== 'Y' && teamAqlField !== true && teamAqlField !== '실패')) {
                                        conditionStats[7].met++;
                                    }
                                } else {
                                    // TYPE-1은 팀 조건 자동 충족
                                    conditionStats[7].total++;
                                    conditionStats[7].met++;
                                }
                            }
                            break;

                        case 8: // 담당구역 reject % < 3%
                            // TYPE-1에만 적용 (TYPE-2는 조건 1-4만 적용됨)
                            if (type === 'TYPE-1') {
                                const rejectField = emp['Area_Reject_Rate'] || emp['area_reject_rate'] || emp['reject_rate'] || emp['reject_%'];
                                if (rejectField !== undefined && rejectField !== '' && rejectField !== null) {
                                    conditionStats[8].total++;
                                    const rejectRate = parseFloat(String(rejectField).replace('%', ''));
                                    // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                    if (isPaid || rejectRate < 3) {
                                        conditionStats[8].met++;
                                    }
                                } else {
                                    conditionStats[8].na_count++;
                                }
                            }
                            break;

                        case 9: // 5PRS 통과율 95% 이상
                            if (type === 'TYPE-1') {
                                const prsScoreField = emp['5PRS_Pass_Rate'] || emp['Average 5PRS score'] || emp['5PRS score'] || emp['5prs_score'] || emp['5PRS점수'];
                                if (prsScoreField !== undefined && prsScoreField !== '' && prsScoreField !== null) {
                                    conditionStats[9].total++;
                                    const score = parseFloat(String(prsScoreField).replace('%', ''));
                                    // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                    if (isPaid || score >= 95) {
                                        conditionStats[9].met++;
                                    }
                                } else {
                                    conditionStats[9].na_count++;
                                }
                            }
                            break;

                        case 10: // 5PRS 검사량 100족 이상
                            if (type === 'TYPE-1') {
                                const prsVolumeField = emp['5PRS_Inspection_Qty'] || emp['5PRS_volume'] || emp['5prs_volume'] || emp['5PRS검사량'];
                                if (prsVolumeField !== undefined && prsVolumeField !== '' && prsVolumeField !== null) {
                                    conditionStats[10].total++;
                                    // 지급된 경우 모든 적용 가능한 조건을 충족한 것으로 처리
                                    if (isPaid || parseInt(prsVolumeField) >= 100) {
                                        conditionStats[10].met++;
                                    }
                                } else {
                                    // 데이터가 없으면 충족으로 간주 (TYPE-1 특별 처리)
                                    conditionStats[10].total++;
                                    conditionStats[10].met++;
                                }
                            }
                            break;
                    }
                });
            }
        });

        console.log('Final conditionStats:', conditionStats);
        
        // 인센티브 통계 계산
        const incentiveAmounts = employees.map(emp => getIncentiveAmount(emp)).filter(amt => amt > 0);
        const maxIncentive = incentiveAmounts.length > 0 ? Math.max(...incentiveAmounts) : 0;
        const minIncentive = incentiveAmounts.length > 0 ? Math.min(...incentiveAmounts) : 0;
        const medianIncentive = incentiveAmounts.length > 0 ?
            incentiveAmounts.sort((a, b) => a - b)[Math.floor(incentiveAmounts.length / 2)] : 0;
        
        let modalContent = `
            <div style="display: grid; grid-template-columns: 1fr; gap: 20px; padding: 20px;">
                <!-- 인센티브 통계 (1행 4열 배치) -->
                <div>
                    <h6 style="color: #666; margin-bottom: 15px;">📊 ${getTranslation('modal.incentiveStats', currentLanguage)}</h6>
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px;">
                            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                <div style="color: #666; font-size: 0.85rem;">${getTranslation('modal.totalPersonnel', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #333;">${totalEmployees}${getTranslation('common.people', currentLanguage)}</div>
                            </div>
                            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                <div style="color: #666; font-size: 0.85rem;">${getTranslation('modal.paidPersonnel', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">${actualPassCount}${getTranslation('common.people', currentLanguage)}</div>
                            </div>
                            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                <div style="color: #666; font-size: 0.85rem;">${getTranslation('modal.unpaidPersonnel', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #dc3545;">${totalEmployees - paidEmployees}${getTranslation('common.people', currentLanguage)}</div>
                            </div>
                            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                <div style="color: #666; font-size: 0.85rem;">${getTranslation('modal.paymentRate', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #007bff;">${paidRate}%</div>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px;">
                                <div>
                                    <div style="color: #666; font-size: 0.8rem;">${getTranslation('modal.avgIncentive', currentLanguage)}</div>
                                    <div style="font-weight: bold;">${avgIncentive.toLocaleString()} VND</div>
                                </div>
                                <div>
                                    <div style="color: #666; font-size: 0.8rem;">${getTranslation('modal.maxIncentive', currentLanguage)}</div>
                                    <div style="font-weight: bold;">${maxIncentive.toLocaleString()} VND</div>
                                </div>
                                <div>
                                    <div style="color: #666; font-size: 0.8rem;">${getTranslation('modal.minIncentive', currentLanguage)}</div>
                                    <div style="font-weight: bold;">${minIncentive.toLocaleString()} VND</div>
                                </div>
                                <div>
                                    <div style="color: #666; font-size: 0.8rem;">${getTranslation('modal.median', currentLanguage)}</div>
                                    <div style="font-weight: bold;">${medianIncentive.toLocaleString()} VND</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 인센티브 수령 상세 및 조건별 통계 -->
                <div style="margin-bottom: 20px;">
                    <h6 style="color: #666; margin-bottom: 10px;">📋 ${getTranslation('modal.incentiveReceiptStatus.title', currentLanguage)}</h6>
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div style="padding: 10px; background: #d4edda; border-radius: 5px; border-left: 4px solid #28a745;">
                                <div style="color: #155724; font-size: 0.85rem;">${getTranslation('modal.incentiveReceiptStatus.received', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #155724;">${actualPassCount}${getTranslation('common.people', currentLanguage)}</div>
                            </div>
                            <div style="padding: 10px; background: #f8d7da; border-radius: 5px; border-left: 4px solid #dc3545;">
                                <div style="color: #721c24; font-size: 0.85rem;">${getTranslation('modal.incentiveReceiptStatus.notReceived', currentLanguage)}</div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #721c24;">${actualFailCount}${getTranslation('common.people', currentLanguage)}</div>
                            </div>
                        </div>
                    </div>
                    <h6 style="color: #666; margin-bottom: 10px;">📊 ${getTranslation('modal.incentiveReceiptStatus.conditionsByReference', currentLanguage)}</h6>
                    <div style="overflow-x: auto;">
                        <table class="table table-sm" style="font-size: 0.9rem;">
                            <thead style="background: #f8f9fa;">
                                <tr>
                                    <th width="5%">#</th>
                                    <th width="40%">${getTranslation('modal.condition', currentLanguage)}</th>
                                    <th width="20%">${getTranslation('modal.evaluationTarget', currentLanguage)}</th>
                                    <th width="15%">${getTranslation('modal.fulfilled', currentLanguage)}</th>
                                    <th width="15%">${getTranslation('modal.notFulfilled', currentLanguage)}</th>
                                    <th width="15%">${getTranslation('modal.fulfillmentRate', currentLanguage)}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(conditionStats).map(([id, stat], index) => {
                                    const isNA = stat.na_count > 0 && stat.total === 0;  // 모든 직원이 N/A인 경우
                                    const rate = stat.total > 0 ? Math.round((stat.met / stat.total) * 100) : 0;
                                    const unmet = stat.total - stat.met;
                                    const evaluatedCount = stat.total;  // N/A가 아닌 평가 대상자 수
                                    
                                    return `
                                    <tr>
                                        <td style="color: ${isNA ? '#999' : '#000'};">${index + 1}</td>
                                        <td style="color: ${isNA ? '#999' : '#000'};">${stat.name}</td>
                                        <td>${isNA ? `<span style="color: #999;">N/A</span>` : `${evaluatedCount}${getTranslation('common.people', currentLanguage)}`}</td>
                                        <td style="color: ${isNA ? '#999' : '#28a745'}; font-weight: bold;">
                                            ${isNA ? 'N/A' : `${stat.met}${getTranslation('common.people', currentLanguage)}`}
                                        </td>
                                        <td style="color: ${isNA ? '#999' : '#dc3545'};">
                                            ${isNA ? 'N/A' : `${unmet}${getTranslation('common.people', currentLanguage)}`}
                                        </td>
                                        <td>
                                            ${isNA ? `<span style="color: #999;">N/A</span>` : `
                                            <div style="display: flex; align-items: center; gap: 5px;">
                                                <div style="background: #e9ecef; height: 8px; width: 60px; border-radius: 4px; overflow: hidden;">
                                                    <div style="background: #28a745; height: 100%; width: ${rate}%;"></div>
                                                </div>
                                                <span style="font-weight: bold;">${rate}%</span>
                                            </div>
                                            `}
                                        </td>
                                    </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 직원별 상세 현황 -->
                <div>
                    <h6 style="color: #666; margin-bottom: 10px;">${getTranslation('modal.employeeDetails', currentLanguage)}</h6>
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <button class="btn btn-sm btn-outline-primary" onclick="filterPositionTable('all')">${getTranslation('modal.all', currentLanguage)}</button>
                        <button class="btn btn-sm btn-outline-success" onclick="filterPositionTable('paid')">${getTranslation('modal.paidOnly', currentLanguage)}</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="filterPositionTable('unpaid')">${getTranslation('modal.unpaidOnly', currentLanguage)}</button>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="table table-sm" id="positionEmployeeTable" style="font-size: 0.9rem;">
                            <thead style="background: #f8f9fa;">
                                <tr>
                                    <th>${getTranslation('modal.tableHeaders.employeeNo', currentLanguage)}</th>
                                    <th>${getTranslation('modal.tableHeaders.name', currentLanguage)}</th>
                                    <th>${getTranslation('modal.tableHeaders.incentive', currentLanguage)}</th>
                                    <th>${getTranslation('modal.tableHeaders.status', currentLanguage)}</th>
                                    <th>${getTranslation('modal.tableHeaders.conditionFulfillment', currentLanguage)}</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        employees.forEach(emp => {
            // Use helper function to get incentive amount
            const amount = getIncentiveAmount(emp);
            const isPaid = amount > 0;
            modalContent += `
                <tr class="employee-row ${isPaid ? 'paid-row' : 'unpaid-row'}" data-emp-no="${emp.emp_no}" style="cursor: pointer;">
                    <td>${emp.emp_no}</td>
                    <td>${emp.name}</td>
                    <td><strong style="color: ${isPaid ? '#28a745' : '#dc3545'};">${amount.toLocaleString()} VND</strong></td>
                    <td>
                        <span class="badge ${isPaid ? 'bg-success' : 'bg-danger'}">
                            ${isPaid ? getTranslation('modal.paymentStatus.paid', currentLanguage) : getTranslation('modal.paymentStatus.unpaid', currentLanguage)}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                            ${(() => {
                                let badges = [];

                                if (emp.condition_results && emp.condition_results.length > 0) {
                                    // condition_results가 있는 경우 - 원래 로직 사용
                                    // 카테고리별로 조건 그룹화 (id 기준으로 필터링)
                                    const attendance = emp.condition_results.filter(c => c.id >= 1 && c.id <= 4); // 조건 1-4: 출근
                                    const aql = emp.condition_results.filter(c => c.id >= 5 && c.id <= 8); // 조건 5-8: AQL
                                    const prs = emp.condition_results.filter(c => c.id >= 9 && c.id <= 10); // 조건 9-10: 5PRS

                                    // 출근 카테고리 평가
                                    if (attendance.length > 0) {
                                        const attendanceNA = attendance.every(c => c.is_na || c.actual === 'N/A');
                                        const applicableAttendance = attendance.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const attendanceMet = applicableAttendance.length > 0 && applicableAttendance.every(c => c.is_met);
                                        if (attendanceNA) {
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ': N/A</span>');
                                        } else if (attendanceMet) {
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✓</span>');
                                        } else {
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✗</span>');
                                        }
                                    }

                                    // AQL 카테고리 평가
                                    if (aql.length > 0) {
                                        const aqlNA = aql.every(c => c.is_na || c.actual === 'N/A');
                                        const applicableAql = aql.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const aqlMet = applicableAql.length > 0 && applicableAql.every(c => c.is_met);
                                        if (aqlNA) {
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ': N/A</span>');
                                        } else if (aqlMet) {
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✓</span>');
                                        } else {
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✗</span>');
                                        }
                                    }

                                    // 5PRS 카테고리 평가
                                    if (prs.length > 0) {
                                        const prsNA = prs.every(c => c.is_na || c.actual === 'N/A');
                                        const applicablePrs = prs.filter(c => !c.is_na && c.actual !== 'N/A');
                                        const prsMet = applicablePrs.length > 0 && applicablePrs.every(c => c.is_met);
                                        if (prsNA) {
                                            badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ': N/A</span>');
                                        } else if (prsMet) {
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✓</span>');
                                        } else {
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✗</span>');
                                        }
                                    }
                                } else {
                                    // condition_results가 없는 경우 - 개별 필드에서 직접 평가
                                    // 출근율 체크 - 다양한 필드명 지원
                                    const attendanceField = emp['attendance_rate_%'] || emp['attendance_rate'] || emp['Attendance rate'] || emp['출근율'];
                                    if (attendanceField !== undefined && attendanceField !== '' && attendanceField !== null) {
                                        const attendanceRate = parseFloat(String(attendanceField).replace('%', ''));
                                        const threshold = type === 'TYPE-1' ? 88 : 96;
                                        if (attendanceRate >= threshold) {
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✓</span>');
                                        } else {
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ' ✗</span>');
                                        }
                                    } else {
                                        badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.attendance', currentLanguage) + ': N/A</span>');
                                    }

                                    // AQL 체크 - 실제 데이터 필드 사용
                                    const aqlFailures = emp['September AQL Failures'] || emp[`${dashboardMonth.charAt(0).toUpperCase() + dashboardMonth.slice(1)} AQL Failures`];
                                    const aqlCondition = emp['cond_5_aql_personal_failure'];

                                    if (aqlCondition === 'PASS' || (aqlFailures !== undefined && (aqlFailures === 0 || aqlFailures === '0'))) {
                                        badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✓</span>');
                                    } else if (aqlCondition === 'FAIL' || (aqlFailures !== undefined && aqlFailures > 0)) {
                                        badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ' ✗</span>');
                                    } else {
                                        badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.aql', currentLanguage) + ': N/A</span>');
                                    }

                                    // 5PRS 체크 - TYPE별로 다른 기준 적용
                                    const prsScoreField = emp['5PRS_Pass_Rate'] || emp['Average 5PRS score'] || emp['5PRS score'] || emp['5prs_score'] || emp['5PRS점수'];
                                    if (prsScoreField !== undefined && prsScoreField !== '' && prsScoreField !== null) {
                                        const prsScore = parseFloat(String(prsScoreField).replace('%', ''));
                                        const prsThreshold = type === 'TYPE-1' ? 95 : 85;
                                        if (prsScore >= prsThreshold) {
                                            badges.push('<span class="badge bg-success">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✓</span>');
                                        } else {
                                            badges.push('<span class="badge bg-danger">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ' ✗</span>');
                                        }
                                    } else {
                                        badges.push('<span class="badge" style="background-color: #999;">' + getTranslation('modal.conditionCategories.prs', currentLanguage) + ': N/A</span>');
                                    }
                                }

                                return badges.join('');
                            })()
                            }
                        </div>
                    </td>
                </tr>
            `;
        });
        
        modalContent += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        modalBody.innerHTML = modalContent;
        // modal.style.display = 'block'; // 이미 show 클래스로 표시됨

        // 모달 스크롤 초기화 (맨 위로)
        modalBody.scrollTop = 0;
        document.querySelector('.modal-content').scrollTop = 0;
        
        // Event delegation을 사용하여 직원 행 클릭 이벤트 처리
        setTimeout(() => {
            const table = document.getElementById('positionEmployeeTable');
            if (!table) {
                console.error('Position employee table not found');
                return;
            }
            
            // 이전 이벤트 리스너 제거 (중복 방지)
            if (window.positionTableClickHandler) {
                table.removeEventListener('click', window.positionTableClickHandler);
            }
            
            // 새로운 이벤트 핸들러 생성 및 저장
            window.positionTableClickHandler = function(event) {
                // tbody 내의 tr을 찾기
                const row = event.target.closest('tbody tr.employee-row');
                if (!row) return;
                
                // data-emp-no 속성에서 직원번호 가져오기
                const empNo = row.getAttribute('data-emp-no');
                console.log('Employee row clicked, empNo:', empNo);
                
                if (empNo) {
                    showEmployeeDetailFromPosition(empNo);
                }
            };
            
            // 테이블에 이벤트 리스너 추가
            table.addEventListener('click', window.positionTableClickHandler);
            console.log('Event delegation set up for employee table');
        }, 100);
        
        // 차트 그리기
        setTimeout(() => {
            const chartId = `positionChart${type.replace('-', '')}${position.replace(/[\\s()]/g, '')}`;
            const canvas = document.getElementById(chartId);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                
                // 기존 차트 삭제
                if (window[`chart_$null`]) {
                    window[`chart_$null`].destroy();
                }
                
                // 새 차트 생성
                window[`chart_$null`] = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['지급', '미지급'],
                        datasets: [{
                            data: [paidEmployees, totalEmployees - paidEmployees],
                            backgroundColor: ['#28a745', '#dc3545'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: false,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        cutout: '70%'
                    }
                });
            }
        }, 100);
    }
    
    // 직급별 테이블 필터링
    function filterPositionTable(filter) {
        const rows = document.querySelectorAll('#positionEmployeeTable tbody tr');
        rows.forEach(row => {
            if (filter === 'all') {
                row.style.display = '';
            } else if (filter === 'paid' && row.classList.contains('paid-row')) {
                row.style.display = '';
            } else if (filter === 'unpaid' && row.classList.contains('unpaid-row')) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // 직급별 상세 팝업에서 호출하는 개인별 상세 팝업 함수
    function showEmployeeDetailFromPosition(empNo) {
        console.log('showEmployeeDetailFromPosition called with empNo:', empNo);
        
        try {
            // 먼저 직급별 상세 팝업을 닫기
            const positionModal = document.getElementById('positionModal');
            console.log('Position modal element:', positionModal);
            
            if (positionModal) {
                const bsPositionModal = bootstrap.Modal.getInstance(positionModal);
                console.log('Position modal instance:', bsPositionModal);
                
                if (bsPositionModal) {
                    bsPositionModal.hide();
                }
            }
            
            // 잠시 후에 개인별 상세 팝업 열기 (애니메이션 충돌 방지)
            setTimeout(() => {
                console.log('Opening employee detail modal for:', empNo);
                showEmployeeDetail(empNo);
            }, 300);
        } catch (error) {
            console.error('Error in showEmployeeDetailFromPosition:', error);
            // 오류가 있어도 개인별 상세 팝업은 열려야 함
            showEmployeeDetail(empNo);
        }
    }
    
    // 직원 상세 정보 표시 (Employee Details Status 모달 사용)
    function showEmployeeDetail(empNo) {
        // 새로운 Employee Details Status 모달을 사용
        showEmployeeDetailModal(empNo);
        return;

        // 아래는 기존 코드 (사용하지 않음)
        const emp = employeeData.find(e => e.emp_no === empNo);
        if (!emp) return;

        const modal = document.getElementById('employeeModal');
        const modalBody = document.getElementById('modalBody');
        const modalTitle = document.getElementById('modalTitle');

        modalTitle.textContent = `${emp.name} (${emp.emp_no}) - ${getTranslation('modal.title')}`;

        // 조건 충족 통계 계산 - N/A 제외
        const conditions = emp.condition_results || [];
        const applicableConditions = conditions.filter(c => !c.is_na && c.actual !== 'N/A');
        const passedConditions = applicableConditions.filter(c => c.is_met).length;
        const totalConditions = applicableConditions.length;
        const passRate = totalConditions > 0 ? (passedConditions / totalConditions * 100).toFixed(0) : 0;

        modalBody.innerHTML = `
            <!-- 상단 통계 카드 -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-value">${emp.type}</div>
                        <div class="stat-label">${getTranslation('modal.basicInfo.type')}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-value">${emp.position}</div>
                        <div class="stat-label">${getTranslation('modal.basicInfo.position')}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-value">${parseInt(emp[dashboardMonth + '_incentive']).toLocaleString()} VND</div>
                        <div class="stat-label">${getTranslation('modal.incentiveInfo.amount')}</div>
                    </div>
                </div>
            </div>
            
            <!-- 차트와 조건 충족도 -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6 class="card-title">` + getTranslation('modal.detailPopup.conditionFulfillment', currentLanguage) + `</h6>
                            <div style="width: 200px; height: 200px; margin: 0 auto; position: relative;">
                                <canvas id="conditionChart$null"></canvas>
                            </div>
                            <div class="mt-3">
                                <h4>$null%</h4>
                                <p class="text-muted">${totalConditions > 0 ? passedConditions + ' / ' + totalConditions + ' ' + getTranslation('modal.detailPopup.conditionsFulfilled', currentLanguage) : getTranslation('modal.detailPopup.noConditions', currentLanguage)}</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">` + getTranslation('modal.detailPopup.paymentStatus', currentLanguage) + `</h6>
                            <div class="payment-status ${parseInt(emp[dashboardMonth + '_incentive']) > 0 ? 'paid' : 'unpaid'}">
                                ${parseInt(emp[dashboardMonth + '_incentive']) > 0 ? `
                                <div>
                                    <i class="fas fa-check-circle"></i>
                                    <h5>` + getTranslation('modal.payment.paid', currentLanguage) + `</h5>
                                    <p class="mb-1">${parseInt(emp[dashboardMonth + '_incentive']).toLocaleString()} VND</p>
                                    ${emp.Talent_Pool_Member === 'Y' ? `
                                    <div style="background: linear-gradient(135deg, #FFD700, #FFA500); padding: 8px; border-radius: 8px; margin-top: 10px;">
                                        <small style="color: white; font-weight: bold;">
                                            🌟 Talent Pool 보너스 포함<br>
                                            기본: ${(parseInt(emp[dashboardMonth + '_incentive']) - parseInt(emp.Talent_Pool_Bonus || 0)).toLocaleString()} VND<br>
                                            보너스: +${parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()} VND
                                        </small>
                                    </div>` : ''}
                                </div>` : `
                                <div>
                                    <i class="fas fa-times-circle"></i>
                                    <h5>` + getTranslation('status.unpaid', currentLanguage) + `</h5>
                                    <p>` + getTranslation('modal.detailPopup.conditionNotMet', currentLanguage) + `</p>
                                </div>`}
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">` + getTranslation('modal.detailPopup.lastMonthIncentive', currentLanguage) + `: ${parseInt(emp.july_incentive).toLocaleString()} VND</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 조건 충족 상세 테이블 -->
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">` + getTranslation('modal.detailPopup.conditionDetails', currentLanguage) + `</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th width="5%">#</th>
                                    <th width="50%">` + getTranslation('modal.detailPopup.condition', currentLanguage) + `</th>
                                    <th width="25%">` + getTranslation('modal.detailPopup.performance', currentLanguage) + `</th>
                                    <th width="20%">` + getTranslation('modal.detailPopup.result', currentLanguage) + `</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${conditions.map((cond, idx) => {
                                    const isNA = cond.is_na || cond.actual === 'N/A';
                                    let rowClass = '';
                                    let badgeHtml = '';
                                    let actualHtml = '';
                                    
                                    if (isNA) {
                                        actualHtml = '<span style="color: #999;">N/A</span>';
                                        badgeHtml = '<span class="badge" style="background-color: #999;">N/A</span>';
                                    } else {
                                        rowClass = cond.is_met ? 'table-success' : 'table-danger';
                                        
                                        // 실적 값의 단위 번역 처리
                                        let actualValue = cond.actual;
                                        if (actualValue && typeof actualValue === 'string') {
                                            // Placeholder 번역 처리
                                            actualValue = actualValue.replace('[PASS]', getTranslation('modal.conditions.pass', currentLanguage));
                                            actualValue = actualValue.replace('[FAIL]', getTranslation('modal.conditions.fail', currentLanguage));
                                            actualValue = actualValue.replace('[CONSECUTIVE_FAIL]', getTranslation('modal.conditions.consecutiveFail', currentLanguage));

                                            // "0일" -> "0 days" / "0 ngày"
                                            actualValue = actualValue.replace(/(\\d+)일/g, function(match, num) {
                                                const dayUnit = parseInt(num) <= 1 ? getTranslation('common.day', currentLanguage) : getTranslation('common.days', currentLanguage);
                                                return num + (currentLanguage === 'ko' ? dayUnit : ' ' + dayUnit);
                                            });
                                            // "0건" -> "0 cases" / "0 trường hợp"
                                            actualValue = actualValue.replace(/(\\d+)건/g, function(match, num) {
                                                if (currentLanguage === 'en') return num + (parseInt(num) <= 1 ? ' case' : ' cases');
                                                if (currentLanguage === 'vi') return num + ' trường hợp';
                                                return match;
                                            });
                                            // "0족" -> "0 pairs" / "0 đôi"
                                            actualValue = actualValue.replace(/(\\d+)족/g, function(match, num) {
                                                if (currentLanguage === 'en') return num + (parseInt(num) <= 1 ? ' pair' : ' pairs');
                                                if (currentLanguage === 'vi') return num + ' đôi';
                                                return match;
                                            });
                                        }
                                        
                                        actualHtml = `<strong>$null</strong>`;
                                        badgeHtml = cond.is_met ? '<span class="badge bg-success">' + getTranslation('modal.conditions.met', currentLanguage) + '</span>' : '<span class="badge bg-danger">' + getTranslation('modal.conditions.notMet', currentLanguage) + '</span>';
                                    }
                                    
                                    // 조건 이름 번역
                                    let condName = cond.name;
                                    if (cond.id && cond.id >= 1 && cond.id <= 10) {
                                        condName = getTranslation('modal.tenConditions.' + cond.id, currentLanguage);
                                    }
                                    
                                    return `
                                    <tr class="$null">
                                        <td>${idx + 1}</td>
                                        <td>$null</td>
                                        <td>$null</td>
                                        <td class="text-center">$null</td>
                                    </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
        
        // 모달 스크롤 초기화 (맨 위로)
        modalBody.scrollTop = 0;
        document.querySelector('.modal-content').scrollTop = 0;
        
        // 차트 그리기
        setTimeout(() => {
            const canvas = document.getElementById(`conditionChart$null`);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                
                // 기존 차트 삭제
                if (window[`chart_$null`]) {
                    window[`chart_$null`].destroy();
                }
                
                // 새 차트 생성
                window[`chart_$null`] = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: [getTranslation('modal.conditions.met', currentLanguage), getTranslation('modal.conditions.notMet', currentLanguage)],
                        datasets: [{
                            data: [passedConditions, Math.max(0, totalConditions - passedConditions)],
                            backgroundColor: ['#28a745', '#dc3545'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        }, 100);
    }
    
    // 모달 닫기
    function closeModal() {
        // 모든 차트 정리
        Object.keys(window).forEach(key => {
            if (key.startsWith('chart_') && window[key]) {
                window[key].destroy();
                delete window[key];
            }
        });
        document.getElementById('employeeModal').style.display = 'none';
    }
    
    // 모달 외부 클릭 시 닫기
    window.onclick = function(event) {
        const modal = document.getElementById('employeeModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
    
    // 테이블 필터링
    function filterTable() {
        const searchInput = document.getElementById('searchInput').value.toLowerCase();
        const typeFilter = document.getElementById('typeFilter').value;
        const positionFilter = document.getElementById('positionFilter').value;
        const paymentFilter = document.getElementById('paymentFilter').value;
        
        const tbody = document.getElementById('employeeTableBody');
        tbody.innerHTML = '';
        
        employeeData.forEach(emp => {
            const amount = getIncentiveAmount(emp);
            const isPaid = amount > 0;
            
            // 필터 조건 확인
            if (searchInput && !emp.name.toLowerCase().includes(searchInput) && !emp.emp_no.includes(searchInput)) {
                return;
            }
            if (typeFilter && emp.type !== typeFilter) {
                return;
            }
            if (positionFilter && emp.position !== positionFilter) {
                return;
            }
            if (paymentFilter === 'paid' && !isPaid) {
                return;
            }
            if (paymentFilter === 'unpaid' && isPaid) {
                return;
            }
            
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer';
            tr.onclick = () => showEmployeeDetail(emp.emp_no);
            
            // Talent Pool 멤버인 경우 특별 스타일 적용
            if (emp.Talent_Pool_Member === 'Y') {
                tr.className = 'talent-pool-row';
            }
            
            // Talent Pool 정보 HTML 생성
            let talentPoolHTML = '-';
            if (emp.Talent_Pool_Member === 'Y') {
                talentPoolHTML = `
                    <div class="talent-pool-tooltip">
                        <span class="talent-pool-star">🌟</span>
                        <strong>${parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()} VND</strong>
                        <span class="tooltiptext">
                            <strong>${getTranslation('talentPool.special', currentLanguage) || 'QIP Talent Pool'}</strong><br>
                            ${getTranslation('talentPool.monthlyBonus', currentLanguage) || '월 특별 보너스'}: ${parseInt(emp.Talent_Pool_Bonus || 0).toLocaleString()} VND<br>
                            ${getTranslation('talentPool.period', currentLanguage) || '지급 기간'}: 2025.07 - 2025.12
                        </span>
                    </div>
                `;
            }
            
            tr.innerHTML = `
                <td>${emp.emp_no}</td>
                <td>${emp.name}${emp.Talent_Pool_Member === 'Y' ? '<span class="talent-pool-badge">TALENT</span>' : ''}</td>
                <td>${emp.position}</td>
                <td><span class="type-badge type-${emp.type.toLowerCase().replace('type-', '')}">${emp.type}</span></td>
                <td>${parseInt(emp.july_incentive).toLocaleString()}</td>
                <td><strong>${amount.toLocaleString()}</strong></td>
                <td>$null</td>
                <td>${isPaid ? '✅ ' + getTranslation('status.paid') : '❌ ' + getTranslation('status.unpaid')}</td>
                <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetail('${emp.emp_no}')">${getTranslation('individual.table.detailButton')}</button></td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    // 직급 필터 업데이트
    function updatePositionFilter() {
        const typeFilter = document.getElementById('typeFilter').value;
        const positionSelect = document.getElementById('positionFilter');
        const currentValue = positionSelect.value;
        
        // 직급 목록 수집
        const positions = new Set();
        employeeData.forEach(emp => {
            if (!typeFilter || emp.type === typeFilter) {
                positions.add(emp.position);
            }
        });
        
        // 옵션 업데이트
        positionSelect.innerHTML = '<option value="" id="optAllPositionsInner">' + getTranslation('individual.filters.allPositions', currentLanguage) + '</option>';
        Array.from(positions).sort().forEach(position => {
            const option = document.createElement('option');
            option.value = position;
            option.textContent = position;
            if (position === currentValue) {
                option.selected = true;
            }
            positionSelect.appendChild(option);
        });
    }

    // ==================== Individual Details 탭 구현 ====================
    // Individual Details 테이블 생성 함수
    function renderIndividualDetailsTab() {
        const detailTable = document.getElementById('detailTable');
        if (!detailTable) return;

        // 이전 월 계산
        const currentMonth = parseInt(document.getElementById('mainSubtitle').dataset.month);
        const prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
        const prevMonthName = getMonthName(prevMonth, currentLanguage);
        const currentMonthName = getMonthName(currentMonth, currentLanguage);

        let tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover" id="employeeTable">
                    <thead class="table-light">
                        <tr>
                            <th id="empIdHeader">${getTranslation('individual.table.columns.employeeId', currentLanguage)}</th>
                            <th id="nameHeader">${getTranslation('individual.table.columns.name', currentLanguage)}</th>
                            <th id="positionHeader">${getTranslation('individual.table.columns.position', currentLanguage)}</th>
                            <th id="typeHeader">${getTranslation('individual.table.columns.type', currentLanguage)}</th>
                            <th id="prevMonthHeader">${prevMonthName}</th>
                            <th id="currentMonthHeader">${currentMonthName}</th>
                            <th id="talentPoolHeader">Talent Pool</th>
                            <th id="statusHeader">${getTranslation('individual.table.columns.status', currentLanguage)}</th>
                            <th id="detailsHeader">${getTranslation('individual.table.columns.details', currentLanguage)}</th>
                        </tr>
                    </thead>
                    <tbody id="employeeTableBody">
                    </tbody>
                </table>
            </div>
        `;

        detailTable.innerHTML = tableHTML;

        // 테이블 내용 채우기
        renderEmployeeTableRows();

        // 필터 이벤트 연결
        setupFilterEventListeners();

        // 초기 필터 업데이트
        updatePositionFilter();
    }

    // 직원 테이블 행 렌더링
    function renderEmployeeTableRows() {
        const tbody = document.getElementById('employeeTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        window.employeeData.forEach(emp => {
            const amount = getIncentiveAmount(emp);
            const isPaid = amount > 0;
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer';

            // 이전 월 인센티브 금액
            const prevMonthAmount = emp.july_incentive || emp.august_incentive || 0;

            // Talent Pool 표시
            let talentPoolHTML = '-';
            if (emp.Talent_Pool_Member === 'Y') {
                talentPoolHTML = `<span class="badge bg-warning">🌟 TALENT</span>`;
                tr.className = 'talent-pool-row';
            }

            tr.innerHTML = `
                <td>${emp.emp_no || emp['Employee No'] || ''}</td>
                <td>${emp.name || emp['Full Name'] || ''}${emp.Talent_Pool_Member === 'Y' ? ' <span class="badge bg-warning">★</span>' : ''}</td>
                <td>${emp.position || emp['FINAL QIP POSITION NAME CODE'] || ''}</td>
                <td><span class="badge bg-${emp.type === 'TYPE-1' ? 'primary' : emp.type === 'TYPE-2' ? 'success' : 'secondary'}">${emp.type}</span></td>
                <td>${Math.round(prevMonthAmount).toLocaleString()} VND</td>
                <td><strong>${Math.round(amount).toLocaleString()} VND</strong></td>
                <td>${talentPoolHTML}</td>
                <td>${isPaid ? '<span class="badge bg-success">지급</span>' : '<span class="badge bg-danger">미지급</span>'}</td>
                <td><button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); showEmployeeDetailModal('${emp.emp_no || emp['Employee No']}')">${getTranslation('individual.table.detailButton', currentLanguage)}</button></td>
            `;

            // 전체 행 클릭 시에도 상세 모달 표시
            tr.onclick = (e) => {
                if (e.target.tagName !== 'BUTTON') {
                    showEmployeeDetailModal(emp.emp_no || emp['Employee No']);
                }
            };

            tbody.appendChild(tr);
        });
    }

    // 필터 이벤트 리스너 설정
    function setupFilterEventListeners() {
        const searchInput = document.getElementById('searchInput');
        const typeFilter = document.getElementById('typeFilter');
        const positionFilter = document.getElementById('positionFilter');
        const paymentFilter = document.getElementById('paymentFilter');

        if (searchInput) {
            searchInput.addEventListener('keyup', filterEmployeeTable);
        }
        if (typeFilter) {
            typeFilter.addEventListener('change', () => {
                updatePositionFilter();
                filterEmployeeTable();
            });
        }
        if (positionFilter) {
            positionFilter.addEventListener('change', filterEmployeeTable);
        }
        if (paymentFilter) {
            paymentFilter.addEventListener('change', filterEmployeeTable);
        }
    }

    // 직원 테이블 필터링 (개선된 버전)
    function filterEmployeeTable() {
        const searchInput = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('typeFilter')?.value || '';
        const positionFilter = document.getElementById('positionFilter')?.value || '';
        const paymentFilter = document.getElementById('paymentFilter')?.value || '';

        const tbody = document.getElementById('employeeTableBody');
        if (!tbody) return;

        const rows = tbody.getElementsByTagName('tr');

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');

            const empNo = cells[0].textContent.toLowerCase();
            const name = cells[1].textContent.toLowerCase();
            const position = cells[2].textContent;
            const type = cells[3].textContent;
            const status = cells[7].textContent;

            let showRow = true;

            // 검색 필터
            if (searchInput && !empNo.includes(searchInput) && !name.includes(searchInput)) {
                showRow = false;
            }

            // TYPE 필터
            if (typeFilter && !type.includes(typeFilter)) {
                showRow = false;
            }

            // 직급 필터
            if (positionFilter && position !== positionFilter) {
                showRow = false;
            }

            // 지급 상태 필터
            if (paymentFilter) {
                const isPaid = status.includes('지급') && !status.includes('미지급');
                if (paymentFilter === 'paid' && !isPaid) {
                    showRow = false;
                } else if (paymentFilter === 'unpaid' && isPaid) {
                    showRow = false;
                }
            }

            row.style.display = showRow ? '' : 'none';
        }
    }

    // ==================== Employee Details Status 모달 ====================
    function showEmployeeDetailModal(empNo) {
        const employee = window.employeeData.find(emp =>
            (emp.emp_no || emp['Employee No']) === empNo
        );

        if (!employee) {
            console.error('Employee not found:', empNo);
            return;
        }

        // 기존 모달 제거
        const existingModal = document.getElementById('employeeDetailModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 모달 HTML 생성
        const modalHTML = createEmployeeDetailModalHTML(employee);

        // 모달을 body에 추가
        const modalDiv = document.createElement('div');
        modalDiv.innerHTML = modalHTML;
        document.body.appendChild(modalDiv);

        // Bootstrap 모달 초기화 및 표시
        const modal = new bootstrap.Modal(document.getElementById('employeeDetailModal'));
        modal.show();
    }

    // Employee Details 모달 HTML 생성
    function createEmployeeDetailModalHTML(employee) {
        const amount = getIncentiveAmount(employee);
        const isPaid = amount > 0;
        const type = employee.type || employee['ROLE TYPE STD'] || 'TYPE-1';
        const position = (employee.position || employee['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();

        // 조건 평가 결과 가져오기
        let conditionResults = evaluateEmployeeConditions(employee);

        // 지급된 경우: 모든 적용 가능한 조건을 충족한 것으로 표시 (Single Source of Truth)
        if (isPaid && type !== 'TYPE-3') {
            conditionResults = conditionResults.map(cond => {
                if (!cond.notApplicable) {
                    // 지급되었으므로 모든 적용 가능한 조건은 충족
                    return { ...cond, met: true };
                }
                return cond;
            });
        }

        // 조건별 상태 표시
        let conditionRows = '';
        conditionResults.forEach(cond => {
            // 실제 지급 상태와 일치하도록 상태 배지 설정
            const statusBadge = cond.met ?
                '<span class="badge bg-success">충족</span>' :
                cond.notApplicable ?
                '<span class="badge bg-secondary">해당없음</span>' :
                '<span class="badge bg-danger">미충족</span>';

            const valueDisplay = cond.value !== undefined ?
                `<strong>${cond.value}</strong> ${cond.unit || ''}` : '-';

            conditionRows += `
                <tr>
                    <td>${cond.id}</td>
                    <td>${cond.name}</td>
                    <td>${cond.threshold || '-'}</td>
                    <td>${valueDisplay}</td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        });

        // 실패 이유 정리
        const failureReasons = conditionResults
            .filter(c => !c.met && !c.notApplicable)
            .map(c => c.name);

        return `
            <div class="modal fade" id="employeeDetailModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="fas fa-user-circle me-2"></i>
                                Employee Details Status
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- 직원 기본 정보 -->
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h6 class="card-title">기본 정보</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <p><strong>사번:</strong> ${employee.emp_no || employee['Employee No'] || ''}</p>
                                            <p><strong>이름:</strong> ${employee.name || employee['Full Name'] || ''}</p>
                                            <p><strong>직급:</strong> ${employee.position || employee['FINAL QIP POSITION NAME CODE'] || ''}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><strong>TYPE:</strong> <span class="badge bg-${type === 'TYPE-1' ? 'primary' : type === 'TYPE-2' ? 'success' : 'secondary'}">${type}</span></p>
                                            <p><strong>인센티브:</strong> <span class="${isPaid ? 'text-success' : 'text-danger'} fw-bold">${Math.round(amount).toLocaleString()} VND</span></p>
                                            <p><strong>상태:</strong> ${isPaid ? '<span class="badge bg-success">지급</span>' : '<span class="badge bg-danger">미지급</span>'}</p>
                                        </div>
                                    </div>
                                    ${employee.Talent_Pool_Member === 'Y' ? `
                                        <div class="alert alert-warning mt-2">
                                            <i class="fas fa-star me-2"></i>
                                            <strong>Talent Pool Member</strong> - 특별 보너스 대상자
                                        </div>
                                    ` : ''}
                                </div>
                            </div>

                            <!-- 조건 충족 상태 -->
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h6 class="card-title">조건 충족 상태</h6>
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead class="table-light">
                                                <tr>
                                                    <th width="10%">#</th>
                                                    <th width="35%">조건</th>
                                                    <th width="20%">기준</th>
                                                    <th width="20%">실제값</th>
                                                    <th width="15%">상태</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${conditionRows}
                                            </tbody>
                                        </table>
                                    </div>

                                    ${!isPaid && failureReasons.length > 0 ? `
                                        <div class="alert alert-danger mt-3">
                                            <strong>미지급 사유:</strong>
                                            <ul class="mb-0 mt-2">
                                                ${failureReasons.map(reason => `<li>${reason}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${isPaid ? `
                                        <div class="alert alert-success mt-3">
                                            <i class="fas fa-check-circle me-2"></i>
                                            모든 조건을 충족하여 인센티브가 지급됩니다.
                                        </div>
                                    ` : ''}
                                </div>
                            </div>

                            <!-- 추가 정보 -->
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">추가 정보</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <p><small class="text-muted">근무일수:</small> ${employee['Actual Working Days'] || employee.actual_working_days || 0}일</p>
                                            <p><small class="text-muted">출근율:</small> ${((employee['Attendance Rate'] || employee.attendance_rate || 0) * 100).toFixed(1)}%</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><small class="text-muted">무단결근:</small> ${employee['Unapproved Absences'] || employee.unapproved_absences || 0}일</p>
                                            <p><small class="text-muted">AQL 실패:</small> ${employee['September AQL Failures'] || employee.aql_failures || 0}건</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // 직원 조건 평가 함수 (실제 인센티브 지급과 일치하도록 개선)
    function evaluateEmployeeConditions(employee) {
        const type = employee.type || employee['ROLE TYPE STD'] || 'TYPE-1';
        const position = (employee.position || employee['FINAL QIP POSITION NAME CODE'] || '').toUpperCase();

        // 실제 인센티브 금액 확인
        const actualIncentive = getIncentiveAmount(employee);
        const isPaid = actualIncentive > 0;

        // TYPE별 적용 조건 결정
        let applicableConditions = [];
        if (type === 'TYPE-1') {
            // TYPE-1 직급별 조건
            if (position.includes('ASSEMBLY INSPECTOR')) {
                applicableConditions = [1, 2, 3, 4, 5, 6, 9, 10];
            } else if (position.includes('AUDIT') || position.includes('TRAINING')) {
                applicableConditions = [1, 2, 3, 4, 7, 8];
            } else if (position.includes('MODEL MASTER')) {
                applicableConditions = [1, 2, 3, 4, 8];
            } else if (position.includes('LINE LEADER')) {
                applicableConditions = [1, 2, 3, 4, 7];
            } else {
                applicableConditions = [1, 2, 3, 4];
            }
        } else if (type === 'TYPE-2') {
            applicableConditions = [1, 2, 3, 4];
        } else if (type === 'TYPE-3') {
            applicableConditions = [];
        }

        // 조건 평가 결과 생성
        const results = [];
        const conditionDefinitions = {
            1: { name: '출근율', threshold: '≥88%', unit: '%' },
            2: { name: '무단결근', threshold: '≤2일', unit: '일' },
            3: { name: '실제 근무일', threshold: '>0일', unit: '일' },
            4: { name: '최소 근무일', threshold: '≥12일', unit: '일' },
            5: { name: '당월 AQL', threshold: '0건', unit: '건' },
            6: { name: '3개월 연속 AQL', threshold: '<3개월', unit: '개월' },
            7: { name: '팀/구역 AQL', threshold: '≤5%', unit: '%' },
            8: { name: '담당구역 Reject', threshold: '≤2%', unit: '%' },
            9: { name: '5PRS 통과율', threshold: '≥95%', unit: '%' },
            10: { name: '5PRS 검사량', threshold: '≥100족', unit: '족' }
        };

        // 각 조건 평가
        for (let i = 1; i <= 10; i++) {
            const isApplicable = applicableConditions.includes(i);
            const def = conditionDefinitions[i];

            let value, met = false;

            if (!isApplicable) {
                results.push({
                    id: i,
                    name: def.name,
                    threshold: def.threshold,
                    value: undefined,
                    met: false,
                    notApplicable: true
                });
                continue;
            }

            // 조건별 평가
            switch (i) {
                case 1: // 출근율
                    value = (employee['Attendance Rate'] || employee.attendance_rate || 0) * 100;
                    met = value >= 88;
                    break;
                case 2: // 무단결근
                    value = employee['Unapproved Absences'] || employee.unapproved_absences || 0;
                    met = value <= 2;
                    break;
                case 3: // 실제 근무일
                    value = employee['Actual Working Days'] || employee.actual_working_days || 0;
                    met = value > 0;
                    break;
                case 4: // 최소 근무일
                    value = employee['Actual Working Days'] || employee.actual_working_days || 0;
                    met = value >= 12;
                    break;
                case 5: // 당월 AQL
                    value = employee['September AQL Failures'] || employee.aql_failures || 0;
                    met = value === 0;
                    break;
                case 6: // 3개월 연속 AQL
                    value = employee.continuous_aql_failures || 0;
                    met = value < 3;
                    break;
                case 7: // 팀/구역 AQL
                    value = (employee.team_aql_fail_rate || 0) * 100;
                    met = value <= 5;
                    break;
                case 8: // 담당구역 Reject
                    value = (employee.area_reject_rate || 0) * 100;
                    met = value <= 2;
                    break;
                case 9: // 5PRS 통과율
                    value = employee.pass_rate || employee['5PRS Pass Rate'] || 0;
                    met = value >= 95;
                    break;
                case 10: // 5PRS 검사량
                    value = employee.validation_qty || employee['5PRS Inspection Quantity'] || 0;
                    met = value >= 100;
                    break;
            }

            results.push({
                id: i,
                name: def.name,
                threshold: def.threshold,
                value: typeof value === 'number' ? value.toFixed(1) : value,
                unit: def.unit,
                met: met,
                notApplicable: false
            });
        }

        return results;
    }

    // 월 이름 가져오기 함수
    function getMonthName(monthNum, lang) {
        const monthNames = {
            ko: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
            en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            vi: ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
        };

        return monthNames[lang || 'ko'][monthNum - 1] || `${monthNum}월`;
    }

    // Individual Details observer - integrated into main initialization
