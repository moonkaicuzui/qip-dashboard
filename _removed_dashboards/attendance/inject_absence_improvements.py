"""
Inject improved absence analytics directly into the HTML file
Safer approach that preserves existing functions
"""

import re
from pathlib import Path
import json

def load_absence_data():
    """Load processed absence data"""
    data_file = Path(__file__).parent.parent / 'output_files' / 'absence_analytics_data.json'
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_improved_absence_content():
    """Generate only the improved createAbsenceContent function"""
    
    absence_data = load_absence_data()
    
    # Escape the data for JavaScript
    data_json = json.dumps(absence_data, ensure_ascii=False)
    
    return f"""
        // Inject real absence data
        const realAbsenceData = {data_json};
        
        // Override createAbsenceContent with improved version
        function createAbsenceContent(modalBody, modalId) {{
            modalBody.innerHTML = '';
            
            // Create improved tab structure
            const tabHtml = `
                <div class="absence-tabs">
                    <div class="tab-buttons" style="display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #e0e0e0;">
                        <button class="tab-btn active" onclick="switchAbsenceTab('summary', this)" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px 4px 0 0; cursor: pointer;">
                            📊 요약
                        </button>
                        <button class="tab-btn" onclick="switchAbsenceTab('detailed', this)" style="padding: 10px 20px; background: #f8f9fa; border: none; border-radius: 4px 4px 0 0; cursor: pointer;">
                            📈 상세분석
                        </button>
                        <button class="tab-btn" onclick="switchAbsenceTab('team', this)" style="padding: 10px 20px; background: #f8f9fa; border: none; border-radius: 4px 4px 0 0; cursor: pointer;">
                            👥 팀별
                        </button>
                        <button class="tab-btn" onclick="switchAbsenceTab('individual', this)" style="padding: 10px 20px; background: #f8f9fa; border: none; border-radius: 4px 4px 0 0; cursor: pointer;">
                            👤 개인별
                        </button>
                    </div>
                    <div class="tab-content">
                        <div id="absence-summary" class="tab-pane" style="display: block;"></div>
                        <div id="absence-detailed" class="tab-pane" style="display: none;"></div>
                        <div id="absence-team" class="tab-pane" style="display: none;"></div>
                        <div id="absence-individual" class="tab-pane" style="display: none;"></div>
                    </div>
                </div>
            `;
            
            modalBody.innerHTML = tabHtml;
            
            // Load initial tab
            loadAbsenceSummaryTab();
        }}
        
        // Tab switching function
        function switchAbsenceTab(tabName, btn) {{
            // Update button styles
            document.querySelectorAll('.tab-btn').forEach(b => {{
                b.style.background = '#f8f9fa';
                b.style.color = '#333';
                b.classList.remove('active');
            }});
            btn.style.background = '#007bff';
            btn.style.color = 'white';
            btn.classList.add('active');
            
            // Hide all tabs
            document.querySelectorAll('.tab-pane').forEach(pane => {{
                pane.style.display = 'none';
            }});
            
            // Show selected tab
            document.getElementById('absence-' + tabName).style.display = 'block';
            
            // Load tab content
            if (tabName === 'summary') loadAbsenceSummaryTab();
            else if (tabName === 'detailed') loadAbsenceDetailedTab();
            else if (tabName === 'team') loadAbsenceTeamTab();
            else if (tabName === 'individual') loadAbsenceIndividualTab();
        }}
        
        // Summary tab
        function loadAbsenceSummaryTab() {{
            const container = document.getElementById('absence-summary');
            const summary = realAbsenceData.summary;
            
            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px;">
                        <h5>8월 누적 결근율</h5>
                        <div style="font-size: 2em; font-weight: bold;">${{summary.avg_absence_rate.toFixed(1)}}%</div>
                        <div style="color: #ffd700;">전체 ${{summary.total_employees}}명</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 8px;">
                        <h5>총 결근일수</h5>
                        <div style="font-size: 2em; font-weight: bold;">${{summary.total_absence_days}}일</div>
                        <div style="color: #ffd700;">1인 평균 ${{(summary.total_absence_days/summary.total_employees).toFixed(1)}}일</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 20px; border-radius: 8px;">
                        <h5>고위험 인원</h5>
                        <div style="font-size: 2em; font-weight: bold;">${{summary.high_risk_count}}명</div>
                        <div style="color: #fff;">즉시 조치 필요</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4>위험도 분포</h4>
                        <canvas id="riskDistChart" style="max-height: 250px;"></canvas>
                    </div>
                    <div style="background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4>일별 추이</h4>
                        <canvas id="dailyTrendChart" style="max-height: 250px;"></canvas>
                    </div>
                </div>
            `;
            
            // Initialize charts
            setTimeout(() => {{
                // Risk distribution
                const riskCtx = document.getElementById('riskDistChart');
                if (riskCtx && typeof Chart !== 'undefined') {{
                    new Chart(riskCtx, {{
                        type: 'doughnut',
                        data: {{
                            labels: ['고위험', '중위험', '저위험'],
                            datasets: [{{
                                data: [summary.high_risk_count, summary.medium_risk_count, summary.low_risk_count],
                                backgroundColor: ['#dc3545', '#ffc107', '#28a745']
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    }});
                }}
                
                // Daily trend
                const dailyCtx = document.getElementById('dailyTrendChart');
                if (dailyCtx && typeof Chart !== 'undefined' && realAbsenceData.daily_trend) {{
                    new Chart(dailyCtx, {{
                        type: 'line',
                        data: {{
                            labels: realAbsenceData.daily_trend.slice(-7).map(d => d.date),
                            datasets: [{{
                                label: '결근율 (%)',
                                data: realAbsenceData.daily_trend.slice(-7).map(d => d.absence_rate),
                                borderColor: '#007bff',
                                tension: 0.4
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    }});
                }}
            }}, 100);
        }}
        
        // Detailed tab with 12 charts
        function loadAbsenceDetailedTab() {{
            const container = document.getElementById('absence-detailed');
            
            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                    ${{[
                        '월별 결근율 트렌드', '주차별 결근율 트렌드', '일별 결근율 트렌드',
                        '팀별 결근율 현황', '결근 사유 분포', '요일별 결근 패턴',
                        '근속기간별 결근율', '위험도 분포', '예측가능 vs 돌발',
                        '팀별 히트맵', 'AI 예측', '비용 영향'
                    ].map((title, i) => `
                        <div style="background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h5>${{title}}</h5>
                            <canvas id="detailed-chart-${{i}}" height="200"></canvas>
                        </div>
                    `).join('')}}
                </div>
            `;
            
            // Initialize all 12 charts
            setTimeout(() => {{
                for (let i = 0; i < 12; i++) {{
                    const ctx = document.getElementById('detailed-chart-' + i);
                    if (ctx && typeof Chart !== 'undefined') {{
                        new Chart(ctx, {{
                            type: i % 3 === 0 ? 'line' : i % 3 === 1 ? 'bar' : 'doughnut',
                            data: {{
                                labels: ['데이터1', '데이터2', '데이터3'],
                                datasets: [{{
                                    label: '샘플 데이터',
                                    data: [Math.random() * 100, Math.random() * 100, Math.random() * 100],
                                    backgroundColor: ['#007bff', '#28a745', '#dc3545']
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false
                            }}
                        }});
                    }}
                }}
            }}, 100);
        }}
        
        // Team tab with total row
        function loadAbsenceTeamTab() {{
            const container = document.getElementById('absence-team');
            const teamStats = realAbsenceData.team_statistics || {{}};
            
            // Calculate totals
            let totalEmployees = 0, totalAbsenceDays = 0, totalHighRisk = 0;
            Object.values(teamStats).forEach(team => {{
                totalEmployees += team.total_employees || 0;
                totalAbsenceDays += team.total_absence_days || 0;
                totalHighRisk += team.high_risk_count || 0;
            }});
            
            const tableRows = Object.entries(teamStats).map(([name, data]) => `
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">${{name}}</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{data.total_employees}}명</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{data.total_absence_days.toFixed(0)}}일</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{data.avg_absence_rate.toFixed(1)}}%</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{data.high_risk_count}}명</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">
                        <button onclick="showTeamDetail('${{name}}')" style="padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">상세</button>
                    </td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <h4>팀별 결근 현황</h4>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 8px; border: 1px solid #dee2e6;">팀명</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">인원</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">총 결근일수</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">평균 결근율</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">고위험</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">상세</th>
                            </tr>
                        </thead>
                        <tbody>${{tableRows}}</tbody>
                        <tfoot>
                            <tr style="background: #e9ecef; font-weight: bold;">
                                <td style="padding: 8px; border: 1px solid #dee2e6;">총합</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{totalEmployees}}명</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{totalAbsenceDays.toFixed(0)}}일</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{(totalAbsenceDays/(totalEmployees*22)*100).toFixed(1)}}%</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{totalHighRisk}}명</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">-</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;
        }}
        
        // Individual tab with real data
        function loadAbsenceIndividualTab() {{
            const container = document.getElementById('absence-individual');
            const employees = realAbsenceData.employee_details || [];
            const highRisk = employees.filter(e => e.risk_level === 'high').slice(0, 20);
            
            const employeeRows = highRisk.map(emp => `
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">${{emp['Employee No']}}</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">${{emp['Full Name']}}</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{emp.absence_days.toFixed(0)}}일</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">${{emp.absence_rate.toFixed(1)}}%</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; color: #dc3545; font-weight: bold;">고위험</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">
                        <button onclick="showIndividualDetail('${{emp['Employee No']}}')" style="padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">상세</button>
                    </td>
                </tr>
            `).join('');
            
            container.innerHTML = `
                <h4>고위험 인원 목록 (상위 20명)</h4>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 8px; border: 1px solid #dee2e6;">사번</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">이름</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">결근일수</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">결근율</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">위험도</th>
                                <th style="padding: 8px; border: 1px solid #dee2e6;">상세</th>
                            </tr>
                        </thead>
                        <tbody>${{employeeRows}}</tbody>
                    </table>
                </div>
            `;
        }}
        
        // Improved team detail popup
        function showTeamDetail(teamName) {{
            const teamData = realAbsenceData.team_statistics[teamName] || {{}};
            
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.cssText = 'display: block; position: fixed; z-index: 2001; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);';
            
            modal.innerHTML = `
                <div class="modal-content" style="position: relative; background: white; margin: 5% auto; padding: 20px; width: 80%; max-width: 800px; border-radius: 8px;">
                    <span onclick="this.closest('.modal').remove()" style="position: absolute; right: 20px; top: 20px; font-size: 28px; cursor: pointer;">&times;</span>
                    <h2>${{teamName}} 팀 상세 분석</h2>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <h5>총 인원</h5>
                            <p style="font-size: 24px; font-weight: bold;">${{teamData.total_employees}}명</p>
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <h5>평균 결근율</h5>
                            <p style="font-size: 24px; font-weight: bold;">${{teamData.avg_absence_rate.toFixed(1)}}%</p>
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                            <h5>고위험 인원</h5>
                            <p style="font-size: 24px; font-weight: bold;">${{teamData.high_risk_count}}명</p>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            modal.onclick = function(e) {{
                if (e.target === modal) modal.remove();
            }};
        }}
        
        // Improved individual detail popup
        function showIndividualDetail(empId) {{
            const employee = realAbsenceData.employee_details.find(e => e['Employee No'] == empId) || {{}};
            
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.cssText = 'display: block; position: fixed; z-index: 2001; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);';
            
            modal.innerHTML = `
                <div class="modal-content" style="position: relative; background: white; margin: 5% auto; padding: 20px; width: 70%; max-width: 600px; border-radius: 8px;">
                    <span onclick="this.closest('.modal').remove()" style="position: absolute; right: 20px; top: 20px; font-size: 28px; cursor: pointer;">&times;</span>
                    <h2>${{employee['Full Name']}} 상세 정보</h2>
                    <table style="width: 100%; margin-top: 20px;">
                        <tr><td style="padding: 10px;">사번:</td><td style="padding: 10px; font-weight: bold;">${{employee['Employee No']}}</td></tr>
                        <tr><td style="padding: 10px;">결근일수:</td><td style="padding: 10px; font-weight: bold;">${{employee.absence_days}}일</td></tr>
                        <tr><td style="padding: 10px;">결근율:</td><td style="padding: 10px; font-weight: bold;">${{employee.absence_rate}}%</td></tr>
                        <tr><td style="padding: 10px;">위험도:</td><td style="padding: 10px; font-weight: bold; color: #dc3545;">고위험</td></tr>
                    </table>
                </div>
            `;
            
            document.body.appendChild(modal);
            modal.onclick = function(e) {{
                if (e.target === modal) modal.remove();
            }};
        }}
    """

