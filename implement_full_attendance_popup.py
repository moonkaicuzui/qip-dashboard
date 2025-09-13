#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implement Card #9 (만근자) popup with detailed full attendance analytics
Includes attendance trends, team distribution, and incentive calculations
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random

def generate_full_attendance_popup_code():
    """Generate JavaScript code for full attendance popup"""
    
    js_code = """
    // Card #9: 만근자 상세 분석 팝업 구현
    function createFullAttendanceModal() {
        console.log('Creating full attendance modal...');
        
        // Get full attendance data
        const attendanceData = getFullAttendanceData();
        
        // Create modal if it doesn't exist
        if (!document.getElementById('modal-full-attendance-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-full-attendance-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>만근자 상세 현황</h2>
                        <span class="close" onclick="closeModal('modal-full-attendance-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">당월 만근자</h4>
                                <div style="font-size: 36px; font-weight: bold;">8명</div>
                                <div style="opacity: 0.8;">전체의 2.0%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">전월 대비</h4>
                                <div style="font-size: 36px; font-weight: bold;">-297명</div>
                                <div style="opacity: 0.8;">▼ 97.4%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 출근율</h4>
                                <div style="font-size: 36px; font-weight: bold;">96.9%</div>
                                <div style="opacity: 0.8;">전체 평균</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">만근 보너스</h4>
                                <div style="font-size: 36px; font-weight: bold;">$800</div>
                                <div style="opacity: 0.8;">총 지급액</div>
                            </div>
                        </div>
                        
                        <!-- Alert Box for Dramatic Decrease -->
                        <div class="alert-section" style="background: #ffebee; border-left: 4px solid #f44336; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                            <h4 style="color: #c62828; margin: 0 0 10px 0;">⚠️ 만근율 급감 경고</h4>
                            <p style="color: #d32f2f; margin: 0;">
                                전월 대비 만근자가 305명에서 8명으로 급감했습니다 (-97.4%). 
                                이는 8월 데이터가 16일까지만 집계되었기 때문일 수 있습니다.
                                월말 최종 집계 후 재확인이 필요합니다.
                            </p>
                        </div>
                        
                        <!-- Charts Section -->
                        <div class="charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                            <!-- Monthly Trend Chart -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">월별 만근율 추이</h3>
                                <canvas id="full-attendance-trend-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Team Distribution Chart -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">팀별 만근자 분포</h3>
                                <canvas id="full-attendance-team-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Attendance Rate Distribution -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">출근율 구간별 인원</h3>
                                <canvas id="attendance-rate-distribution-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Achievement Factors -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">만근 달성 요인</h3>
                                <canvas id="achievement-factors-chart" style="max-height: 300px;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Full Attendance List -->
                        <div class="table-section" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <h3 style="margin: 0 0 20px 0; color: #333;">만근자 명단</h3>
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: #f8f9fa;">
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">이름</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">팀</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">직급</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">근무일수</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">출근율</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">연속 만근</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">보너스</th>
                                        </tr>
                                    </thead>
                                    <tbody id="full-attendance-table-body">
                                        <!-- Dynamic content will be inserted here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Near Perfect Attendance Section -->
                        <div class="table-section" style="background: #f0f8ff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="margin: 0 0 20px 0; color: #333;">준만근자 (95% 이상)</h3>
                            <p style="color: #666; margin-bottom: 15px;">1-2일만 결근한 직원들로, 다음 달 만근 가능성이 높습니다.</p>
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: #e3f2fd;">
                                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #90caf9;">이름</th>
                                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #90caf9;">팀</th>
                                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #90caf9;">출근율</th>
                                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #90caf9;">결근일수</th>
                                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #90caf9;">개선 필요사항</th>
                                        </tr>
                                    </thead>
                                    <tbody id="near-perfect-table-body">
                                        <!-- Dynamic content will be inserted here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Improvement Recommendations -->
                        <div class="recommendations-section" style="background: #e8f5e9; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #4caf50;">
                            <h3 style="margin: 0 0 15px 0; color: #2e7d32;">📈 만근율 개선 제안</h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                                <div>
                                    <h4 style="color: #388e3c; margin-bottom: 10px;">단기 개선 방안</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>출근 인센티브 강화 (만근 보너스 상향)</li>
                                        <li>팀별 만근 경쟁 시스템 도입</li>
                                        <li>근태 관리 시스템 개선</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style="color: #388e3c; margin-bottom: 10px;">장기 개선 방안</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>근무 환경 개선 프로그램</li>
                                        <li>유연 근무제 도입 검토</li>
                                        <li>건강 관리 프로그램 강화</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        // Initialize charts
        setTimeout(() => {
            createFullAttendanceCharts();
            populateFullAttendanceTables();
        }, 100);
    }
    
    function getFullAttendanceData() {
        // Generate sample full attendance data
        return {
            total: 8,
            rate: 2.0,
            previousMonth: 305,
            avgAttendanceRate: 96.9,
            totalBonus: 800,
            monthlyData: [
                { month: '2025-03', count: 285, rate: 73.1 },
                { month: '2025-04', count: 292, rate: 74.9 },
                { month: '2025-05', count: 310, rate: 79.5 },
                { month: '2025-06', count: 298, rate: 76.4 },
                { month: '2025-07', count: 305, rate: 78.2 },
                { month: '2025-08', count: 8, rate: 2.0 }  // Partial month data
            ],
            teamDistribution: {
                'ASSEMBLY': 2,
                'STITCHING': 1,
                'BOTTOM': 1,
                'MTL': 1,
                'OSC': 1,
                'AQL': 1,
                'QA': 1
            },
            rateDistribution: {
                '100%': 8,
                '95-99%': 43,
                '90-94%': 87,
                '85-89%': 124,
                '80-84%': 89,
                '<80%': 40
            },
            achievementFactors: {
                '건강 관리': 35,
                '근무 의욕': 30,
                '팀 분위기': 20,
                '인센티브': 15
            },
            fullAttendanceList: [
                { name: 'Nguyen Van A', team: 'ASSEMBLY', position: 'QIP', days: 16, rate: '100%', consecutive: 3, bonus: '$100' },
                { name: 'Tran Thi B', team: 'ASSEMBLY', position: 'INSPECTOR', days: 16, rate: '100%', consecutive: 2, bonus: '$100' },
                { name: 'Le Van C', team: 'STITCHING', position: 'QIP', days: 16, rate: '100%', consecutive: 1, bonus: '$100' },
                { name: 'Pham Thi D', team: 'BOTTOM', position: 'INSPECTOR', days: 16, rate: '100%', consecutive: 4, bonus: '$100' },
                { name: 'Hoang Van E', team: 'MTL', position: 'METAL_INSPECTOR', days: 16, rate: '100%', consecutive: 2, bonus: '$100' },
                { name: 'Vo Thi F', team: 'OSC', position: 'OUT_SOLE_CEMENT', days: 16, rate: '100%', consecutive: 1, bonus: '$100' },
                { name: 'Dinh Van G', team: 'AQL', position: 'AQL_INSPECTOR', days: 16, rate: '100%', consecutive: 5, bonus: '$100' },
                { name: 'Bui Thi H', team: 'QA', position: 'QA_1ST', days: 16, rate: '100%', consecutive: 3, bonus: '$100' }
            ],
            nearPerfectList: [
                { name: 'Do Van I', team: 'ASSEMBLY', rate: '96.9%', absenceDays: 1, improvement: '건강 관리' },
                { name: 'Ngo Thi J', team: 'STITCHING', rate: '96.9%', absenceDays: 1, improvement: '가족 상황' },
                { name: 'Ly Van K', team: 'BOTTOM', rate: '95.3%', absenceDays: 2, improvement: '교통 문제' },
                { name: 'Mai Thi L', team: 'AQL', rate: '95.3%', absenceDays: 2, improvement: '건강 관리' },
                { name: 'Truong Van M', team: 'QA', rate: '95.3%', absenceDays: 2, improvement: '개인 사유' }
            ]
        };
    }
    
    function createFullAttendanceCharts() {
        const data = getFullAttendanceData();
        
        // Destroy existing charts if they exist
        if (window.fullAttendanceCharts) {
            Object.values(window.fullAttendanceCharts).forEach(chart => chart.destroy());
        }
        window.fullAttendanceCharts = {};
        
        // 1. Monthly Trend Chart
        const trendCtx = document.getElementById('full-attendance-trend-chart');
        if (trendCtx) {
            window.fullAttendanceCharts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: data.monthlyData.map(d => d.month),
                    datasets: [{
                        label: '만근자 수',
                        data: data.monthlyData.map(d => d.count),
                        borderColor: '#48bb78',
                        backgroundColor: 'rgba(72, 187, 120, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y'
                    }, {
                        label: '만근율 (%)',
                        data: data.monthlyData.map(d => d.rate),
                        borderColor: '#4299e1',
                        backgroundColor: 'rgba(66, 153, 225, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        annotation: {
                            annotations: {
                                line1: {
                                    type: 'line',
                                    yMin: 8,
                                    yMax: 8,
                                    borderColor: 'rgb(255, 99, 132)',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    label: {
                                        content: '8월 급감',
                                        enabled: true,
                                        position: 'end'
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: '만근자 수' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: { display: true, text: '만근율 (%)' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }
        
        // 2. Team Distribution Chart
        const teamCtx = document.getElementById('full-attendance-team-chart');
        if (teamCtx) {
            window.fullAttendanceCharts.team = new Chart(teamCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.teamDistribution),
                    datasets: [{
                        label: '만근자 수',
                        data: Object.values(data.teamDistribution),
                        backgroundColor: [
                            '#667eea', '#f56565', '#48bb78', '#ed8936',
                            '#9f7aea', '#38b2ac', '#ed64a6', '#ecc94b'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }
        
        // 3. Attendance Rate Distribution
        const rateCtx = document.getElementById('attendance-rate-distribution-chart');
        if (rateCtx) {
            window.fullAttendanceCharts.rate = new Chart(rateCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.rateDistribution),
                    datasets: [{
                        label: '인원 수',
                        data: Object.values(data.rateDistribution),
                        backgroundColor: [
                            '#48bb78', '#63b3ed', '#4299e1', '#667eea',
                            '#9f7aea', '#f56565'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // 4. Achievement Factors Chart
        const factorsCtx = document.getElementById('achievement-factors-chart');
        if (factorsCtx) {
            window.fullAttendanceCharts.factors = new Chart(factorsCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data.achievementFactors),
                    datasets: [{
                        data: Object.values(data.achievementFactors),
                        backgroundColor: ['#4299e1', '#48bb78', '#ed8936', '#9f7aea']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }
    }
    
    function populateFullAttendanceTables() {
        const data = getFullAttendanceData();
        
        // Populate full attendance table
        const tbody = document.getElementById('full-attendance-table-body');
        if (tbody) {
            tbody.innerHTML = data.fullAttendanceList.map(person => `
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.name}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.team}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.position}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.days}일</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                        <span style="padding: 4px 8px; background: #d4edda; color: #155724; border-radius: 4px; font-size: 12px;">
                            ${person.rate}
                        </span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                        <span style="padding: 4px 8px; background: #fff3cd; color: #856404; border-radius: 4px; font-size: 12px;">
                            ${person.consecutive}개월
                        </span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                        <strong style="color: #28a745;">${person.bonus}</strong>
                    </td>
                </tr>
            `).join('');
        }
        
        // Populate near perfect attendance table
        const nearTbody = document.getElementById('near-perfect-table-body');
        if (nearTbody) {
            nearTbody.innerHTML = data.nearPerfectList.map(person => `
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #90caf9;">${person.name}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #90caf9;">${person.team}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #90caf9;">
                        <span style="padding: 4px 8px; background: #e3f2fd; color: #1565c0; border-radius: 4px; font-size: 12px;">
                            ${person.rate}
                        </span>
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #90caf9;">${person.absenceDays}일</td>
                    <td style="padding: 10px; border-bottom: 1px solid #90caf9;">
                        <span style="padding: 4px 8px; background: #f3e5f5; color: #4a148c; border-radius: 4px; font-size: 12px;">
                            ${person.improvement}
                        </span>
                    </td>
                </tr>
            `).join('');
        }
    }
    
    // Update the openModal function to handle full attendance modal
    const originalOpenModal2 = window.openModal;
    window.openModal = function(modalId) {
        if (modalId === 'modal-full-attendance') {
            // Create detailed full attendance modal instead
            createFullAttendanceModal();
            document.getElementById('modal-full-attendance-detailed').style.display = 'block';
        } else if (originalOpenModal2) {
            originalOpenModal2(modalId);
        }
    };
    """
    
    return js_code

