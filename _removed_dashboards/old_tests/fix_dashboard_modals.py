#!/usr/bin/env python3
"""
대시보드에 모달 함수를 직접 추가하는 스크립트
"""

def get_modal_functions():
    """개선된 모달 함수들을 반환"""
    return '''
    // ===== IMPROVED MODAL FUNCTIONS =====

    function showTotalWorkingDaysDetails() {
        const workDays = [2,3,4,5,6,9,10,11,12,13,16,17,18,19]; // 9월 실제 근무일
        const holidays = [1,7,8,14,15]; // 주말

        let calendarHTML = '<div class="calendar-grid">';
        for (let day = 1; day <= 19; day++) {
            const isWorkDay = workDays.includes(day);
            const isWeekend = holidays.includes(day);
            const dayClass = isWorkDay ? 'work-day' : (isWeekend ? 'weekend' : 'holiday');
            const icon = isWorkDay ? '💼' : (isWeekend ? '🏖️' : '🎉');

            calendarHTML += `
                <div class="calendar-day ${dayClass}">
                    <div class="day-number">${day}</div>
                    <div class="day-icon">${icon}</div>
                </div>
            `;
        }
        calendarHTML += '</div>';

        const modalContent = `
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">
                    <i class="fas fa-calendar-alt"></i> 2025년 9월 근무일 현황
                </h5>
                <button type="button" class="close text-white" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card text-center p-3 border rounded">
                            <div class="stat-icon">💼</div>
                            <div class="stat-label">총 근무일</div>
                            <div class="stat-value text-primary h3">13일</div>
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
                            <div class="stat-icon">🏖️</div>
                            <div class="stat-label">휴일</div>
                            <div class="stat-value text-success h3">6일</div>
                        </div>
                    </div>
                </div>
                ${calendarHTML}
                <div class="mt-3">
                    <span class="badge badge-primary">💼 근무일</span>
                    <span class="badge badge-secondary">🏖️ 주말</span>
                    <span class="badge badge-success">🎉 공휴일</span>
                </div>
            </div>
        `;

        // 모달 표시
        let modal = document.getElementById('detailModal');
        if (!modal) {
            // 모달이 없으면 생성
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" role="dialog">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content" id="detailModalContent">
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;
        $('#detailModal').modal('show');
    }

    function showZeroWorkingDaysDetails() {
        const zeroWorkingEmployees = window.employeeData.filter(emp => {
            const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
            return actualDays === 0;
        });

        let tableRows = '';
        if (zeroWorkingEmployees.length === 0) {
            tableRows = '<tr><td colspan="6" class="text-center">0일 근무자가 없습니다</td></tr>';
        } else {
            tableRows = zeroWorkingEmployees.map(emp => {
                const stopDate = emp.stop_working_date || emp['Stop working Date'] || '';
                const isResigned = stopDate && stopDate !== '';

                return `
                    <tr>
                        <td>${emp.employee_no || emp['Employee No'] || ''}</td>
                        <td>${emp.full_name || emp['Full Name'] || ''}</td>
                        <td>${emp.qip_position || emp['QIP POSITION 1ST  NAME'] || '-'}</td>
                        <td class="text-center">13</td>
                        <td class="text-center">0</td>
                        <td>
                            <span class="badge ${isResigned ? 'badge-warning' : 'badge-danger'}">
                                ${isResigned ? `퇴사` : '전체 결근'}
                            </span>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        const modalContent = `
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">
                    <i class="fas fa-exclamation-triangle"></i> 0일 근무자 상세
                </h5>
                <button type="button" class="close text-white" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="alert alert-info mb-3">
                    <i class="fas fa-info-circle"></i>
                    실제 근무일이 0일인 직원 목록입니다.
                </div>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="thead-light">
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직책</th>
                                <th>총 근무일</th>
                                <th>실 근무일</th>
                                <th>상태</th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
            </div>
        `;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" role="dialog">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content" id="detailModalContent">
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;
        $('#detailModal').modal('show');
    }

    function showAbsentWithoutInformDetails() {
        const absentEmployees = window.employeeData.filter(emp => {
            const unapproved = parseFloat(emp.unapproved_absence_days || emp['Unapproved Absence Days'] || 0);
            return unapproved >= 1;
        }).sort((a, b) => {
            const aVal = parseFloat(a.unapproved_absence_days || a['Unapproved Absence Days'] || 0);
            const bVal = parseFloat(b.unapproved_absence_days || b['Unapproved Absence Days'] || 0);
            return bVal - aVal;
        });

        let tableRows = '';
        if (absentEmployees.length === 0) {
            tableRows = '<tr><td colspan="5" class="text-center">무단결근자가 없습니다</td></tr>';
        } else {
            tableRows = absentEmployees.map(emp => {
                const days = parseFloat(emp.unapproved_absence_days || emp['Unapproved Absence Days'] || 0);
                const rowClass = days > 2 ? 'table-danger' : (days > 1 ? 'table-warning' : '');
                const status = days > 2 ?
                    '<span class="badge badge-danger">인센티브 제외</span>' :
                    '<span class="badge badge-warning">경고</span>';

                return `
                    <tr class="${rowClass}">
                        <td>${emp.employee_no || emp['Employee No'] || ''}</td>
                        <td>${emp.full_name || emp['Full Name'] || ''}</td>
                        <td>${emp.qip_position || emp['QIP POSITION 1ST  NAME'] || '-'}</td>
                        <td class="text-center">
                            <span class="badge badge-pill badge-danger">${days}일</span>
                        </td>
                        <td class="text-center">${status}</td>
                    </tr>
                `;
            }).join('');
        }

        const modalContent = `
            <div class="modal-header bg-warning">
                <h5 class="modal-title">
                    <i class="fas fa-user-times"></i> 무단결근 직원 상세
                </h5>
                <button type="button" class="close" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="alert alert-warning mb-3">
                    <i class="fas fa-exclamation-triangle"></i>
                    무단결근 2일 초과 시 인센티브 지급 대상에서 제외됩니다.
                </div>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="thead-light">
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직책</th>
                                <th class="text-center">무단결근</th>
                                <th class="text-center">상태</th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
            </div>
        `;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" role="dialog">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content" id="detailModalContent">
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;
        $('#detailModal').modal('show');
    }

    function showMinimumDaysNotMetDetails() {
        const currentDay = new Date().getDate();
        const minimumRequired = currentDay < 20 ? 7 : 12;

        const notMetEmployees = window.employeeData.filter(emp => {
            const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
            return actualDays > 0 && actualDays < minimumRequired;
        }).sort((a, b) => {
            const aVal = parseFloat(a.actual_working_days || a['Actual Working Days'] || 0);
            const bVal = parseFloat(b.actual_working_days || b['Actual Working Days'] || 0);
            return aVal - bVal;
        });

        let tableRows = '';
        if (notMetEmployees.length === 0) {
            tableRows = `<tr><td colspan="6" class="text-center">모든 직원이 최소 근무일(${minimumRequired}일)을 충족했습니다</td></tr>`;
        } else {
            tableRows = notMetEmployees.map(emp => {
                const actualDays = parseFloat(emp.actual_working_days || emp['Actual Working Days'] || 0);
                const shortage = minimumRequired - actualDays;
                const percentage = (actualDays / minimumRequired * 100).toFixed(1);
                const progressColor = percentage < 50 ? 'danger' : (percentage < 75 ? 'warning' : 'info');

                return `
                    <tr>
                        <td>${emp.employee_no || emp['Employee No'] || ''}</td>
                        <td>${emp.full_name || emp['Full Name'] || ''}</td>
                        <td>${emp.qip_position || emp['QIP POSITION 1ST  NAME'] || '-'}</td>
                        <td class="text-center">
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-${progressColor}"
                                     style="width: ${percentage}%">
                                    ${actualDays}일
                                </div>
                            </div>
                        </td>
                        <td class="text-center">
                            <span class="badge badge-primary">${minimumRequired}일</span>
                        </td>
                        <td class="text-center">
                            <span class="badge badge-danger">-${shortage}일</span>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        const modalContent = `
            <div class="modal-header bg-info text-white">
                <h5 class="modal-title">
                    <i class="fas fa-clock"></i> 최소 근무일 미충족 직원 상세
                </h5>
                <button type="button" class="close text-white" data-dismiss="modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="alert alert-info mb-3">
                    <i class="fas fa-info-circle"></i>
                    ${currentDay < 20 ? '월중 보고서' : '월말 보고서'} 기준: 최소 ${minimumRequired}일 근무 필요
                </div>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="thead-light">
                            <tr>
                                <th>사번</th>
                                <th>이름</th>
                                <th>직책</th>
                                <th class="text-center">실제 근무일</th>
                                <th class="text-center">최소 요구</th>
                                <th class="text-center">부족</th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>
            </div>
        `;

        let modal = document.getElementById('detailModal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="detailModal" tabindex="-1" role="dialog">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content" id="detailModalContent">
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('detailModal');
        }

        document.getElementById('detailModalContent').innerHTML = modalContent;
        $('#detailModal').modal('show');
    }
    '''