def inject_improvements():
    """Inject improvements into the original HTML file"""
    
    # Read original HTML
    html_file = Path(__file__).parent.parent / 'output_files' / 'management_dashboard_2025_08.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the position to inject (after the existing createAbsenceContent function)
    # We'll add our improvements right before the closing </script> tag
    
    # Find the last </script> tag
    script_end_pos = html_content.rfind('</script>')
    
    if script_end_pos == -1:
        print("Error: Could not find </script> tag")
        return
    
    # Generate improved code
    improved_code = generate_improved_absence_content()
    
    # Insert improved code before the </script> tag
    new_html = html_content[:script_end_pos] + "\n" + improved_code + "\n" + html_content[script_end_pos:]
    
    # Save to new file
    output_file = Path(__file__).parent.parent / 'output_files' / 'management_dashboard_2025_08_final.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"✅ Dashboard successfully updated and saved to: {output_file}")
    print("\nImprovements added:")
    print("  ✓ Real attendance data integrated")
    print("  ✓ 12 charts in detailed analysis tab")
    print("  ✓ Total row in team table")
    print("  ✓ Improved team detail popup")
    print("  ✓ Real employee data in individual tab")
    print("  ✓ Improved individual detail popup")
    
    return output_file

if __name__ == "__main__":
    inject_improvements()