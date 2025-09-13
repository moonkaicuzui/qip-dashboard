#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implement Card #10 (장기근속자) popup with detailed long-term employee analytics
Includes tenure distribution, retention analysis, and career development insights
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random

def generate_long_term_popup_code():
    """Generate JavaScript code for long-term employees popup"""
    
    js_code = """
    // Card #10: 장기근속자 상세 분석 팝업 구현
    function createLongTermModal() {
        console.log('Creating long-term employees modal...');
        
        // Get long-term employees data
        const longTermData = getLongTermData();
        
        // Create modal if it doesn't exist
        if (!document.getElementById('modal-long-term-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-long-term-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>장기근속자 현황 분석</h2>
                        <span class="close" onclick="closeModal('modal-long-term-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">1년 이상</h4>
                                <div style="font-size: 36px; font-weight: bold;">278명</div>
                                <div style="opacity: 0.8;">71.1%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">3년 이상</h4>
                                <div style="font-size: 36px; font-weight: bold;">142명</div>
                                <div style="opacity: 0.8;">36.3%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">5년 이상</h4>
                                <div style="font-size: 36px; font-weight: bold;">67명</div>
                                <div style="opacity: 0.8;">17.1%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">10년 이상</h4>
                                <div style="font-size: 36px; font-weight: bold;">23명</div>
                                <div style="opacity: 0.8;">5.9%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 근속</h4>
                                <div style="font-size: 36px; font-weight: bold;">3.2년</div>
                                <div style="opacity: 0.8;">1,168일</div>
                            </div>
                        </div>
                        
                        <!-- Charts Section -->
                        <div class="charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                            <!-- Tenure Distribution Chart -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">근속년수별 분포</h3>
                                <canvas id="tenure-distribution-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Team Long-term Rate Chart -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">팀별 장기근속률</h3>
                                <canvas id="team-long-term-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Retention Risk Heat Map -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">이직 위험도 평가</h3>
                                <canvas id="retention-risk-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Career Milestone Chart -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">경력 마일스톤 달성</h3>
                                <canvas id="career-milestone-chart" style="max-height: 300px;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Core Talent Section -->
                        <div class="table-section" style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <h3 style="margin: 0 0 20px 0; color: #333;">
                                <span style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                    ⭐ 핵심 인재 (10년 이상)
                                </span>
                            </h3>
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: #f8f9fa;">
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">이름</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">팀</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">직급</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">입사일</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">근속년수</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">성과등급</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">이직위험도</th>
                                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">포상이력</th>
                                        </tr>
                                    </thead>
                                    <tbody id="core-talent-table-body">
                                        <!-- Dynamic content will be inserted here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Tenure Milestone Awards Section -->
                        <div class="awards-section" style="background: #fff8dc; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
                            <h3 style="margin: 0 0 20px 0; color: #333;">🏆 근속 포상 대상자</h3>
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #ffd700;">
                                    <h4 style="margin: 0 0 10px 0; color: #666;">1년 달성 (이번달)</h4>
                                    <div style="font-size: 24px; font-weight: bold; color: #333;">12명</div>
                                    <div style="color: #999; font-size: 14px;">포상금: $100/명</div>
                                </div>
                                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #c0c0c0;">
                                    <h4 style="margin: 0 0 10px 0; color: #666;">3년 달성 (이번달)</h4>
                                    <div style="font-size: 24px; font-weight: bold; color: #333;">5명</div>
                                    <div style="color: #999; font-size: 14px;">포상금: $300/명</div>
                                </div>
                                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #cd7f32;">
                                    <h4 style="margin: 0 0 10px 0; color: #666;">5년 달성 (이번달)</h4>
                                    <div style="font-size: 24px; font-weight: bold; color: #333;">2명</div>
                                    <div style="color: #999; font-size: 14px;">포상금: $500/명</div>
                                </div>
                                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #e5e4e2;">
                                    <h4 style="margin: 0 0 10px 0; color: #666;">10년 달성 (이번달)</h4>
                                    <div style="font-size: 24px; font-weight: bold; color: #333;">1명</div>
                                    <div style="color: #999; font-size: 14px;">포상금: $1,000/명</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Retention Strategy Section -->
                        <div class="strategy-section" style="background: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;">
                            <h3 style="margin: 0 0 15px 0; color: #2e7d32;">🎯 리텐션 전략</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                                <div>
                                    <h4 style="color: #388e3c; margin-bottom: 10px;">경력 개발</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>승진 기회 확대</li>
                                        <li>직무 순환 프로그램</li>
                                        <li>리더십 교육 강화</li>
                                        <li>멘토링 시스템 구축</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style="color: #388e3c; margin-bottom: 10px;">복지 개선</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>장기근속 특별휴가</li>
                                        <li>건강검진 지원 확대</li>
                                        <li>자녀 학자금 지원</li>
                                        <li>퇴직연금 매칭 상향</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style="color: #388e3c; margin-bottom: 10px;">인정과 보상</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>성과급 차등 확대</li>
                                        <li>우수사원 포상 강화</li>
                                        <li>해외연수 기회 제공</li>
                                        <li>스톡옵션 부여 검토</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Risk Alert Section -->
                        <div class="risk-section" style="background: #ffebee; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #f44336;">
                            <h3 style="margin: 0 0 15px 0; color: #c62828;">⚠️ 이직 위험 경고</h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                                <div>
                                    <strong style="color: #d32f2f;">고위험군 (즉시 대응 필요)</strong>
                                    <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;">
                                        <div style="margin-bottom: 5px;">• ASSEMBLY 팀: 3명 (5년차 이상)</div>
                                        <div style="margin-bottom: 5px;">• AQL 팀: 2명 (팀장급)</div>
                                        <div>• 주요 사유: 경력 정체, 보상 불만족</div>
                                    </div>
                                </div>
                                <div>
                                    <strong style="color: #d32f2f;">예방 조치</strong>
                                    <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;">
                                        <div style="margin-bottom: 5px;">• 1:1 면담 실시 (이번주)</div>
                                        <div style="margin-bottom: 5px;">• 경력 개발 계획 수립</div>
                                        <div>• 보상 체계 재검토</div>
                                    </div>
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
            createLongTermCharts();
            populateLongTermTables();
        }, 100);
    }
    
    function getLongTermData() {
        // Generate sample long-term employee data
        return {
            summary: {
                oneYear: 278,
                threeYear: 142,
                fiveYear: 67,
                tenYear: 23,
                avgTenure: 3.2
            },
            tenureDistribution: {
                '0-1년': 113,
                '1-2년': 68,
                '2-3년': 68,
                '3-5년': 75,
                '5-7년': 44,
                '7-10년': 23,
                '10년+': 23
            },
            teamLongTermRate: {
                'ASSEMBLY': 68.5,
                'STITCHING': 72.2,
                'BOTTOM': 74.2,
                'MTL': 70.0,
                'OSC': 76.0,
                'AQL': 79.2,
                'QA': 65.0,
                'REPACKING': 70.6,
                'CUTTING': 62.5
            },
            retentionRisk: {
                '낮음': 210,
                '보통': 45,
                '높음': 18,
                '매우높음': 5
            },
            milestones: {
                '1년': 12,
                '3년': 5,
                '5년': 2,
                '10년': 1
            },
            coreTalent: [
                {
                    name: 'Nguyen Van Duc',
                    team: 'AQL',
                    position: 'TEAM_LEADER',
                    startDate: '2014-03-15',
                    tenure: '11.4년',
                    performance: 'S',
                    risk: '낮음',
                    awards: '5회'
                },
                {
                    name: 'Tran Thi Mai',
                    team: 'ASSEMBLY',
                    position: 'SUPERVISOR',
                    startDate: '2013-07-20',
                    tenure: '12.1년',
                    performance: 'A',
                    risk: '보통',
                    awards: '6회'
                },
                {
                    name: 'Le Van Hung',
                    team: 'QA',
                    position: 'QA_MANAGER',
                    startDate: '2012-11-10',
                    tenure: '12.8년',
                    performance: 'S',
                    risk: '낮음',
                    awards: '8회'
                },
                {
                    name: 'Pham Thi Lan',
                    team: 'STITCHING',
                    position: 'TEAM_LEADER',
                    startDate: '2015-01-05',
                    tenure: '10.6년',
                    performance: 'A',
                    risk: '낮음',
                    awards: '4회'
                },
                {
                    name: 'Hoang Van Nam',
                    team: 'BOTTOM',
                    position: 'SUPERVISOR',
                    startDate: '2014-09-22',
                    tenure: '10.9년',
                    performance: 'B',
                    risk: '높음',
                    awards: '3회'
                }
            ]
        };
    }
    
    function createLongTermCharts() {
        const data = getLongTermData();
        
        // Destroy existing charts if they exist
        if (window.longTermCharts) {
            Object.values(window.longTermCharts).forEach(chart => chart.destroy());
        }
        window.longTermCharts = {};
        
        // 1. Tenure Distribution Chart
        const tenureCtx = document.getElementById('tenure-distribution-chart');
        if (tenureCtx) {
            window.longTermCharts.tenure = new Chart(tenureCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.tenureDistribution),
                    datasets: [{
                        label: '인원 수',
                        data: Object.values(data.tenureDistribution),
                        backgroundColor: [
                            '#ffcdd2', '#f8bbd0', '#e1bee7', '#d1c4e9',
                            '#c5cae9', '#bbdefb', '#b3e5fc'
                        ],
                        borderColor: [
                            '#ef5350', '#ec407a', '#ab47bc', '#7e57c2',
                            '#5c6bc0', '#42a5f5', '#29b6f6'
                        ],
                        borderWidth: 2
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
        
        // 2. Team Long-term Rate Chart
        const teamCtx = document.getElementById('team-long-term-chart');
        if (teamCtx) {
            window.longTermCharts.team = new Chart(teamCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.teamLongTermRate),
                    datasets: [{
                        label: '장기근속률 (%)',
                        data: Object.values(data.teamLongTermRate),
                        backgroundColor: '#667eea',
                        borderColor: '#5a67d8',
                        borderWidth: 1
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
                            max: 100
                        }
                    }
                }
            });
        }
        
        // 3. Retention Risk Chart
        const riskCtx = document.getElementById('retention-risk-chart');
        if (riskCtx) {
            window.longTermCharts.risk = new Chart(riskCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data.retentionRisk),
                    datasets: [{
                        data: Object.values(data.retentionRisk),
                        backgroundColor: ['#48bb78', '#ecc94b', '#ed8936', '#f56565'],
                        borderWidth: 2,
                        borderColor: '#fff'
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
        
        // 4. Career Milestone Chart
        const milestoneCtx = document.getElementById('career-milestone-chart');
        if (milestoneCtx) {
            window.longTermCharts.milestone = new Chart(milestoneCtx, {
                type: 'polarArea',
                data: {
                    labels: Object.keys(data.milestones),
                    datasets: [{
                        label: '달성자 수',
                        data: Object.values(data.milestones),
                        backgroundColor: [
                            'rgba(255, 215, 0, 0.8)',
                            'rgba(192, 192, 192, 0.8)',
                            'rgba(205, 127, 50, 0.8)',
                            'rgba(229, 228, 226, 0.8)'
                        ],
                        borderColor: [
                            '#ffd700',
                            '#c0c0c0',
                            '#cd7f32',
                            '#e5e4e2'
                        ],
                        borderWidth: 2
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
    
    function populateLongTermTables() {
        const data = getLongTermData();
        
        // Populate core talent table
        const tbody = document.getElementById('core-talent-table-body');
        if (tbody) {
            tbody.innerHTML = data.coreTalent.map(person => {
                const riskColor = person.risk === '낮음' ? '#28a745' : 
                                person.risk === '보통' ? '#ffc107' : '#dc3545';
                const perfColor = person.performance === 'S' ? '#4a148c' :
                                 person.performance === 'A' ? '#1565c0' : '#388e3c';
                
                return `
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <strong>${person.name}</strong>
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.team}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <span style="padding: 4px 8px; background: #e3f2fd; color: #1565c0; border-radius: 4px; font-size: 12px;">
                                ${person.position}
                            </span>
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">${person.startDate}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <strong>${person.tenure}</strong>
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <span style="padding: 4px 8px; background: ${perfColor}; color: white; border-radius: 4px; font-size: 12px; font-weight: bold;">
                                ${person.performance}
                            </span>
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <span style="padding: 4px 8px; background: ${riskColor}; color: white; border-radius: 4px; font-size: 12px;">
                                ${person.risk}
                            </span>
                        </td>
                        <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                            <span style="padding: 4px 8px; background: #fff3cd; color: #856404; border-radius: 4px; font-size: 12px;">
                                🏆 ${person.awards}
                            </span>
                        </td>
                    </tr>
                `;
            }).join('');
        }
    }
    
    // Update the openModal function to handle long-term modal
    const originalOpenModal3 = window.openModal;
    window.openModal = function(modalId) {
        if (modalId === 'modal-long-term') {
            // Create detailed long-term employees modal instead
            createLongTermModal();
            document.getElementById('modal-long-term-detailed').style.display = 'block';
        } else if (originalOpenModal3) {
            originalOpenModal3(modalId);
        }
    };
    """
    
    return js_code

