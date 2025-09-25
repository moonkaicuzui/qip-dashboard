#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced HR Management Dashboard with 3-Level Nested Treemap
3단계 중첩 트리맵과 Sunburst 상세 뷰를 포함한 개선된 대시보드
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import argparse
import warnings
warnings.filterwarnings('ignore')

class Enhanced3LevelTreemapDashboard:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.report_date = datetime.now()
        self.data = {
            'current': pd.DataFrame(),
            'previous': pd.DataFrame(),
            'attendance': pd.DataFrame()
        }
        self.metadata = {}
        self.team_structure = {}
        self.team_mapping = {}
        
    def load_data(self):
        """데이터 로드"""
        print(f"\n📊 Loading data for {self.year}년 {self.month}월...")
        
        # Load team structure
        team_structure_path = os.path.join(self.base_path, 'HR info', 'team_sturcture_update_version2.csv')
        if os.path.exists(team_structure_path):
            self.team_structure_df = pd.read_csv(team_structure_path, encoding='utf-8-sig')
            print(f"✅ Loaded team structure: {len(self.team_structure_df)} records")
        else:
            print("⚠️ Team structure file not found")
            self.team_structure_df = pd.DataFrame()
            
        # Load current month data
        self.load_current_month_data()
        self.load_previous_month_data()
        
    def load_current_month_data(self):
        """현재 월 데이터 로드"""
        month_names = {
            1: '1월', 2: '2월', 3: '3월', 4: '4월', 5: '5월', 6: '6월',
            7: '7월', 8: '8월', 9: '9월', 10: '10월', 11: '11월', 12: '12월'
        }
        
        month_str = month_names.get(self.month, f'{self.month}월')
        file_path = os.path.join(self.base_path, 'input_files', f'{self.year}년 {month_str} 인센티브 지급 세부 정보.csv')
        
        if os.path.exists(file_path):
            self.data['current'] = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"✅ Loaded current month data: {len(self.data['current'])} employees")
        else:
            print(f"⚠️ Current month file not found: {file_path}")
            self.data['current'] = pd.DataFrame()
            
    def load_previous_month_data(self):
        """이전 월 데이터 로드 - NO FAKE DATA"""
        prev_month = self.month - 1 if self.month > 1 else 12
        prev_year = self.year if self.month > 1 else self.year - 1
        
        month_names = {
            1: '1월', 2: '2월', 3: '3월', 4: '4월', 5: '5월', 6: '6월',
            7: '7월', 8: '8월', 9: '9월', 10: '10월', 11: '11월', 12: '12월'
        }
        
        month_str = month_names.get(prev_month, f'{prev_month}월')
        file_path = os.path.join(self.base_path, 'input_files', f'{prev_year}년 {month_str} 인센티브 지급 세부 정보.csv')
        
        if os.path.exists(file_path):
            self.data['previous'] = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"✅ Loaded previous month data: {len(self.data['previous'])} employees")
        else:
            print(f"⚠️ Previous month data not found - will show 0 for comparisons")
            self.data['previous'] = pd.DataFrame()
            
    def process_hierarchy_data(self):
        """5단계 계층 구조 데이터 처리"""
        if self.team_structure_df.empty:
            return {}
            
        # 계층 구조 데이터 생성
        hierarchy_data = []
        
        for _, row in self.team_structure_df.iterrows():
            hierarchy_data.append({
                'teams': row.get('teams', ''),
                'role_categories': row.get('role_categories', ''),
                'position_1st': row.get('position_1st', ''),
                'position_2nd': row.get('position_2nd', ''),
                'position_3rd': row.get('position_3rd', ''),
                'type': row.get('ROLE TYPE STD', 'TYPE-2')
            })
            
        return hierarchy_data
        
    def calculate_team_stats(self):
        """팀별 통계 계산"""
        team_stats = {}
        
        if not self.data['current'].empty:
            # 현재 월 팀별 인원 계산
            for team in self.team_structure_df['teams'].unique():
                team_employees = self.team_structure_df[self.team_structure_df['teams'] == team]
                team_stats[team] = {
                    'current': len(team_employees),
                    'previous': 0,
                    'change': 0,
                    'change_percent': 0,
                    'roles': {}
                }
                
                # 역할별 인원 계산
                for role in team_employees['role_categories'].unique():
                    if pd.notna(role):
                        role_count = len(team_employees[team_employees['role_categories'] == role])
                        team_stats[team]['roles'][role] = {
                            'current': role_count,
                            'positions': {}
                        }
                        
                        # Position별 인원 계산
                        role_employees = team_employees[team_employees['role_categories'] == role]
                        for pos in role_employees['position_1st'].unique():
                            if pd.notna(pos):
                                pos_count = len(role_employees[role_employees['position_1st'] == pos])
                                team_stats[team]['roles'][role]['positions'][pos] = pos_count
        
        # 이전 월 데이터가 있으면 비교
        if not self.data['previous'].empty and 'teams' in self.data['previous'].columns:
            for team in team_stats:
                prev_count = len(self.data['previous'][self.data['previous']['teams'] == team])
                team_stats[team]['previous'] = prev_count
                team_stats[team]['change'] = team_stats[team]['current'] - prev_count
                if prev_count > 0:
                    team_stats[team]['change_percent'] = (team_stats[team]['change'] / prev_count) * 100
                    
        return team_stats
        
    def generate_dashboard_html(self):
        """3단계 중첩 트리맵과 Sunburst 차트를 포함한 대시보드 생성"""
        
        hierarchy_data = self.process_hierarchy_data()
        team_stats = self.calculate_team_stats()
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HR Management Dashboard - {self.year}년 {self.month}월</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard-container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            font-size: 18px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        /* 3단계 중첩 트리맵 스타일 */
        .treemap-container {{
            position: relative;
            width: 100%;
            height: 600px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 30px;
        }}
        
        .treemap-level-1 {{
            position: absolute;
            border: 2px solid #333;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .treemap-level-2 {{
            position: absolute;
            border: 1px solid rgba(255,255,255,0.3);
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .treemap-level-3 {{
            position: absolute;
            border: 1px solid rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .treemap-level-1:hover,
        .treemap-level-2:hover,
        .treemap-level-3:hover {{
            transform: scale(1.02);
            z-index: 100;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        
        .treemap-label {{
            position: absolute;
            top: 2px;
            left: 4px;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            pointer-events: none;
            z-index: 10;
        }}
        
        .treemap-label-1 {{
            font-size: 16px;
        }}
        
        .treemap-label-2 {{
            font-size: 13px;
        }}
        
        .treemap-label-3 {{
            font-size: 10px;
        }}
        
        .treemap-info {{
            position: absolute;
            bottom: 4px;
            right: 4px;
            font-size: 11px;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            pointer-events: none;
            z-index: 10;
        }}
        
        /* 텍스트 축약 스타일 */
        .abbreviated {{
            font-size: 9px !important;
        }}
        
        /* Sunburst 차트 모달 */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
        }}
        
        .modal-content {{
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border-radius: 15px;
            width: 90%;
            max-width: 1200px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{
            color: #000;
        }}
        
        .sunburst-container {{
            height: 600px;
            margin: 20px 0;
        }}
        
        /* 범례 */
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        .stat-change {{
            font-size: 14px;
            margin-top: 10px;
            font-weight: bold;
        }}
        
        .positive {{
            color: #00C851;
        }}
        
        .negative {{
            color: #CC0000;
        }}
        
        .neutral {{
            color: #757575;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>HR Management Dashboard</h1>
            <div class="date">{self.year}년 {self.month}월 | Generated: {self.report_date.strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="content">
            <div class="section-title">📊 3단계 중첩 트리맵 - 팀별 인원 분포</div>
            <div class="treemap-container" id="nested-treemap"></div>
            
            <div class="legend" id="treemap-legend"></div>
            
            <div class="section-title">📈 주요 통계</div>
            <div class="stats-grid" id="stats-grid"></div>
        </div>
    </div>
    
    <!-- Sunburst 상세 뷰 모달 -->
    <div id="sunburstModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2 id="modal-title">상세 계층 구조</h2>
            <div class="sunburst-container" id="sunburst-chart"></div>
            <div id="modal-stats"></div>
        </div>
    </div>
    
    <script>
        // 데이터 준비
        const hierarchyData = {json.dumps(hierarchy_data, ensure_ascii=False)};
        const teamStats = {json.dumps(team_stats, ensure_ascii=False)};
        
        // 텍스트 축약 함수
        function abbreviateText(text, maxLength) {{
            const abbreviations = {{
                'ASSEMBLY INSPECTOR': 'ASM INSP',
                'BOTTOM INSPECTOR': 'BTM INSP',
                'STITCHING INSPECTOR': 'STH INSP',
                'CUTTING INSPECTOR': 'CUT INSP',
                'OSC INSPECTOR': 'OSC INSP',
                'MTL INSPECTOR': 'MTL INSP',
                'QA INSPECTOR': 'QA INSP',
                'AQL INSPECTOR': 'AQL INSP',
                'GROUP LEADER': 'GRP LDR',
                'LINE LEADER': 'LINE LDR',
                'TEAM LEADER': 'TEAM LDR',
                'SUPERVISOR': 'SUPV',
                'MANAGER': 'MGR',
                'TOP-MANAGEMENT': 'TOP-MGT',
                'MID-MANAGEMENT': 'MID-MGT',
                'INSPECTOR': 'INSP',
                'SUPPORT': 'SUPP',
                'PACKING': 'PACK',
                'REPORT': 'RPT',
                'AUDITOR': 'AUD'
            }};
            
            // 미리 정의된 축약어가 있으면 사용
            if (abbreviations[text]) {{
                return abbreviations[text];
            }}
            
            // 너무 긴 텍스트는 잘라냄
            if (text && text.length > maxLength) {{
                return text.substring(0, maxLength) + '...';
            }}
            
            return text;
        }}
        
        // 색상 계산 함수
        function getColorForChange(changePercent) {{
            const absPercent = Math.abs(changePercent);
            
            if (changePercent > 0) {{
                // 양수: 초록색 그라데이션
                if (absPercent > 15) return '#00C851';
                else if (absPercent > 10) return '#2ECC71';
                else if (absPercent > 5) return '#5CB85C';
                else if (absPercent > 2) return '#7FB069';
                else return '#90C695';
            }} else if (changePercent < 0) {{
                // 음수: 빨간색 그라데이션
                if (absPercent > 15) return '#CC0000';
                else if (absPercent > 10) return '#E74C3C';
                else if (absPercent > 5) return '#D9534F';
                else if (absPercent > 2) return '#E57373';
                else return '#EF9A9A';
            }} else {{
                return '#757575'; // 변화 없음
            }}
        }}
        
        // 텍스트 색상 결정 함수
        function getTextColor(bgColor) {{
            const lightColors = ['#90C695', '#7FB069', '#EF9A9A', '#E57373', '#757575'];
            return lightColors.includes(bgColor) ? '#1a1a1a' : 'white';
        }}
        
        // 3단계 중첩 트리맵 생성
        function create3LevelTreemap() {{
            const container = document.getElementById('nested-treemap');
            container.innerHTML = '';
            
            const width = container.offsetWidth - 20;
            const height = container.offsetHeight - 20;
            
            // 팀별 데이터 집계
            const teams = {{}};
            hierarchyData.forEach(item => {{
                const team = item.teams;
                const role = item.role_categories || 'NONE';
                const pos1 = item.position_1st;
                
                if (!teams[team]) {{
                    teams[team] = {{
                        count: 0,
                        roles: {{}}
                    }};
                }}
                teams[team].count++;
                
                if (!teams[team].roles[role]) {{
                    teams[team].roles[role] = {{
                        count: 0,
                        positions: {{}}
                    }};
                }}
                teams[team].roles[role].count++;
                
                if (!teams[team].roles[role].positions[pos1]) {{
                    teams[team].roles[role].positions[pos1] = 0;
                }}
                teams[team].roles[role].positions[pos1]++;
            }});
            
            // 팀 정렬 (인원 수 기준)
            const sortedTeams = Object.entries(teams)
                .sort((a, b) => b[1].count - a[1].count)
                .slice(0, 12); // 상위 12개 팀만 표시
            
            // Squarified Treemap 알고리즘으로 레벨 1 위치 계산
            const totalCount = sortedTeams.reduce((sum, [_, data]) => sum + data.count, 0);
            let currentX = 10;
            let currentY = 10;
            let rowHeight = height - 20;
            let rowWidth = 0;
            let currentRow = [];
            
            sortedTeams.forEach(([teamName, teamData], index) => {{
                const teamWidth = (teamData.count / totalCount) * (width - 20);
                
                // 새 행 시작 조건
                if (currentX + teamWidth > width - 10 && currentRow.length > 0) {{
                    // 현재 행 렌더링
                    renderRow(currentRow, currentX - rowWidth, currentY, rowWidth, rowHeight / 2);
                    
                    // 다음 행 준비
                    currentY += rowHeight / 2;
                    rowHeight = height - currentY - 10;
                    currentX = 10;
                    rowWidth = 0;
                    currentRow = [];
                }}
                
                currentRow.push({{
                    name: teamName,
                    data: teamData,
                    width: teamWidth
                }});
                rowWidth += teamWidth;
                currentX += teamWidth;
            }});
            
            // 마지막 행 렌더링
            if (currentRow.length > 0) {{
                renderRow(currentRow, 10, currentY, width - 20, rowHeight);
            }}
            
            function renderRow(rowTeams, x, y, totalWidth, height) {{
                let currentX = x;
                
                rowTeams.forEach(team => {{
                    const teamWidth = (team.width / rowTeams.reduce((sum, t) => sum + t.width, 0)) * totalWidth;
                    
                    // 팀 박스 (레벨 1)
                    const teamDiv = document.createElement('div');
                    teamDiv.className = 'treemap-level-1';
                    teamDiv.style.left = currentX + 'px';
                    teamDiv.style.top = y + 'px';
                    teamDiv.style.width = teamWidth + 'px';
                    teamDiv.style.height = height + 'px';
                    
                    // 변화율 계산
                    const stats = teamStats[team.name] || {{}};
                    const changePercent = stats.change_percent || 0;
                    teamDiv.style.backgroundColor = getColorForChange(changePercent);
                    
                    // 팀 레이블
                    const teamLabel = document.createElement('div');
                    teamLabel.className = 'treemap-label treemap-label-1';
                    teamLabel.textContent = teamWidth < 100 ? abbreviateText(team.name, 10) : team.name;
                    teamLabel.style.color = getTextColor(teamDiv.style.backgroundColor);
                    teamDiv.appendChild(teamLabel);
                    
                    // 팀 정보
                    const teamInfo = document.createElement('div');
                    teamInfo.className = 'treemap-info';
                    teamInfo.innerHTML = `${{team.data.count}}명<br>${{changePercent >= 0 ? '+' : ''}}${{changePercent.toFixed(1)}}%`;
                    teamInfo.style.color = getTextColor(teamDiv.style.backgroundColor);
                    teamDiv.appendChild(teamInfo);
                    
                    // 역할별 박스 (레벨 2)
                    let roleY = 25;
                    const sortedRoles = Object.entries(team.data.roles)
                        .sort((a, b) => b[1].count - a[1].count);
                    
                    sortedRoles.forEach(([roleName, roleData]) => {{
                        const roleHeight = (roleData.count / team.data.count) * (height - 30);
                        
                        if (roleHeight > 15) {{ // 최소 높이
                            const roleDiv = document.createElement('div');
                            roleDiv.className = 'treemap-level-2';
                            roleDiv.style.left = '5px';
                            roleDiv.style.top = roleY + 'px';
                            roleDiv.style.width = (teamWidth - 10) + 'px';
                            roleDiv.style.height = roleHeight + 'px';
                            roleDiv.style.backgroundColor = 'rgba(255,255,255,0.1)';
                            
                            // 역할 레이블
                            if (roleHeight > 25) {{
                                const roleLabel = document.createElement('div');
                                roleLabel.className = 'treemap-label treemap-label-2';
                                roleLabel.textContent = teamWidth < 150 ? abbreviateText(roleName, 8) : roleName;
                                roleDiv.appendChild(roleLabel);
                            }}
                            
                            // Position별 박스 (레벨 3)
                            let posX = 5;
                            const sortedPositions = Object.entries(roleData.positions)
                                .sort((a, b) => b[1] - a[1]);
                            
                            sortedPositions.forEach(([posName, posCount]) => {{
                                const posWidth = (posCount / roleData.count) * (teamWidth - 20);
                                
                                if (posWidth > 20) {{ // 최소 너비
                                    const posDiv = document.createElement('div');
                                    posDiv.className = 'treemap-level-3';
                                    posDiv.style.left = posX + 'px';
                                    posDiv.style.top = '20px';
                                    posDiv.style.width = posWidth + 'px';
                                    posDiv.style.height = (roleHeight - 25) + 'px';
                                    posDiv.style.backgroundColor = 'rgba(0,0,0,0.2)';
                                    
                                    // Position 텍스트
                                    const posText = document.createElement('div');
                                    if (posWidth < 60) {{
                                        posText.className = 'abbreviated';
                                        posText.textContent = abbreviateText(posName, 6);
                                    }} else {{
                                        posText.innerHTML = `${{posName}}<br>${{posCount}}명`;
                                    }}
                                    posDiv.appendChild(posText);
                                    
                                    // 클릭 이벤트 - Sunburst 차트 표시
                                    posDiv.onclick = () => showSunburstDetail(team.name, roleName, posName);
                                    
                                    roleDiv.appendChild(posDiv);
                                    posX += posWidth;
                                }}
                            }});
                            
                            teamDiv.appendChild(roleDiv);
                            roleY += roleHeight;
                        }}
                    }});
                    
                    // 팀 박스 클릭 이벤트
                    teamDiv.onclick = (e) => {{
                        if (e.target === teamDiv) {{
                            showSunburstDetail(team.name);
                        }}
                    }};
                    
                    container.appendChild(teamDiv);
                    currentX += teamWidth;
                }});
            }}
        }}
        
        // Sunburst 상세 뷰 표시
        function showSunburstDetail(team, role = null, position = null) {{
            const modal = document.getElementById('sunburstModal');
            const modalTitle = document.getElementById('modal-title');
            const modalStats = document.getElementById('modal-stats');
            
            // 제목 설정
            if (position) {{
                modalTitle.textContent = `${{team}} > ${{role}} > ${{position}} 상세 구조`;
            }} else if (role) {{
                modalTitle.textContent = `${{team}} > ${{role}} 상세 구조`;
            }} else {{
                modalTitle.textContent = `${{team}} 팀 상세 구조`;
            }}
            
            // Sunburst 데이터 준비
            const sunburstData = prepareSunburstData(team, role, position);
            
            // Sunburst 차트 생성
            const data = [{{
                type: 'sunburst',
                labels: sunburstData.labels,
                parents: sunburstData.parents,
                values: sunburstData.values,
                marker: {{
                    colors: sunburstData.colors
                }},
                textinfo: 'label+value',
                hovertemplate: '%{{label}}<br>인원: %{{value}}명<extra></extra>'
            }}];
            
            const layout = {{
                margin: {{t: 0, l: 0, r: 0, b: 0}},
                width: document.querySelector('.modal-content').offsetWidth - 40,
                height: 600
            }};
            
            Plotly.newPlot('sunburst-chart', data, layout);
            
            // 통계 정보 표시
            const stats = teamStats[team] || {{}};
            modalStats.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${{stats.current || 0}}</div>
                        <div class="stat-label">현재 인원</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${{stats.previous || 0}}</div>
                        <div class="stat-label">이전 월 인원</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value ${{stats.change >= 0 ? 'positive' : 'negative'}}">
                            ${{stats.change >= 0 ? '+' : ''}}${{stats.change || 0}}
                        </div>
                        <div class="stat-label">증감 인원</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value ${{stats.change_percent >= 0 ? 'positive' : 'negative'}}">
                            ${{stats.change_percent >= 0 ? '+' : ''}}${{(stats.change_percent || 0).toFixed(1)}}%
                        </div>
                        <div class="stat-label">증감률</div>
                    </div>
                </div>
            `;
            
            modal.style.display = 'block';
        }}
        
        // Sunburst 데이터 준비
        function prepareSunburstData(selectedTeam, selectedRole, selectedPosition) {{
            const labels = [];
            const parents = [];
            const values = [];
            const colors = [];
            
            // 색상 팔레트
            const colorPalette = [
                '#667eea', '#f56565', '#48bb78', '#ed8936', '#9f7aea',
                '#38b2ac', '#ed64a6', '#ecc94b', '#4299e1', '#a0aec0'
            ];
            
            // 필터링된 데이터
            let filteredData = hierarchyData;
            if (selectedTeam) {{
                filteredData = filteredData.filter(d => d.teams === selectedTeam);
            }}
            if (selectedRole) {{
                filteredData = filteredData.filter(d => d.role_categories === selectedRole);
            }}
            if (selectedPosition) {{
                filteredData = filteredData.filter(d => d.position_1st === selectedPosition);
            }}
            
            // 루트 노드
            labels.push(selectedPosition || selectedRole || selectedTeam || '전체');
            parents.push('');
            values.push(filteredData.length);
            colors.push('#e0e0e0');
            
            // 계층별 데이터 추가
            const processed = new Set();
            
            filteredData.forEach((item, index) => {{
                // Teams 레벨 (선택되지 않은 경우만)
                if (!selectedTeam && item.teams) {{
                    const key = item.teams;
                    if (!processed.has(key)) {{
                        labels.push(item.teams);
                        parents.push(labels[0]);
                        values.push(filteredData.filter(d => d.teams === item.teams).length);
                        colors.push(colorPalette[processed.size % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
                
                // Role Categories 레벨
                if (!selectedRole && item.role_categories) {{
                    const parentKey = selectedTeam || item.teams;
                    const key = `${{parentKey}}|${{item.role_categories}}`;
                    if (!processed.has(key)) {{
                        labels.push(item.role_categories);
                        parents.push(parentKey);
                        values.push(filteredData.filter(d => 
                            d.teams === item.teams && 
                            d.role_categories === item.role_categories
                        ).length);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
                
                // Position 1st 레벨
                if (!selectedPosition && item.position_1st) {{
                    const parentKey = selectedRole || item.role_categories || 'NONE';
                    const key = `${{parentKey}}|${{item.position_1st}}`;
                    if (!processed.has(key)) {{
                        labels.push(item.position_1st);
                        parents.push(parentKey);
                        values.push(filteredData.filter(d => 
                            d.teams === item.teams && 
                            d.role_categories === item.role_categories &&
                            d.position_1st === item.position_1st
                        ).length);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
                
                // Position 2nd 레벨
                if (item.position_2nd) {{
                    const parentKey = item.position_1st;
                    const key = `${{parentKey}}|${{item.position_2nd}}`;
                    if (!processed.has(key)) {{
                        labels.push(item.position_2nd);
                        parents.push(parentKey);
                        values.push(1);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
                
                // Position 3rd 레벨
                if (item.position_3rd) {{
                    const parentKey = item.position_2nd;
                    const key = `${{parentKey}}|${{item.position_3rd}}`;
                    if (!processed.has(key)) {{
                        labels.push(item.position_3rd);
                        parents.push(parentKey);
                        values.push(1);
                        colors.push(colorPalette[labels.length % colorPalette.length]);
                        processed.add(key);
                    }}
                }}
            }});
            
            return {{ labels, parents, values, colors }};
        }}
        
        // 범례 생성
        function createLegend() {{
            const legendContainer = document.getElementById('treemap-legend');
            const legendItems = [
                {{ color: '#00C851', label: '15% 이상 증가' }},
                {{ color: '#2ECC71', label: '10-15% 증가' }},
                {{ color: '#5CB85C', label: '5-10% 증가' }},
                {{ color: '#7FB069', label: '2-5% 증가' }},
                {{ color: '#90C695', label: '0-2% 증가' }},
                {{ color: '#757575', label: '변화 없음' }},
                {{ color: '#EF9A9A', label: '0-2% 감소' }},
                {{ color: '#E57373', label: '2-5% 감소' }},
                {{ color: '#D9534F', label: '5-10% 감소' }},
                {{ color: '#E74C3C', label: '10-15% 감소' }},
                {{ color: '#CC0000', label: '15% 이상 감소' }}
            ];
            
            legendItems.forEach(item => {{
                const legendItem = document.createElement('div');
                legendItem.className = 'legend-item';
                legendItem.innerHTML = `
                    <div class="legend-color" style="background-color: ${{item.color}}"></div>
                    <span>${{item.label}}</span>
                `;
                legendContainer.appendChild(legendItem);
            }});
        }}
        
        // 통계 카드 생성
        function createStatsCards() {{
            const statsGrid = document.getElementById('stats-grid');
            
            // 전체 통계 계산
            const totalCurrent = Object.values(teamStats).reduce((sum, team) => sum + (team.current || 0), 0);
            const totalPrevious = Object.values(teamStats).reduce((sum, team) => sum + (team.previous || 0), 0);
            const totalChange = totalCurrent - totalPrevious;
            const totalChangePercent = totalPrevious > 0 ? (totalChange / totalPrevious) * 100 : 0;
            
            const stats = [
                {{
                    label: '전체 인원',
                    value: totalCurrent,
                    change: totalChange,
                    changePercent: totalChangePercent
                }},
                {{
                    label: '팀 수',
                    value: Object.keys(teamStats).length,
                    change: 0,
                    changePercent: 0
                }},
                {{
                    label: '평균 팀 인원',
                    value: Math.round(totalCurrent / Object.keys(teamStats).length),
                    change: 0,
                    changePercent: 0
                }}
            ];
            
            stats.forEach(stat => {{
                const card = document.createElement('div');
                card.className = 'stat-card';
                
                const changeClass = stat.change > 0 ? 'positive' : stat.change < 0 ? 'negative' : 'neutral';
                const changeText = stat.change !== 0 ? 
                    `<div class="stat-change ${{changeClass}}">
                        ${{stat.change > 0 ? '+' : ''}}${{stat.change}}명 (${{stat.changePercent.toFixed(1)}}%)
                    </div>` : '';
                
                card.innerHTML = `
                    <div class="stat-value">${{stat.value}}</div>
                    <div class="stat-label">${{stat.label}}</div>
                    ${{changeText}}
                `;
                
                statsGrid.appendChild(card);
            }});
        }}
        
        // 모달 닫기 이벤트
        document.querySelector('.close').onclick = function() {{
            document.getElementById('sunburstModal').style.display = 'none';
        }}
        
        window.onclick = function(event) {{
            const modal = document.getElementById('sunburstModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // 페이지 로드 시 실행
        window.onload = function() {{
            create3LevelTreemap();
            createLegend();
            createStatsCards();
        }}
    </script>
</body>
</html>"""
        
        return html_content
        
    def save_dashboard(self, html_content):
        """대시보드 HTML 파일 저장"""
        output_dir = os.path.join(self.base_path, 'output_files')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f'3level_treemap_dashboard_{self.year}_{self.month:02d}.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Dashboard saved to: {output_file}")
        return output_file
        
    def run(self):
        """대시보드 생성 실행"""
        print("\n" + "="*60)
        print("🚀 3-Level Nested Treemap Dashboard Generator")
        print("="*60)
        
        # 데이터 로드
        self.load_data()
        
        # HTML 생성
        html_content = self.generate_dashboard_html()
        
        # 파일 저장
        output_file = self.save_dashboard(html_content)
        
        print("\n" + "="*60)
        print("✨ Dashboard generation complete!")
        print("="*60)
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate 3-Level Nested Treemap Dashboard')
    parser.add_argument('--month', type=int, default=8, help='Month (1-12)')
    parser.add_argument('--year', type=int, default=2025, help='Year')
    
    args = parser.parse_args()
    
    dashboard = Enhanced3LevelTreemapDashboard(args.month, args.year)
    output_file = dashboard.run()
    
    # 브라우저에서 자동 열기
    import webbrowser
    webbrowser.open(f'file://{os.path.abspath(output_file)}')

if __name__ == '__main__':
    main()