/**
 * Dashboard V2 - Main JavaScript Module
 * 구조 개선된 인센티브 대시보드
 */

// ==================== Global State ====================
const DashboardState = {
    currentLang: 'ko',
    currentTab: 'summary',
    data: null,
    translations: null,
    charts: {},
    initialized: false
};

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Dashboard V2...');

    // Load data from global variable
    if (window.dashboardData) {
        DashboardState.data = window.dashboardData.employees;
        DashboardState.translations = window.dashboardData.translations;
        DashboardState.config = window.dashboardData.config;
        DashboardState.stats = window.dashboardData.stats;

        initializeDashboard();
    } else {
        console.error('Dashboard data not found!');
        showError('데이터를 불러올 수 없습니다.');
    }
});

function initializeDashboard() {
    // 1. Initialize language system
    LanguageManager.init();

    // 2. Render navigation tabs
    TabManager.renderTabs();

    // 3. Render initial content
    TabManager.showTab('summary');

    // 4. Setup event listeners
    setupEventListeners();

    DashboardState.initialized = true;
    console.log('Dashboard initialized successfully');
}

// ==================== Language Manager ====================
const LanguageManager = {
    init() {
        // Set initial language
        this.setLanguage(DashboardState.currentLang);

        // Setup language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setLanguage(e.target.dataset.lang);
            });
        });
    },

    setLanguage(lang) {
        DashboardState.currentLang = lang;

        // Update button states
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });

        // Update all texts
        this.updateAllTexts();

        // Store preference
        localStorage.setItem('dashboardLang', lang);
    },

    updateAllTexts() {
        // Update header
        const titleElement = document.getElementById('dashboardTitle');
        if (titleElement) {
            const title = this.getTranslation('headers.title');
            titleElement.textContent = title;
        }

        // Update subtitle
        const subtitleElement = document.getElementById('dashboardSubtitle');
        if (subtitleElement && DashboardState.config) {
            const month = DashboardState.config.month;
            const year = DashboardState.config.year;
            const subtitleText = this.getTranslation('headers.subtitle');

            if (subtitleText && subtitleText !== 'headers.subtitle') {
                const subtitle = subtitleText
                    .replace('{month}', this.getMonthName(month))
                    .replace('{year}', year);
                subtitleElement.textContent = subtitle;
            } else {
                // Fallback if translation not found
                subtitleElement.textContent = `${year}년 ${this.getMonthName(month)}`;
            }
        }

        // Update tabs
        TabManager.updateTabLabels();

        // Update current tab content
        TabManager.refreshCurrentTab();
    },

    getTranslation(key) {
        const keys = key.split('.');
        let value = DashboardState.translations;

        for (const k of keys) {
            if (value && typeof value === 'object') {
                value = value[k];
            } else {
                return key;
            }
        }

        if (value && typeof value === 'object' && value[DashboardState.currentLang]) {
            return value[DashboardState.currentLang];
        }

        return key;
    },

    getMonthName(month) {
        const months = {
            'january': { ko: '1월', en: 'January', vi: 'Tháng 1' },
            'february': { ko: '2월', en: 'February', vi: 'Tháng 2' },
            'march': { ko: '3월', en: 'March', vi: 'Tháng 3' },
            'april': { ko: '4월', en: 'April', vi: 'Tháng 4' },
            'may': { ko: '5월', en: 'May', vi: 'Tháng 5' },
            'june': { ko: '6월', en: 'June', vi: 'Tháng 6' },
            'july': { ko: '7월', en: 'July', vi: 'Tháng 7' },
            'august': { ko: '8월', en: 'August', vi: 'Tháng 8' },
            'september': { ko: '9월', en: 'September', vi: 'Tháng 9' },
            'october': { ko: '10월', en: 'October', vi: 'Tháng 10' },
            'november': { ko: '11월', en: 'November', vi: 'Tháng 11' },
            'december': { ko: '12월', en: 'December', vi: 'Tháng 12' }
        };

        const monthLower = month.toLowerCase();
        return months[monthLower] ? months[monthLower][DashboardState.currentLang] : month;
    }
};

