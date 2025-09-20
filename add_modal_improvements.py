#!/usr/bin/env python3
"""
대시보드에 개선된 모달 기능 추가
"""

import re

def add_improved_modals_to_dashboard():
    """integrated_dashboard_final.py에 모달 개선사항 추가"""

    # 개선된 모달 스크립트 읽기
    with open('improved_modal_scripts.js', 'r', encoding='utf-8') as f:
        improved_scripts = f.read()

    # integrated_dashboard_final.py 읽기
    with open('integrated_dashboard_final.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # generate_dashboard_html 함수 찾기
    pattern = r'def generate_dashboard_html\([^)]*\):'
    match = re.search(pattern, content)

    if not match:
        print("generate_dashboard_html 함수를 찾을 수 없습니다.")
        return False

    # JavaScript 섹션에 모달 함수 추가
    # </script> 태그 직전에 삽입
    script_end_pattern = r'(\s*)(</script>)'

    # 모달 함수가 이미 있는지 확인
    if 'showZeroWorkingDaysDetails' not in content:
        # 모달 HTML 구조 추가
        modal_html = '''
        <!-- Detail Modal -->
        <div class="modal fade" id="detailModal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content" id="detailModalContent">
                    <!-- Content will be dynamically loaded -->
                </div>
            </div>
        </div>
        '''

        # body 태그 닫기 직전에 모달 HTML 추가
        body_end = r'(\s*)(</body>)'
        content = re.sub(body_end, f'{modal_html}\\1\\2', content)

    # CSS 스타일 추가
    style_addition = '''
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
        }
        .calendar-day:hover { transform: scale(1.05); }
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
        .day-number { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
        .day-icon { font-size: 1.5rem; }
        .stat-card { transition: transform 0.2s; }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .stat-icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-label { color: #666; font-size: 0.9rem; }
        .progress { background-color: #f0f0f0; }
        .modal-body .table td { vertical-align: middle; }
    '''

    # CSS 섹션에 추가
    style_pattern = r'(</style>)'
    content = re.sub(style_pattern, f'{style_addition}\\1', content, count=1)

    # 수정된 내용 저장
    with open('integrated_dashboard_final_with_modals.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ 모달 개선사항이 integrated_dashboard_final_with_modals.py 파일에 추가되었습니다.")
    return True

def create_validation_tab_with_modals():
    """validation 탭에 모달 호출 버튼 추가"""

    validation_tab_html = '''
    <div id="validation-content" class="tab-pane fade">
        <div class="row mb-4">
            <div class="col-12">
                <h4>📊 Summary & System Validation</h4>
            </div>
        </div>

        <!-- KPI Cards with Modal Triggers -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">총 근무일</h5>
                        <h2 class="text-primary">13일</h2>
                        <button class="btn btn-sm btn-primary" onclick="showTotalWorkingDaysDetails()">
                            <i class="fas fa-calendar-alt"></i> 상세보기
                        </button>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">0일 근무자</h5>
                        <h2 class="text-danger" id="zeroWorkingCount">0명</h2>
                        <button class="btn btn-sm btn-danger" onclick="showZeroWorkingDaysDetails()">
                            <i class="fas fa-user-times"></i> 상세보기
                        </button>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">무단결근 2일 초과</h5>
                        <h2 class="text-warning" id="absentCount">0명</h2>
                        <button class="btn btn-sm btn-warning" onclick="showAbsentWithoutInformDetails()">
                            <i class="fas fa-exclamation-triangle"></i> 상세보기
                        </button>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">최소일 미충족</h5>
                        <h2 class="text-info" id="minimumNotMetCount">0명</h2>
                        <button class="btn btn-sm btn-info" onclick="showMinimumDaysNotMetDetails()">
                            <i class="fas fa-clock"></i> 상세보기
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Calculate counts when tab is shown
            document.addEventListener('DOMContentLoaded', function() {
                // Zero working days
                const zeroCount = employeeData.filter(emp =>
                    parseFloat(emp.actual_working_days || emp.Actual_Working_Days || 0) === 0
                ).length;
                document.getElementById('zeroWorkingCount').innerText = zeroCount + '명';

                // Absent without inform > 2 days
                const absentCount = employeeData.filter(emp =>
                    parseFloat(emp.unapproved_absence_days || emp.Unapproved_Absence_Days || 0) > 2
                ).length;
                document.getElementById('absentCount').innerText = absentCount + '명';

                // Minimum days not met
                const currentDay = new Date().getDate();
                const minimumRequired = currentDay < 20 ? 7 : 12;
                const notMetCount = employeeData.filter(emp => {
                    const actualDays = parseFloat(emp.actual_working_days || emp.Actual_Working_Days || 0);
                    return actualDays > 0 && actualDays < minimumRequired;
                }).length;
                document.getElementById('minimumNotMetCount').innerText = notMetCount + '명';
            });
        </script>
    </div>
    '''

    return validation_tab_html

if __name__ == "__main__":
    # 1. 모달 개선사항 추가
    if add_improved_modals_to_dashboard():
        # 2. Validation 탭 HTML 생성
        validation_html = create_validation_tab_with_modals()

        # 파일로 저장
        with open('validation_tab_template.html', 'w', encoding='utf-8') as f:
            f.write(validation_html)

        print("✅ validation_tab_template.html 생성 완료")
        print("\n다음 단계:")
        print("1. integrated_dashboard_final_with_modals.py 파일을 사용하여 대시보드 재생성")
        print("2. python3 integrated_dashboard_final_with_modals.py --month 9 --year 2025")