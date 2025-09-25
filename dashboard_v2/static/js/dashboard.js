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
        const title = this.getTranslation('headers.title');
        document.getElementById('dashboardTitle').textContent = title;

        // Update subtitle
        const month = DashboardState.config.month;
        const year = DashboardState.config.year;
        const subtitle = this.getTranslation('headers.subtitle')
            .replace('{month}', this.getMonthName(month))
            .replace('{year}', year);
        document.getElementById('dashboardSubtitle').textContent = subtitle;

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
                            <div class="stat-label">${LanguageManager.getTranslation('summary.totalEmployees')}</div>
                            <div class="stat-value text-primary">${stats.totalEmployees}</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-check-circle stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.paidEmployees')}</div>
                            <div class="stat-value text-success">${stats.paidEmployees}</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-percentage stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.paymentRate')}</div>
                            <div class="stat-value text-info">${stats.paymentRate.toFixed(1)}%</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card">
                            <i class="fas fa-coins stat-icon"></i>
                            <div class="stat-label">${LanguageManager.getTranslation('summary.totalAmount')}</div>
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

// Placeholder for other tabs
const IndividualTab = {
    render() {
        return '<div class="p-4">Individual Details - Coming Soon</div>';
    },
    init() {}
};

const ConditionsTab = {
    render() {
        return '<div class="p-4">Conditions - Coming Soon</div>';
    },
    init() {}
};

const OrgChartTab = {
    render() {
        return '<div class="p-4">Organization Chart - Coming Soon</div>';
    },
    init() {}
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

// Export for debugging
window.DashboardState = DashboardState;
window.LanguageManager = LanguageManager;