// ==================== Tab Manager ====================
const TabManager = {
    tabs: ['summary', 'position', 'individual', 'conditions', 'orgchart'],

    renderTabs() {
        const tabsContainer = document.getElementById('dashboardTabs');
        const contentContainer = document.getElementById('dashboardTabContent');

        tabsContainer.innerHTML = '';
        contentContainer.innerHTML = '';

        this.tabs.forEach((tabId, index) => {
            // Create tab button
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.role = 'presentation';

            const button = document.createElement('button');
            button.className = `nav-link ${index === 0 ? 'active' : ''}`;
            button.id = `${tabId}-tab`;
            button.dataset.bsToggle = 'tab';
            button.dataset.bsTarget = `#${tabId}`;
            button.type = 'button';
            button.role = 'tab';
            button.textContent = LanguageManager.getTranslation(`tabs.${tabId}`);

            button.addEventListener('click', () => this.showTab(tabId));

            li.appendChild(button);
            tabsContainer.appendChild(li);

            // Create tab panel
            const panel = document.createElement('div');
            panel.className = `tab-pane fade ${index === 0 ? 'show active' : ''}`;
            panel.id = tabId;
            panel.role = 'tabpanel';

            contentContainer.appendChild(panel);
        });
    },

    showTab(tabId) {
        DashboardState.currentTab = tabId;

        // Update tab buttons
        document.querySelectorAll('.nav-link').forEach(btn => {
            const isActive = btn.dataset.bsTarget === `#${tabId}`;
            btn.classList.toggle('active', isActive);
        });

        // Update tab panels
        document.querySelectorAll('.tab-pane').forEach(panel => {
            const isActive = panel.id === tabId;
            panel.classList.toggle('show', isActive);
            panel.classList.toggle('active', isActive);
        });

        // Render tab content
        this.renderTabContent(tabId);
    },

    renderTabContent(tabId) {
        const panel = document.getElementById(tabId);

        if (!panel) {
            console.error(`Tab panel not found: ${tabId}`);
            return;
        }

        try {
            switch(tabId) {
                case 'summary':
                    panel.innerHTML = SummaryTab.render();
                    SummaryTab.init();
                    break;
                case 'position':
                    panel.innerHTML = PositionTab.render();
                    PositionTab.init();
                    break;
                case 'individual':
                    panel.innerHTML = IndividualTab.render();
                    IndividualTab.init();
                    break;
                case 'conditions':
                    panel.innerHTML = ConditionsTab.render();
                    ConditionsTab.init();
                    break;
                case 'orgchart':
                    panel.innerHTML = OrgChartTab.render();
                    OrgChartTab.init();
                    break;
            }
        } catch (error) {
            console.error(`Error rendering tab ${tabId}:`, error);
            panel.innerHTML = '<div class="alert alert-danger">Error loading tab content</div>';
        }
    },

    updateTabLabels() {
        this.tabs.forEach(tabId => {
            const button = document.getElementById(`${tabId}-tab`);
            if (button) {
                button.textContent = LanguageManager.getTranslation(`tabs.${tabId}`);
            }
        });
    },

    refreshCurrentTab() {
        this.renderTabContent(DashboardState.currentTab);
    }
};

