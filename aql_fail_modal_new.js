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

        // 현재 언어 상태
        let currentLang = currentLanguage || 'ko';

        function sortData(column) {
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
                    case 'supervisor':
                        aVal = a['direct boss name'] || '';
                        bVal = b['direct boss name'] || '';
                        break;
                    case 'inspectorId':
                        aVal = a['MST direct boss name'] || '';
                        bVal = b['MST direct boss name'] || '';
                        break;
                    case 'passCount':
                        aVal = parseFloat(a['AQL_Pass_Count'] || 0);
                        bVal = parseFloat(b['AQL_Pass_Count'] || 0);
                        break;
                    case 'failures':
                        aVal = parseFloat(a['September AQL Failures'] || 0);
                        bVal = parseFloat(b['September AQL Failures'] || 0);
                        break;
                    case 'failPercent':
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

        function switchLanguage(lang) {
            currentLang = lang;
            updateAllModalContent();
        }

        function updateAllModalContent() {
            // 모달 제목 업데이트
            const titleEl = document.querySelector('#aqlFailModal .modal-title span[data-i18n]');
            if (titleEl) {
                titleEl.textContent = getTranslation('validationTab.modals.aqlFail.title', currentLang);
            }

            // Alert 메시지 업데이트
            const alertEl = document.querySelector('#aqlFailModal .alert span[data-i18n="aqlFailAlert"]');
            if (alertEl) {
                alertEl.textContent = getTranslation('validationTab.modals.aqlFail.alertMessage', currentLang);
            }

            // 카운트 메시지 업데이트
            const countEl = document.querySelector('#aqlFailModal .alert span[data-i18n="aqlFailCount"]');
            if (countEl) {
                const countMsg = getTranslation('validationTab.modals.aqlFail.totalCount', currentLang);
                countEl.textContent = countMsg.replace('{count}', aqlFailEmployees.length);
            }

            // 테이블 헤더 업데이트
            const headers = {
                'empNo': 'validationTab.modals.aqlFail.headers.empNo',
                'name': 'validationTab.modals.aqlFail.headers.name',
                'supervisor': 'validationTab.modals.aqlFail.headers.supervisor',
                'inspectorId': 'validationTab.modals.aqlFail.headers.inspectorId',
                'aqlPass': 'validationTab.modals.aqlFail.headers.aqlPass',
                'aqlFail': 'validationTab.modals.aqlFail.headers.aqlFail',
                'failPercent': 'validationTab.modals.aqlFail.headers.failPercent'
            };

            Object.keys(headers).forEach(key => {
                const headerEl = document.querySelector(`#aqlFailModal th[data-i18n="${key}"]`);
                if (headerEl) {
                    const iconSpan = headerEl.querySelector('.sort-icon');
                    const icon = iconSpan ? iconSpan.textContent : '';
                    headerEl.innerHTML = `<span data-i18n="${key}">${getTranslation(headers[key], currentLang)}</span><span class="sort-icon">${icon}</span>`;
                }
            });

            // 라인리더 집계 섹션 헤더 업데이트
            const lineLeaderTitleEl = document.querySelector('#aqlFailModal h6[data-i18n="lineLeaderTitle"]');
            if (lineLeaderTitleEl) {
                lineLeaderTitleEl.innerHTML = `<i class="fas fa-users me-2"></i><span data-i18n="lineLeaderTitle">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.title', currentLang)}</span>`;
            }

            const lineLeaderDescEl = document.querySelector('#aqlFailModal p[data-i18n="lineLeaderDesc"]');
            if (lineLeaderDescEl) {
                lineLeaderDescEl.textContent = getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.description', currentLang);
            }

            // 라인리더 테이블 헤더 업데이트
            const lineLeaderHeaders = {
                'leaderName': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderName',
                'leaderSupervisor': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderSupervisor',
                'subordinatePass': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinatePass',
                'subordinateFail': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinateFail',
                'failPercent': 'validationTab.modals.aqlFail.lineLeaderSummary.headers.failPercent'
            };

            Object.keys(lineLeaderHeaders).forEach(key => {
                const headerEl = document.querySelector(`#lineLeaderTable th[data-i18n="${key}"]`);
                if (headerEl) {
                    headerEl.textContent = getTranslation(lineLeaderHeaders[key], currentLang);
                }
            });
        }

        function updateTableBody() {
            const tbody = document.querySelector('#aqlFailModal tbody');
            if (!tbody) return;

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp['September AQL Failures'] || 0);
                const supervisorName = emp['direct boss name'] || '-';
                const supervisorId = emp['MST direct boss name'] || '-';

                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                // 실패율에 따른 색상 구분
                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = currentLang === 'ko' ? `${failPercent}% (심각)` : currentLang === 'en' ? `${failPercent}% (Critical)` : `${failPercent}% (Nghiêm trọng)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = currentLang === 'ko' ? `${failPercent}% (경고)` : currentLang === 'en' ? `${failPercent}% (Warning)` : `${failPercent}% (Cảnh báo)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                        <td class="unified-table-cell">${supervisorName}</td>
                        <td class="unified-table-cell text-center">${supervisorId}</td>
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

            const emptyMessage = currentLang === 'ko' ? 'AQL FAIL이 없습니다' : currentLang === 'en' ? 'No AQL FAIL records' : 'Không có bản ghi AQL FAIL';
            tbody.innerHTML = tableRows || `<tr><td colspan="7" class="text-center text-muted">${emptyMessage}</td></tr>`;

            // 정렬 아이콘 업데이트
            document.querySelectorAll('#aqlFailModal th[data-sort]').forEach(th => {
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

        function aggregateLineLeaderStats() {
            const lineLeaderStats = {};

            // 라인리더별 집계
            aqlFailEmployees.forEach(emp => {
                const supervisorId = emp['MST direct boss name'];
                const supervisorName = emp['direct boss name'];

                if (!supervisorId || !supervisorName) return;

                if (!lineLeaderStats[supervisorId]) {
                    // 라인리더의 상사 정보 찾기
                    const supervisorData = window.employeeData.find(e => e['Employee No'] === supervisorId);
                    const supervisorOfSupervisor = supervisorData ? (supervisorData['direct boss name'] || '-') : '-';

                    lineLeaderStats[supervisorId] = {
                        name: supervisorName,
                        supervisor: supervisorOfSupervisor,
                        totalPass: 0,
                        totalFail: 0
                    };
                }

                const passCount = parseFloat(emp['AQL_Pass_Count'] || 0);
                const failCount = parseFloat(emp['September AQL Failures'] || 0);

                lineLeaderStats[supervisorId].totalPass += passCount;
                lineLeaderStats[supervisorId].totalFail += failCount;
            });

            // 배열로 변환 및 FAIL % 계산
            return Object.values(lineLeaderStats).map(stat => {
                const total = stat.totalPass + stat.totalFail;
                const failPercent = total > 0 ? ((stat.totalFail / total) * 100).toFixed(1) : '0.0';
                return { ...stat, failPercent: parseFloat(failPercent) };
            }).sort((a, b) => b.failPercent - a.failPercent); // FAIL % 내림차순
        }

        function renderLineLeaderTable() {
            const lineLeaderStats = aggregateLineLeaderStats();
            const tbody = document.querySelector('#lineLeaderTable tbody');
            if (!tbody) return;

            const rows = lineLeaderStats.map(stat => {
                let failBadgeClass = '';
                if (stat.failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                } else if (stat.failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                } else {
                    failBadgeClass = 'bg-info';
                }

                return `
                    <tr>
                        <td class="unified-table-cell">${stat.name}</td>
                        <td class="unified-table-cell">${stat.supervisor}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${stat.totalPass}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${stat.totalFail}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${stat.failPercent}%</span>
                        </td>
                    </tr>
                `;
            }).join('');

            const emptyMessage = currentLang === 'ko' ? '라인리더 데이터가 없습니다' : currentLang === 'en' ? 'No Line Leader data' : 'Không có dữ liệu Line Leader';
            tbody.innerHTML = rows || `<tr><td colspan="5" class="text-center text-muted">${emptyMessage}</td></tr>`;
        }

        function createAqlFailModal() {
            const lang = currentLang;

            function getSortIcon(column) {
                if (sortColumn === column) {
                    return sortOrder === 'asc' ? ' ▲' : ' ▼';
                }
                return ' ⇅';
            }

            let tableRows = aqlFailEmployees.map(emp => {
                const failures = parseFloat(emp['September AQL Failures'] || 0);
                const supervisorName = emp['direct boss name'] || '-';
                const supervisorId = emp['MST direct boss name'] || '-';

                const totalTests = emp['AQL_Total_Tests'] || 10;
                const passCount = emp['AQL_Pass_Count'] || Math.max(0, totalTests - failures);
                const failPercent = emp['AQL_Fail_Percent'] ? emp['AQL_Fail_Percent'].toFixed(1) : ((failures / totalTests * 100).toFixed(1));

                let failBadgeClass = '';
                let failBadgeText = '';
                if (failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                    failBadgeText = lang === 'ko' ? `${failPercent}% (심각)` : lang === 'en' ? `${failPercent}% (Critical)` : `${failPercent}% (Nghiêm trọng)`;
                } else if (failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                    failBadgeText = lang === 'ko' ? `${failPercent}% (경고)` : lang === 'en' ? `${failPercent}% (Warning)` : `${failPercent}% (Cảnh báo)`;
                } else {
                    failBadgeClass = 'bg-info';
                    failBadgeText = `${failPercent}%`;
                }

                return `
                    <tr class="unified-table-row">
                        <td class="unified-table-cell">${emp['Employee No'] || ''}</td>
                        <td class="unified-table-cell">${emp['Full Name'] || ''}</td>
                        <td class="unified-table-cell">${supervisorName}</td>
                        <td class="unified-table-cell text-center">${supervisorId}</td>
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

            // 라인리더 집계 테이블
            const lineLeaderStats = aggregateLineLeaderStats();
            const lineLeaderRows = lineLeaderStats.map(stat => {
                let failBadgeClass = '';
                if (stat.failPercent >= 30) {
                    failBadgeClass = 'bg-danger';
                } else if (stat.failPercent >= 20) {
                    failBadgeClass = 'bg-warning text-dark';
                } else {
                    failBadgeClass = 'bg-info';
                }

                return `
                    <tr>
                        <td class="unified-table-cell">${stat.name}</td>
                        <td class="unified-table-cell">${stat.supervisor}</td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-success">${stat.totalPass}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge bg-danger">${stat.totalFail}건</span>
                        </td>
                        <td class="unified-table-cell text-center">
                            <span class="badge ${failBadgeClass}">${stat.failPercent}%</span>
                        </td>
                    </tr>
                `;
            }).join('');

            const countMsg = getTranslation('validationTab.modals.aqlFail.totalCount', lang).replace('{count}', aqlFailEmployees.length);

            let modalContent = `
                <div class="modal-dialog modal-xl" style="max-width: 95%; margin: 20px auto;">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <span data-i18n="validationTab.modals.aqlFail.title">${getTranslation('validationTab.modals.aqlFail.title', lang)}</span>
                            </h5>
                            <div class="d-flex align-items-center">
                                <div class="btn-group btn-group-sm me-3">
                                    <button type="button" class="btn ${lang === 'ko' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('ko')">한국어</button>
                                    <button type="button" class="btn ${lang === 'en' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('en')">English</button>
                                    <button type="button" class="btn ${lang === 'vi' ? 'btn-primary' : 'btn-outline-primary'}" onclick="window.switchAqlLang('vi')">Tiếng Việt</button>
                                </div>
                                <button type="button" class="btn-close" onclick="window.closeAqlModal()"></button>
                            </div>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning d-flex align-items-center mb-3">
                                <i class="fas fa-info-circle me-2"></i>
                                <div>
                                    <strong><span data-i18n="aqlFailAlert">${getTranslation('validationTab.modals.aqlFail.alertMessage', lang)}</span></strong><br>
                                    <span data-i18n="aqlFailCount">${countMsg}</span>
                                </div>
                            </div>

                            <h6 class="mb-3"><i class="fas fa-list me-2"></i>직원별 AQL FAIL 상세</h6>

                            <table class="table table-hover" id="aqlFailEmployeeTable">
                                <thead class="unified-table-header">
                                    <tr>
                                        <th style="cursor: pointer;" data-sort="empNo" onclick="window.sortAqlData('empNo')">
                                            <span data-i18n="empNo">${getTranslation('validationTab.modals.aqlFail.headers.empNo', lang)}</span><span class="sort-icon">${getSortIcon('empNo')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="name" onclick="window.sortAqlData('name')">
                                            <span data-i18n="name">${getTranslation('validationTab.modals.aqlFail.headers.name', lang)}</span><span class="sort-icon">${getSortIcon('name')}</span>
                                        </th>
                                        <th style="cursor: pointer;" data-sort="supervisor" onclick="window.sortAqlData('supervisor')">
                                            <span data-i18n="supervisor">${getTranslation('validationTab.modals.aqlFail.headers.supervisor', lang)}</span><span class="sort-icon">${getSortIcon('supervisor')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="inspectorId" onclick="window.sortAqlData('inspectorId')">
                                            <span data-i18n="inspectorId">${getTranslation('validationTab.modals.aqlFail.headers.inspectorId', lang)}</span><span class="sort-icon">${getSortIcon('inspectorId')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="passCount" onclick="window.sortAqlData('passCount')">
                                            <span data-i18n="aqlPass">${getTranslation('validationTab.modals.aqlFail.headers.aqlPass', lang)}</span><span class="sort-icon">${getSortIcon('passCount')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failures" onclick="window.sortAqlData('failures')">
                                            <span data-i18n="aqlFail">${getTranslation('validationTab.modals.aqlFail.headers.aqlFail', lang)}</span><span class="sort-icon">${getSortIcon('failures')}</span>
                                        </th>
                                        <th class="text-center" style="cursor: pointer;" data-sort="failPercent" onclick="window.sortAqlData('failPercent')">
                                            <span data-i18n="failPercent">${getTranslation('validationTab.modals.aqlFail.headers.failPercent', lang)}</span><span class="sort-icon">${getSortIcon('failPercent')}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableRows || '<tr><td colspan="7" class="text-center text-muted">AQL FAIL이 없습니다</td></tr>'}
                                </tbody>
                            </table>

                            <hr class="my-4">

                            <h6 class="mb-3" data-i18n="lineLeaderTitle"><i class="fas fa-users me-2"></i>${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.title', lang)}</h6>
                            <p class="text-muted small" data-i18n="lineLeaderDesc">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.description', lang)}</p>

                            <table class="table table-hover" id="lineLeaderTable">
                                <thead class="unified-table-header">
                                    <tr>
                                        <th data-i18n="leaderName">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderName', lang)}</th>
                                        <th data-i18n="leaderSupervisor">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.leaderSupervisor', lang)}</th>
                                        <th class="text-center" data-i18n="subordinatePass">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinatePass', lang)}</th>
                                        <th class="text-center" data-i18n="subordinateFail">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.subordinateFail', lang)}</th>
                                        <th class="text-center" data-i18n="failPercent">${getTranslation('validationTab.modals.aqlFail.lineLeaderSummary.headers.failPercent', lang)}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${lineLeaderRows || '<tr><td colspan="5" class="text-center text-muted">라인리더 데이터가 없습니다</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            // 기존 모달 제거
            const existingModal = document.getElementById('aqlFailModal');
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
            modalDiv.id = 'aqlFailModal';
            modalDiv.className = 'modal fade show';
            modalDiv.style.display = 'block';
            modalDiv.style.zIndex = '1055';
            modalDiv.innerHTML = modalContent;

            // 백드롭 생성
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.style.zIndex = '1050';

            document.body.appendChild(backdrop);
            document.body.appendChild(modalDiv);
            document.body.style.overflow = 'hidden';

            // 전역 함수 등록
            window.sortAqlData = sortData;
            window.switchAqlLang = switchLanguage;
        }

        // 모달 닫기 함수
        window.closeAqlModal = function() {
            if (modalDiv) {
                modalDiv.remove();
                modalDiv = null;
            }
            if (backdrop) {
                backdrop.remove();
                backdrop = null;
            }
            document.body.style.overflow = '';
        };

        // 초기 렌더링
        sortData('failPercent');  // FAIL %로 정렬
        createAqlFailModal();
    }