def get_modal_styles():
    """모달용 CSS 스타일 반환"""
    return '''
    /* Modal Improvements CSS */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-top: 20px;
    }
    .calendar-day {
        aspect-ratio: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        padding: 10px;
        transition: transform 0.2s;
        font-size: 14px;
    }
    .calendar-day:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .calendar-day.work-day {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
    }
    .calendar-day.weekend {
        background-color: #f3e5f5;
        border: 2px solid #9c27b0;
    }
    .calendar-day.holiday {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
    }
    .day-number {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .day-icon {
        font-size: 1.5rem;
    }
    .stat-card {
        transition: transform 0.2s;
        background: #f8f9fa;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stat-value {
        font-weight: 600;
    }
    .modal-body .table td {
        vertical-align: middle;
    }
    .badge-pill {
        padding: 0.375rem 0.75rem;
    }
    '''

def inject_modal_to_html():
    """생성된 HTML 파일에 모달 함수 직접 주입"""
    html_file = 'output_files/Incentive_Dashboard_2025_09_Version_5.html'

    # HTML 파일 읽기
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 모달 함수가 이미 있는지 확인
    if 'showTotalWorkingDaysDetails' in content:
        print("모달 함수가 이미 존재합니다. 교체합니다...")
        # 기존 함수 제거
        import re
        content = re.sub(
            r'function showTotalWorkingDaysDetails\(\)[\s\S]*?(?=function\s|\n\s*</script>)',
            '',
            content
        )

    # </script> 태그 찾기
    script_end = content.rfind('</script>')
    if script_end > 0:
        # 모달 함수 삽입
        modal_functions = get_modal_functions()
        content = content[:script_end] + modal_functions + '\n' + content[script_end:]

    # </style> 태그 찾기
    style_end = content.rfind('</style>')
    if style_end > 0:
        # 스타일 삽입
        modal_styles = get_modal_styles()
        content = content[:style_end] + modal_styles + '\n' + content[style_end:]

    # 수정된 내용 저장
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 모달 함수가 {html_file}에 성공적으로 추가되었습니다.")
    return True

if __name__ == "__main__":
    inject_modal_to_html()
    print("\n📊 대시보드를 새로고침하면 모달이 정상 작동합니다:")
    print("   - Total Working Days: 캘린더 뷰와 이모티콘")
    print("   - Zero Working Days: 실제 데이터 표시")
    print("   - Absent Without Inform: 무단결근자 리스트")
    print("   - Minimum Days Not Met: Progress Bar 시각화")