// ==================== Summary Tab ====================
const SummaryTab = {
    render() {
        const stats = DashboardState.stats;

        return `
            <div class="container-fluid mt-3">
                <div class="row">
                    <!-- Stats Cards -->
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-users stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.cards.totalEmployees')}</div>
                            <div class="stat-value text-primary">${stats.totalEmployees}</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-check-circle stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.cards.paidEmployees')}</div>
                            <div class="stat-value text-success">${stats.paidEmployees}</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-percentage stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.cards.paymentRate')}</div>
                            <div class="stat-value text-info">${stats.paymentRate.toFixed(1)}%</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-coins stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.cards.totalAmount')}</div>
                            <div class="stat-value text-warning">${formatNumber(stats.totalAmount)} VND</div>
                        </div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <canvas id="typeChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <canvas id="positionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        // Render charts
        this.renderTypeChart();
        this.renderPositionChart();
    },

    renderTypeChart() {
        const ctx = document.getElementById('typeChart');
        if (!ctx) return;

        // Destroy existing chart
        if (DashboardState.charts.typeChart) {
            DashboardState.charts.typeChart.destroy();
        }

        // Prepare data
        const typeData = this.prepareTypeData();

        DashboardState.charts.typeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: typeData.labels,
                datasets: [{
                    data: typeData.data,
                    backgroundColor: ['#0066cc', '#28a745', '#ffc107']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: LanguageManager.getTranslation('charts.byType')
                    }
                }
            }
        });
    },

    renderPositionChart() {
        const ctx = document.getElementById('positionChart');
        if (!ctx) return;

        // Destroy existing chart
        if (DashboardState.charts.positionChart) {
            DashboardState.charts.positionChart.destroy();
        }

        // Prepare data
        const positionData = this.preparePositionData();

        DashboardState.charts.positionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: positionData.labels,
                datasets: [{
                    label: LanguageManager.getTranslation('charts.paidCount'),
                    data: positionData.data,
                    backgroundColor: '#0066cc'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: LanguageManager.getTranslation('charts.byPosition')
                    }
                }
            }
        });
    },

    prepareTypeData() {
        const typeCounts = {};
        DashboardState.data.forEach(emp => {
            const type = emp.type || 'Unknown';
            typeCounts[type] = (typeCounts[type] || 0) + 1;
        });

        return {
            labels: Object.keys(typeCounts),
            data: Object.values(typeCounts)
        };
    },

    preparePositionData() {
        const positionCounts = {};
        DashboardState.data.forEach(emp => {
            if (emp.amount > 0) {
                const position = emp.position || 'Unknown';
                positionCounts[position] = (positionCounts[position] || 0) + 1;
            }
        });

        // Sort and take top 10
        const sorted = Object.entries(positionCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        return {
            labels: sorted.map(item => item[0]),
            data: sorted.map(item => item[1])
        };
    }
};

// ==================== Position Tab ====================
const PositionTab = {
    render() {
        return `
            <div class="container-fluid mt-3">
                <div class="data-table">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>${LanguageManager.getTranslation('table.position')}</th>
                                <th>${LanguageManager.getTranslation('table.type')}</th>
                                <th>${LanguageManager.getTranslation('table.totalCount')}</th>
                                <th>${LanguageManager.getTranslation('table.paidCount')}</th>
                                <th>${LanguageManager.getTranslation('table.paymentRate')}</th>
                                <th>${LanguageManager.getTranslation('table.totalAmount')}</th>
                            </tr>
                        </thead>
                        <tbody id="positionTableBody">
                            <!-- Data will be inserted here -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    init() {
        this.renderTable();
    },

    renderTable() {
        const tbody = document.getElementById('positionTableBody');
        if (!tbody) return;

        const positionData = this.prepareTableData();

        tbody.innerHTML = positionData.map(row => `
            <tr>
                <td>${row.position}</td>
                <td><span class="badge bg-${this.getTypeBadgeColor(row.type)}">${row.type}</span></td>
                <td>${row.total}</td>
                <td>${row.paid}</td>
                <td>${row.rate.toFixed(1)}%</td>
                <td>${formatNumber(row.amount)} VND</td>
            </tr>
        `).join('');
    },

    prepareTableData() {
        const positionMap = {};

        DashboardState.data.forEach(emp => {
            const position = emp.position || 'Unknown';
            if (!positionMap[position]) {
                positionMap[position] = {
                    position: position,
                    type: emp.type,
                    total: 0,
                    paid: 0,
                    amount: 0
                };
            }

            positionMap[position].total++;
            if (emp.amount > 0) {
                positionMap[position].paid++;
                positionMap[position].amount += emp.amount;
            }
        });

        return Object.values(positionMap).map(item => ({
            ...item,
            rate: item.total > 0 ? (item.paid / item.total * 100) : 0
        })).sort((a, b) => b.amount - a.amount);
    },

    getTypeBadgeColor(type) {
        const colors = {
            'TYPE-1': 'primary',
            'TYPE-2': 'success',
            'TYPE-3': 'warning'
        };
        return colors[type] || 'secondary';
    }
};

// ==================== Individual Tab ====================
const IndividualTab = {
    render() {
        return `
            <div class="container-fluid mt-3">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <input type="text" id="individualSearch" class="form-control"
                               placeholder="${LanguageManager.getTranslation('individual.searchPlaceholder')}">
                    </div>
                    <div class="col-md-3">
                        <select id="individualFilter" class="form-select">
                            <option value="all">${LanguageManager.getTranslation('individual.all')}</option>
                            <option value="paid">${LanguageManager.getTranslation('individual.paidOnly')}</option>
                            <option value="unpaid">${LanguageManager.getTranslation('individual.unpaidOnly')}</option>
                        </select>
                    </div>
                </div>
                <div class="data-table">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>${LanguageManager.getTranslation('table.employeeId')}</th>
                                <th>${LanguageManager.getTranslation('table.name')}</th>
                                <th>${LanguageManager.getTranslation('table.position')}</th>
                                <th>${LanguageManager.getTranslation('table.type')}</th>
                                <th>${LanguageManager.getTranslation('table.attendanceRate')}</th>
                                <th>${LanguageManager.getTranslation('table.aqlFailure')}</th>
                                <th>${LanguageManager.getTranslation('table.5prsScore')}</th>
                                <th>${LanguageManager.getTranslation('table.amount')}</th>
                                <th>${LanguageManager.getTranslation('table.action')}</th>
                            </tr>
                        </thead>
                        <tbody id="individualTableBody">
                            <!-- Data will be inserted here -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    init() {
        this.renderTable();
        this.setupFilters();
    },

    renderTable() {
        const tbody = document.getElementById('individualTableBody');
        if (!tbody) return;

        const employees = DashboardState.data || [];
        const filterValue = document.getElementById('individualFilter')?.value || 'all';
        const searchValue = document.getElementById('individualSearch')?.value?.toLowerCase() || '';

        // Filter employees
        let filtered = employees.filter(emp => {
            // Filter by payment status
            if (filterValue === 'paid' && emp.amount <= 0) return false;
            if (filterValue === 'unpaid' && emp.amount > 0) return false;

            // Filter by search
            if (searchValue) {
                const searchMatch =
                    emp.employee_id?.toString().includes(searchValue) ||
                    emp.name?.toLowerCase().includes(searchValue) ||
                    emp.position?.toLowerCase().includes(searchValue);
                if (!searchMatch) return false;
            }

            return true;
        });

        // Sort by amount descending
        filtered.sort((a, b) => (b.amount || 0) - (a.amount || 0));

        tbody.innerHTML = filtered.map(emp => `
            <tr>
                <td>${emp.employee_id || ''}</td>
                <td>${emp.name || ''}</td>
                <td>${emp.position || ''}</td>
                <td><span class="badge bg-${this.getTypeBadgeColor(emp.type)}">${emp.type || ''}</span></td>
                <td>${emp.attendance_rate ? emp.attendance_rate.toFixed(1) + '%' : '-'}</td>
                <td>${emp.aql_failure ? '❌' : '✅'}</td>
                <td>${emp['5prs_score'] || '-'}</td>
                <td class="${emp.amount > 0 ? 'text-success fw-bold' : ''}">
                    ${formatNumber(emp.amount || 0)} VND
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="ModalManager.showEmployeeModal('${emp.employee_id}')">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    },

    setupFilters() {
        const searchInput = document.getElementById('individualSearch');
        const filterSelect = document.getElementById('individualFilter');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.renderTable());
        }

        if (filterSelect) {
            filterSelect.addEventListener('change', () => this.renderTable());
        }
    },

    getTypeBadgeColor(type) {
        const colors = {
            'TYPE-1': 'primary',
            'TYPE-2': 'success',
            'TYPE-3': 'warning'
        };
        return colors[type] || 'secondary';
    }
};