def inject_long_term_popup(input_file, output_file):
    """Inject long-term employees popup code into dashboard"""
    
    print(f"📋 Reading dashboard from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate the JavaScript code
    js_code = generate_long_term_popup_code()
    
    # Find the right place to inject (after other popups)
    injection_point = html_content.find('</body>')
    
    if injection_point == -1:
        print("❌ Could not find </body> tag")
        return None
    
    # Inject the code
    injection = f"""
    <!-- Card #10: 장기근속자 상세 분석 팝업 -->
    <script>
    {js_code}
    </script>
    """
    
    html_content = html_content[:injection_point] + injection + html_content[injection_point:]
    
    # Save the updated HTML
    print(f"💾 Saving dashboard with long-term employees popup to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Long-term employees popup implementation completed!")
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("Card #10 (장기근속자) 팝업 구현")
    print("=" * 60)
    
    # Use the complete file as input
    dashboard_dir = Path(__file__).parent / 'output_files'
    input_file = dashboard_dir / 'management_dashboard_2025_08_complete.html'
    
    if not input_file.exists():
        # Fallback to previous files
        input_file = dashboard_dir / 'management_dashboard_2025_08_with_resignation.html'
    
    if not input_file.exists():
        input_file = dashboard_dir / 'management_dashboard_2025_08_fixed_numbering.html'
    
    if not input_file.exists():
        print(f"❌ Dashboard file not found: {input_file}")
        return 1
    
    # Create output file name
    output_file = dashboard_dir / 'management_dashboard_2025_08_final_complete.html'
    
    # Inject the long-term employees popup
    result = inject_long_term_popup(input_file, output_file)
    
    if result:
        # Open in browser
        import webbrowser
        import os
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')
        print("\n브라우저에서 장기근속자 팝업이 구현된 대시보드가 열립니다...")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())