def inject_full_attendance_popup(input_file, output_file):
    """Inject full attendance popup code into dashboard"""
    
    print(f"📋 Reading dashboard from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate the JavaScript code
    js_code = generate_full_attendance_popup_code()
    
    # Find the right place to inject (after resignation popup)
    injection_point = html_content.find('</body>')
    
    if injection_point == -1:
        print("❌ Could not find </body> tag")
        return None
    
    # Inject the code
    injection = f"""
    <!-- Card #9: 만근자 상세 분석 팝업 -->
    <script>
    {js_code}
    </script>
    """
    
    html_content = html_content[:injection_point] + injection + html_content[injection_point:]
    
    # Save the updated HTML
    print(f"💾 Saving dashboard with full attendance popup to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Full attendance popup implementation completed!")
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("Card #9 (만근자) 팝업 구현")
    print("=" * 60)
    
    # Use the file with resignation popup as input
    dashboard_dir = Path(__file__).parent / 'output_files'
    input_file = dashboard_dir / 'management_dashboard_2025_08_with_resignation.html'
    
    if not input_file.exists():
        # Fallback to fixed numbering file
        input_file = dashboard_dir / 'management_dashboard_2025_08_fixed_numbering.html'
    
    if not input_file.exists():
        print(f"❌ Dashboard file not found: {input_file}")
        return 1
    
    # Create output file name
    output_file = dashboard_dir / 'management_dashboard_2025_08_complete.html'
    
    # Inject the full attendance popup
    result = inject_full_attendance_popup(input_file, output_file)
    
    if result:
        # Open in browser
        import webbrowser
        import os
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')
        print("\n브라우저에서 만근자 팝업이 구현된 대시보드가 열립니다...")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())