// ==================== Conditions Tab ====================
const ConditionsTab = {
    render() {
        return `
            <div class="container-fluid mt-3">
                <div class="row">
                    <div class="col-md-12">
                        <h5>${LanguageManager.getTranslation('conditions.title')}</h5>
                        <div id="conditionsContent">
                            <!-- Conditions will be rendered here -->
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <canvas id="conditionsChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="data-table">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>${LanguageManager.getTranslation('conditions.condition')}</th>
                                        <th>${LanguageManager.getTranslation('conditions.passRate')}</th>
                                        <th>${LanguageManager.getTranslation('conditions.passed')}</th>
                                        <th>${LanguageManager.getTranslation('conditions.failed')}</th>
                                    </tr>
                                </thead>
                                <tbody id="conditionsTableBody">
                                    <!-- Data will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        this.analyzeConditions();
        this.renderChart();
    },

    analyzeConditions() {
        const tbody = document.getElementById('conditionsTableBody');
        if (!tbody) return;

        const conditions = {};
        const employees = DashboardState.data || [];

        // Analyze each employee's conditions
        employees.forEach(emp => {
            if (emp.condition_results && Array.isArray(emp.condition_results)) {
                emp.condition_results.forEach(result => {
                    const condName = result.condition || 'Unknown';
                    if (!conditions[condName]) {
                        conditions[condName] = { passed: 0, failed: 0, total: 0 };
                    }
                    conditions[condName].total++;
                    if (result.met) {
                        conditions[condName].passed++;
                    } else {
                        conditions[condName].failed++;
                    }
                });
            }
        });

        // Render table
        const conditionsList = Object.entries(conditions).map(([name, stats]) => ({
            name,
            ...stats,
            passRate: stats.total > 0 ? (stats.passed / stats.total * 100) : 0
        }));

        tbody.innerHTML = conditionsList.map(cond => `
            <tr>
                <td>${cond.name}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar bg-success" style="width: ${cond.passRate}%">
                            ${cond.passRate.toFixed(1)}%
                        </div>
                    </div>
                </td>
                <td class="text-success">${cond.passed}</td>
                <td class="text-danger">${cond.failed}</td>
            </tr>
        `).join('');

        this.conditionsData = conditionsList;
    },

    renderChart() {
        const ctx = document.getElementById('conditionsChart');
        if (!ctx || !this.conditionsData) return;

        // Destroy existing chart
        if (DashboardState.charts.conditionsChart) {
            DashboardState.charts.conditionsChart.destroy();
        }

        DashboardState.charts.conditionsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.conditionsData.map(c => c.name),
                datasets: [{
                    label: LanguageManager.getTranslation('conditions.passRate'),
                    data: this.conditionsData.map(c => c.passRate),
                    backgroundColor: this.conditionsData.map(c =>
                        c.passRate >= 80 ? '#28a745' :
                        c.passRate >= 60 ? '#ffc107' : '#dc3545'
                    )
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: LanguageManager.getTranslation('conditions.chartTitle')
                    }
                }
            }
        });
    }
};

// ==================== OrgChart Tab ====================
const OrgChartTab = {
    render() {
        return `
            <div class="container-fluid mt-3">
                <h5>${LanguageManager.getTranslation('orgchart.title')}</h5>
                <div class="row">
                    <div class="col-md-12">
                        <div id="orgChartContainer" class="org-chart-container">
                            <!-- Org chart will be rendered here -->
                        </div>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="data-table">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>${LanguageManager.getTranslation('table.managerName')}</th>
                                        <th>${LanguageManager.getTranslation('table.position')}</th>
                                        <th>${LanguageManager.getTranslation('table.teamSize')}</th>
                                        <th>${LanguageManager.getTranslation('table.teamPaidRate')}</th>
                                        <th>${LanguageManager.getTranslation('table.totalTeamAmount')}</th>
                                    </tr>
                                </thead>
                                <tbody id="orgChartTableBody">
                                    <!-- Data will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        this.buildOrgChart();
        this.renderManagerTable();
    },

    buildOrgChart() {
        const container = document.getElementById('orgChartContainer');
        if (!container) return;

        const type1Employees = (DashboardState.data || []).filter(emp => emp.type === 'TYPE-1');

        // Build hierarchy
        const hierarchy = this.buildHierarchy(type1Employees);

        // Render org chart
        container.innerHTML = `
            <div class="org-chart">
                ${this.renderOrgNode(hierarchy)}
            </div>
        `;
    },

    buildHierarchy(employees) {
        const employeeMap = {};
        const rootNodes = [];

        // Create employee map
        employees.forEach(emp => {
            employeeMap[emp.employee_id] = {
                ...emp,
                subordinates: []
            };
        });

        // Build hierarchy
        employees.forEach(emp => {
            if (emp.boss_id && employeeMap[emp.boss_id]) {
                employeeMap[emp.boss_id].subordinates.push(employeeMap[emp.employee_id]);
            } else {
                rootNodes.push(employeeMap[emp.employee_id]);
            }
        });

        return rootNodes;
    },

    renderOrgNode(nodes) {
        if (!nodes || nodes.length === 0) return '';

        return nodes.map(node => `
            <div class="org-node">
                <div class="org-card ${node.amount > 0 ? 'paid' : 'unpaid'}"
                     onclick="ModalManager.showEmployeeModal('${node.employee_id}')">
                    <div class="org-name">${node.name}</div>
                    <div class="org-position">${node.position}</div>
                    <div class="org-amount">${formatNumber(node.amount || 0)} VND</div>
                </div>
                ${node.subordinates.length > 0 ? `
                    <div class="org-children">
                        ${this.renderOrgNode(node.subordinates)}
                    </div>
                ` : ''}
            </div>
        `).join('');
    },

    renderManagerTable() {
        const tbody = document.getElementById('orgChartTableBody');
        if (!tbody) return;

        const type1Employees = (DashboardState.data || []).filter(emp => emp.type === 'TYPE-1');
        const managerStats = [];

        type1Employees.forEach(manager => {
            const teamMembers = this.getTeamMembers(manager.employee_id);
            const paidMembers = teamMembers.filter(m => m.amount > 0);
            const totalAmount = teamMembers.reduce((sum, m) => sum + (m.amount || 0), 0);

            managerStats.push({
                name: manager.name,
                position: manager.position,
                teamSize: teamMembers.length,
                paidRate: teamMembers.length > 0 ? (paidMembers.length / teamMembers.length * 100) : 0,
                totalAmount: totalAmount
            });
        });

        tbody.innerHTML = managerStats.map(stat => `
            <tr>
                <td>${stat.name}</td>
                <td>${stat.position}</td>
                <td>${stat.teamSize}</td>
                <td>${stat.paidRate.toFixed(1)}%</td>
                <td>${formatNumber(stat.totalAmount)} VND</td>
            </tr>
        `).join('');
    },

    getTeamMembers(managerId) {
        const members = [];
        const employees = DashboardState.data || [];

        employees.forEach(emp => {
            if (emp.boss_id === managerId) {
                members.push(emp);
                // Recursively get subordinates
                members.push(...this.getTeamMembers(emp.employee_id));
            }
        });

        return members;
    }
};

