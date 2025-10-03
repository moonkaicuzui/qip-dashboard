#!/usr/bin/env python3
"""
인센티브 기준 탭 렌더링 함수 추가 스크립트
"""

# JavaScript 코드 추가
js_addition = '''
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
'''

# JavaScript 파일에 추가
js_file = "dashboard_v2/static/js/dashboard_complete.js"

with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

# initializeDashboard 함수 찾기
init_pattern = r'function initializeDashboard\(\) \{'

if init_pattern in content:
    # 함수가 이미 존재한다면, 그 앞에 renderCriteriaTab 함수 추가
    content = content.replace('function initializeDashboard() {',
                            js_addition + '\n\n    function initializeDashboard() {')
    print("✅ renderCriteriaTab 함수 추가 완료")
else:
    print("⚠️ initializeDashboard 함수를 찾을 수 없습니다.")

# 파일 저장
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 인센티브 기준 탭 렌더링 함수 추가 완료!")