// ==================== Modal Manager ====================
const ModalManager = {
    showEmployeeModal(employeeId) {
        const employee = DashboardState.data.find(emp => emp.employee_id == employeeId);
        if (!employee) return;

        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="employeeModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                ${LanguageManager.getTranslation('modal.employeeDetails')}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>${LanguageManager.getTranslation('modal.basicInfo')}</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.employeeId')}:</th>
                                            <td>${employee.employee_id}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.name')}:</th>
                                            <td>${employee.name}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.position')}:</th>
                                            <td>${employee.position}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.type')}:</th>
                                            <td><span class="badge bg-primary">${employee.type}</span></td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>${LanguageManager.getTranslation('modal.performanceInfo')}</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.attendanceRate')}:</th>
                                            <td>${employee.attendance_rate ? employee.attendance_rate.toFixed(1) + '%' : '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.aqlFailure')}:</th>
                                            <td>${employee.aql_failure ? '❌ Failed' : '✅ Passed'}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.5prsScore')}:</th>
                                            <td>${employee['5prs_score'] || '-'}</td>
                                        </tr>
                                        <tr>
                                            <th>${LanguageManager.getTranslation('table.amount')}:</th>
                                            <td class="${employee.amount > 0 ? 'text-success fw-bold' : ''}">
                                                ${formatNumber(employee.amount || 0)} VND
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            ${this.renderConditionsTable(employee)}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                ${LanguageManager.getTranslation('modal.close')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('employeeModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
        modal.show();
    },

    renderConditionsTable(employee) {
        if (!employee.condition_results || !Array.isArray(employee.condition_results)) {
            return '';
        }

        return `
            <div class="mt-3">
                <h6>${LanguageManager.getTranslation('modal.conditionsDetail')}</h6>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>${LanguageManager.getTranslation('conditions.condition')}</th>
                            <th>${LanguageManager.getTranslation('conditions.status')}</th>
                            <th>${LanguageManager.getTranslation('conditions.value')}</th>
                            <th>${LanguageManager.getTranslation('conditions.threshold')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${employee.condition_results.map(result => `
                            <tr>
                                <td>${result.condition}</td>
                                <td>${result.met ?
                                    '<span class="badge bg-success">Pass</span>' :
                                    '<span class="badge bg-danger">Fail</span>'
                                }</td>
                                <td>${result.value || '-'}</td>
                                <td>${result.threshold || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    showConditionModal(conditionName) {
        // Get condition details from position matrix
        const conditionDef = DashboardState.positionMatrix?.conditions?.[conditionName];
        if (!conditionDef) return;

        const modalHtml = `
            <div class="modal fade" id="conditionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header unified-modal-header">
                            <h5 class="modal-title unified-modal-title">
                                ${conditionName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>${LanguageManager.getTranslation('modal.description')}:</strong></p>
                            <p>${conditionDef.description || '-'}</p>

                            <p><strong>${LanguageManager.getTranslation('modal.threshold')}:</strong></p>
                            <p>${conditionDef.threshold || '-'}</p>

                            <p><strong>${LanguageManager.getTranslation('modal.formula')}:</strong></p>
                            <p><code>${conditionDef.formula || '-'}</code></p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                ${LanguageManager.getTranslation('modal.close')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('conditionModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('conditionModal'));
        modal.show();
    }
};

// ==================== Utility Functions ====================
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function showError(message) {
    const container = document.querySelector('.container-fluid');
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

function setupEventListeners() {
    // Window resize handler
    window.addEventListener('resize', () => {
        // Redraw charts if needed
        Object.values(DashboardState.charts).forEach(chart => {
            if (chart) chart.resize();
        });
    });

    // Load saved language preference
    const savedLang = localStorage.getItem('dashboardLang');
    if (savedLang && ['ko', 'en', 'vi'].includes(savedLang)) {
        LanguageManager.setLanguage(savedLang);
    }
}

// ==================== Original Modal Functions ====================
// These functions maintain compatibility with the original dashboard

function showTotalWorkingDaysDetails() {
    let workDays = [];
    let holidays = [];
    let totalWorkingDays = 13; // Default fallback

    if (window.excelDashboardData && window.excelDashboardData.attendance) {
        const dailyData = window.excelDashboardData.attendance.daily_data;
        totalWorkingDays = window.excelDashboardData.attendance.total_working_days;

        // Analyze daily data
        for (let day = 1; day <= 19; day++) {
            if (dailyData && dailyData[day]) {
                if (dailyData[day].is_working_day) {
                    workDays.push(day);
                } else {
                    holidays.push(day);
                }
            } else {
                holidays.push(day);
            }
        }
    } else {
        // Fallback: default working days
        workDays = [2,3,4,5,6,9,10,11,12,13,16,17,18,19];
        holidays = [1,7,8,14,15];
    }

    // Show modal with calendar
    ModalManager.showWorkingDaysModal(workDays, holidays, totalWorkingDays);
}

function showZeroWorkingDaysDetails() {
    const zeroWorkingEmployees = (DashboardState.data || []).filter(emp =>
        emp.actual_working_days === 0 || emp['Working Days'] === 0
    );
    ModalManager.showZeroWorkingDaysModal(zeroWorkingEmployees);
}

function showAbsentWithoutInformDetails() {
    const absentEmployees = (DashboardState.data || []).filter(emp => {
        const unapproved = parseFloat(emp.unapproved_absences || emp['Unapproved Absences'] || 0);
        return unapproved >= 1;
    });
    ModalManager.showAbsentEmployeesModal(absentEmployees);
}

function showMinimumDaysDetails() {
    const employees = DashboardState.data || [];
    const filteredEmployees = employees.filter(emp => {
        const workingDays = emp.actual_working_days || emp['Working Days'] || 0;
        return workingDays > 0 && workingDays < 10;
    });
    ModalManager.showMinimumDaysModal(filteredEmployees);
}

// Extend ModalManager with additional modal functions
ModalManager.showWorkingDaysModal = function(workDays, holidays, totalDays) {
    const modalHtml = `
        <div class="modal fade" id="workingDaysModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header unified-modal-header">
                        <h5 class="modal-title unified-modal-title">
                            ${LanguageManager.getTranslation('modal.workingDaysTitle') || '근무일 상세'}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="calendar-grid">
                            ${[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19].map(day => `
                                <div class="calendar-day ${workDays.includes(day) ? 'work-day' : 'no-data'}">
                                    <div class="day-number">${day}</div>
                                    <div class="day-weekday">${this.getWeekdayName(day)}</div>
                                    ${workDays.includes(day) ? '<div class="day-icon">💼</div>' : ''}
                                </div>
                            `).join('')}
                        </div>
                        <div class="mt-3">
                            <p><strong>총 근무일수:</strong> ${totalDays}일</p>
                            <p><strong>근무일:</strong> ${workDays.join(', ')}일</p>
                            <p><strong>휴일:</strong> ${holidays.join(', ')}일</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    const existingModal = document.getElementById('workingDaysModal');
    if (existingModal) existingModal.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('workingDaysModal'));
    modal.show();
};

ModalManager.getWeekdayName = function(day) {
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    // September 1, 2025 is Monday
    const firstDayOfWeek = 1;
    const dayIndex = (firstDayOfWeek + day - 1) % 7;
    return weekdays[dayIndex];
};

ModalManager.showZeroWorkingDaysModal = function(employees) {
    const modalHtml = `
        <div class="modal fade" id="zeroWorkingModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header unified-modal-header">
                        <h5 class="modal-title unified-modal-title">
                            근무일 0일 직원 목록 (${employees.length}명)
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>사원번호</th>
                                    <th>이름</th>
                                    <th>직급</th>
                                    <th>TYPE</th>
                                    <th>출근율</th>
                                    <th>인센티브</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${employees.map(emp => `
                                    <tr>
                                        <td>${emp.employee_id || emp.emp_no}</td>
                                        <td>${emp.name}</td>
                                        <td>${emp.position}</td>
                                        <td><span class="badge bg-primary">${emp.type}</span></td>
                                        <td>0%</td>
                                        <td class="text-danger">0 VND</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    const existingModal = document.getElementById('zeroWorkingModal');
    if (existingModal) existingModal.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('zeroWorkingModal'));
    modal.show();
};

// Export for debugging and global access
window.DashboardState = DashboardState;
window.LanguageManager = LanguageManager;
window.ModalManager = ModalManager;
window.showTotalWorkingDaysDetails = showTotalWorkingDaysDetails;
window.showZeroWorkingDaysDetails = showZeroWorkingDaysDetails;
window.showAbsentWithoutInformDetails = showAbsentWithoutInformDetails;
window.showMinimumDaysDetails = showMinimumDaysDetails;