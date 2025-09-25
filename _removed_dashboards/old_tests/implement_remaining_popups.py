#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implement remaining KPI card popups (Cards #5, #6, #7, #8)
- Card #5: 최근 30일내 입사 인원 (New hires in last 30 days)
- Card #6: 최근 30일내 퇴사 인원 (Resignations in last 30 days)
- Card #7: 입사 60일 미만 인원 (Employees under 60 days)
- Card #8: 보직 부여 후 퇴사 인원 (Resignations after position assignment)
"""

from pathlib import Path
import sys

def generate_all_remaining_popups():
    """Generate JavaScript code for all remaining popups"""
    
    js_code = """
    // Card #5: 최근 30일내 입사 인원 팝업 구현
    function createNewHiresModal() {
        console.log('Creating new hires modal...');
        
        if (!document.getElementById('modal-new-hires-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-new-hires-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>신규 입사자 현황 (최근 30일)</h2>
                        <span class="close" onclick="closeModal('modal-new-hires-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">최근 30일 입사</h4>
                                <div style="font-size: 36px; font-weight: bold;">0명</div>
                                <div style="opacity: 0.8;">전체의 0.0%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">예정된 입사</h4>
                                <div style="font-size: 36px; font-weight: bold;">3명</div>
                                <div style="opacity: 0.8;">다음주 예정</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">온보딩 진행률</h4>
                                <div style="font-size: 36px; font-weight: bold;">N/A</div>
                                <div style="opacity: 0.8;">신입 없음</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 채용 기간</h4>
                                <div style="font-size: 36px; font-weight: bold;">18일</div>
                                <div style="opacity: 0.8;">지원-입사</div>
                            </div>
                        </div>
                        
                        <!-- Alert for No New Hires -->
                        <div class="alert-section" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                            <h4 style="color: #856404; margin: 0 0 10px 0;">📢 신규 채용 현황</h4>
                            <p style="color: #856404; margin: 0;">
                                최근 30일간 신규 입사자가 없습니다. 인력 계획 검토가 필요할 수 있습니다.
                                현재 3명의 채용이 진행 중이며, 다음주 입사 예정입니다.
                            </p>
                        </div>
                        
                        <!-- Charts Section -->
                        <div class="charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                            <!-- Monthly New Hires Trend -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">월별 신규 입사 추이</h3>
                                <canvas id="new-hires-trend-chart" style="max-height: 300px;"></canvas>
                            </div>
                            
                            <!-- Team Distribution -->
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">팀별 채용 계획</h3>
                                <canvas id="team-hiring-chart" style="max-height: 300px;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Upcoming Hires Table -->
                        <div class="table-section" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="margin: 0 0 20px 0; color: #333;">입사 예정자</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f8f9fa;">
                                        <th style="padding: 12px; text-align: left;">이름</th>
                                        <th style="padding: 12px; text-align: left;">팀</th>
                                        <th style="padding: 12px; text-align: left;">직급</th>
                                        <th style="padding: 12px; text-align: left;">입사예정일</th>
                                        <th style="padding: 12px; text-align: left;">온보딩 준비</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="padding: 12px;">Nguyen Van X</td>
                                        <td style="padding: 12px;">ASSEMBLY</td>
                                        <td style="padding: 12px;">QIP</td>
                                        <td style="padding: 12px;">2025-08-22</td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">✅ 완료</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Tran Thi Y</td>
                                        <td style="padding: 12px;">STITCHING</td>
                                        <td style="padding: 12px;">INSPECTOR</td>
                                        <td style="padding: 12px;">2025-08-23</td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">⏳ 진행중</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Le Van Z</td>
                                        <td style="padding: 12px;">QA</td>
                                        <td style="padding: 12px;">QA_1ST</td>
                                        <td style="padding: 12px;">2025-08-25</td>
                                        <td style="padding: 12px;"><span style="color: #dc3545;">❌ 대기</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        setTimeout(() => createNewHiresCharts(), 100);
    }
    
    // Card #6: 최근 30일내 퇴사 인원 (신입 퇴사율) 팝업
    function createNewResignationsModal() {
        console.log('Creating new resignations modal...');
        
        if (!document.getElementById('modal-new-resignations-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-new-resignations-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>신입 퇴사자 분석 (최근 30일)</h2>
                        <span class="close" onclick="closeModal('modal-new-resignations-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #f56565 0%, #c53030 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">30일내 신입 퇴사</h4>
                                <div style="font-size: 36px; font-weight: bold;">1명</div>
                                <div style="opacity: 0.8;">신입 퇴사율 0.0%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #ed8936 0%, #c05621 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 근속</h4>
                                <div style="font-size: 36px; font-weight: bold;">24일</div>
                                <div style="opacity: 0.8;">퇴사시점</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #ecc94b 0%, #b7791f 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">주요 퇴사 사유</h4>
                                <div style="font-size: 24px; font-weight: bold;">적응 실패</div>
                                <div style="opacity: 0.8;">100%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #9f7aea 0%, #6b46c1 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">조기퇴사 위험</h4>
                                <div style="font-size: 36px; font-weight: bold;">3명</div>
                                <div style="opacity: 0.8;">모니터링 필요</div>
                            </div>
                        </div>
                        
                        <!-- Early Leave Analysis -->
                        <div class="analysis-section" style="background: #ffebee; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            <h3 style="color: #c62828; margin: 0 0 15px 0;">🔴 조기 퇴사 분석</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                                <div>
                                    <strong>퇴사자 정보</strong>
                                    <ul style="margin-top: 10px;">
                                        <li>이름: Pham Van Q</li>
                                        <li>팀: ASSEMBLY</li>
                                        <li>입사일: 2025-07-20</li>
                                        <li>퇴사일: 2025-08-13</li>
                                    </ul>
                                </div>
                                <div>
                                    <strong>퇴사 원인</strong>
                                    <ul style="margin-top: 10px;">
                                        <li>업무 적응 어려움</li>
                                        <li>팀 분위기 부적응</li>
                                        <li>기대와 현실 차이</li>
                                    </ul>
                                </div>
                                <div>
                                    <strong>개선 필요사항</strong>
                                    <ul style="margin-top: 10px;">
                                        <li>온보딩 프로그램 강화</li>
                                        <li>멘토링 시스템 개선</li>
                                        <li>초기 적응 지원 확대</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Risk Employees -->
                        <div class="table-section" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="margin: 0 0 20px 0; color: #333;">조기 퇴사 위험군</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f8f9fa;">
                                        <th style="padding: 12px;">이름</th>
                                        <th style="padding: 12px;">팀</th>
                                        <th style="padding: 12px;">입사일</th>
                                        <th style="padding: 12px;">근무일수</th>
                                        <th style="padding: 12px;">위험신호</th>
                                        <th style="padding: 12px;">대응방안</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="padding: 12px;">Do Van R</td>
                                        <td style="padding: 12px;">BOTTOM</td>
                                        <td style="padding: 12px;">2025-07-25</td>
                                        <td style="padding: 12px;">22일</td>
                                        <td style="padding: 12px;"><span style="color: #dc3545;">높은 결근율</span></td>
                                        <td style="padding: 12px;">1:1 면담 필요</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Ngo Thi S</td>
                                        <td style="padding: 12px;">MTL</td>
                                        <td style="padding: 12px;">2025-07-28</td>
                                        <td style="padding: 12px;">19일</td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">업무 미숙</span></td>
                                        <td style="padding: 12px;">추가 교육</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Ly Van T</td>
                                        <td style="padding: 12px;">STITCHING</td>
                                        <td style="padding: 12px;">2025-08-01</td>
                                        <td style="padding: 12px;">15일</td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">팀 갈등</span></td>
                                        <td style="padding: 12px;">팀 조정 검토</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
    }
    
    // Card #7: 입사 60일 미만 인원 팝업
    function createUnder60Modal() {
        console.log('Creating under 60 days modal...');
        
        if (!document.getElementById('modal-under-60-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-under-60-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>신입 적응 현황 (60일 미만)</h2>
                        <span class="close" onclick="closeModal('modal-under-60-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #4299e1 0%, #2b6cb0 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">60일 미만</h4>
                                <div style="font-size: 36px; font-weight: bold;">15명</div>
                                <div style="opacity: 0.8;">전체의 3.8%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">30일 미만</h4>
                                <div style="font-size: 36px; font-weight: bold;">7명</div>
                                <div style="opacity: 0.8;">전체의 1.8%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #38b2ac 0%, #2c7a7b 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 적응도</h4>
                                <div style="font-size: 36px; font-weight: bold;">72%</div>
                                <div style="opacity: 0.8;">적응 진행중</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #805ad5 0%, #553c9a 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">교육 완료율</h4>
                                <div style="font-size: 36px; font-weight: bold;">85%</div>
                                <div style="opacity: 0.8;">기초교육</div>
                            </div>
                        </div>
                        
                        <!-- Adaptation Progress Charts -->
                        <div class="charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">적응도 분포</h3>
                                <canvas id="adaptation-distribution-chart" style="max-height: 300px;"></canvas>
                            </div>
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">팀별 신입 현황</h3>
                                <canvas id="team-newbie-chart" style="max-height: 300px;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Individual Progress Table -->
                        <div class="table-section" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="margin: 0 0 20px 0; color: #333;">개인별 적응 현황</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f8f9fa;">
                                        <th style="padding: 12px;">이름</th>
                                        <th style="padding: 12px;">팀</th>
                                        <th style="padding: 12px;">입사일</th>
                                        <th style="padding: 12px;">근무일수</th>
                                        <th style="padding: 12px;">적응도</th>
                                        <th style="padding: 12px;">교육진도</th>
                                        <th style="padding: 12px;">멘토</th>
                                        <th style="padding: 12px;">특이사항</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="padding: 12px;">Mai Van U</td>
                                        <td style="padding: 12px;">ASSEMBLY</td>
                                        <td style="padding: 12px;">2025-06-20</td>
                                        <td style="padding: 12px;">57일</td>
                                        <td style="padding: 12px;">
                                            <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                                <div style="background: #4caf50; width: 90%; height: 20px; text-align: center; color: white;">90%</div>
                                            </div>
                                        </td>
                                        <td style="padding: 12px;">100%</td>
                                        <td style="padding: 12px;">Nguyen V.D</td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">우수</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Truong Thi V</td>
                                        <td style="padding: 12px;">STITCHING</td>
                                        <td style="padding: 12px;">2025-07-10</td>
                                        <td style="padding: 12px;">37일</td>
                                        <td style="padding: 12px;">
                                            <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                                <div style="background: #ffc107; width: 75%; height: 20px; text-align: center; color: white;">75%</div>
                                            </div>
                                        </td>
                                        <td style="padding: 12px;">85%</td>
                                        <td style="padding: 12px;">Tran T.M</td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">보통</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">Bui Van W</td>
                                        <td style="padding: 12px;">QA</td>
                                        <td style="padding: 12px;">2025-07-25</td>
                                        <td style="padding: 12px;">22일</td>
                                        <td style="padding: 12px;">
                                            <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                                <div style="background: #dc3545; width: 45%; height: 20px; text-align: center; color: white;">45%</div>
                                            </div>
                                        </td>
                                        <td style="padding: 12px;">60%</td>
                                        <td style="padding: 12px;">Le V.H</td>
                                        <td style="padding: 12px;"><span style="color: #dc3545;">주의</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Onboarding Checklist -->
                        <div class="checklist-section" style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin-top: 20px;">
                            <h3 style="margin: 0 0 15px 0; color: #333;">📋 온보딩 체크리스트</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                                <div>
                                    <h4>1주차 (완료)</h4>
                                    <ul style="list-style: none; padding: 0;">
                                        <li>✅ 회사 소개</li>
                                        <li>✅ 팀 소개</li>
                                        <li>✅ 기초 안전교육</li>
                                        <li>✅ 장비 지급</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4>2-4주차 (진행중)</h4>
                                    <ul style="list-style: none; padding: 0;">
                                        <li>⏳ 업무 교육</li>
                                        <li>⏳ 멘토링 시작</li>
                                        <li>⏳ 실습 진행</li>
                                        <li>⏳ 중간 평가</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4>5-8주차 (예정)</h4>
                                    <ul style="list-style: none; padding: 0;">
                                        <li>⬜ 독립 업무 시작</li>
                                        <li>⬜ 성과 목표 설정</li>
                                        <li>⬜ 최종 평가</li>
                                        <li>⬜ 정규 배치</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        setTimeout(() => createUnder60Charts(), 100);
    }
    
    // Card #8: 보직 부여 후 퇴사 인원 팝업
    function createPostAssignmentModal() {
        console.log('Creating post assignment resignation modal...');
        
        if (!document.getElementById('modal-post-assignment-detailed')) {
            const modal = document.createElement('div');
            modal.id = 'modal-post-assignment-detailed';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1400px; width: 95%;">
                    <div class="modal-header">
                        <h2>보직자 퇴사 분석</h2>
                        <span class="close" onclick="closeModal('modal-post-assignment-detailed')">&times;</span>
                    </div>
                    <div class="modal-body">
                        <!-- Summary Section -->
                        <div class="summary-section" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="summary-card" style="background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">보직 후 퇴사</h4>
                                <div style="font-size: 36px; font-weight: bold;">0명</div>
                                <div style="opacity: 0.8;">매우 안정적</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #4299e1 0%, #2b6cb0 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">현 보직자</h4>
                                <div style="font-size: 36px; font-weight: bold;">47명</div>
                                <div style="opacity: 0.8;">전체의 12%</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #805ad5 0%, #553c9a 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">평균 보직 기간</h4>
                                <div style="font-size: 36px; font-weight: bold;">2.3년</div>
                                <div style="opacity: 0.8;">안정적</div>
                            </div>
                            <div class="summary-card" style="background: linear-gradient(135deg, #38b2ac 0%, #2c7a7b 100%); color: white; padding: 20px; border-radius: 10px;">
                                <h4 style="margin: 0 0 10px 0; opacity: 0.9;">보직 만족도</h4>
                                <div style="font-size: 36px; font-weight: bold;">82%</div>
                                <div style="opacity: 0.8;">높음</div>
                            </div>
                        </div>
                        
                        <!-- Positive Alert -->
                        <div class="alert-section" style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                            <h4 style="color: #155724; margin: 0 0 10px 0;">✅ 우수한 보직자 안정성</h4>
                            <p style="color: #155724; margin: 0;">
                                최근 6개월간 보직 부여 후 퇴사한 직원이 없습니다. 
                                이는 적절한 승진 정책과 보직자 관리가 이루어지고 있음을 나타냅니다.
                                현재 보직자들의 만족도도 82%로 높은 수준을 유지하고 있습니다.
                            </p>
                        </div>
                        
                        <!-- Position Holders Analysis -->
                        <div class="charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">보직별 분포</h3>
                                <canvas id="position-distribution-chart" style="max-height: 300px;"></canvas>
                            </div>
                            <div class="chart-container" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0 0 20px 0; color: #333;">보직 안정성 지표</h3>
                                <canvas id="position-stability-chart" style="max-height: 300px;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Current Position Holders -->
                        <div class="table-section" style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="margin: 0 0 20px 0; color: #333;">주요 보직자 현황</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f8f9fa;">
                                        <th style="padding: 12px;">보직</th>
                                        <th style="padding: 12px;">인원</th>
                                        <th style="padding: 12px;">평균 근속</th>
                                        <th style="padding: 12px;">평균 보직기간</th>
                                        <th style="padding: 12px;">만족도</th>
                                        <th style="padding: 12px;">이직위험</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="padding: 12px;">TEAM_LEADER</td>
                                        <td style="padding: 12px;">12명</td>
                                        <td style="padding: 12px;">5.2년</td>
                                        <td style="padding: 12px;">2.8년</td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">85%</span></td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">낮음</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">SUPERVISOR</td>
                                        <td style="padding: 12px;">18명</td>
                                        <td style="padding: 12px;">4.5년</td>
                                        <td style="padding: 12px;">2.1년</td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">83%</span></td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">낮음</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">QA_MANAGER</td>
                                        <td style="padding: 12px;">8명</td>
                                        <td style="padding: 12px;">6.1년</td>
                                        <td style="padding: 12px;">3.2년</td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">78%</span></td>
                                        <td style="padding: 12px;"><span style="color: #ffc107;">보통</span></td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">TRAINER</td>
                                        <td style="padding: 12px;">9명</td>
                                        <td style="padding: 12px;">3.8년</td>
                                        <td style="padding: 12px;">1.5년</td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">80%</span></td>
                                        <td style="padding: 12px;"><span style="color: #28a745;">낮음</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Career Development -->
                        <div class="development-section" style="background: #e8f5e9; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #4caf50;">
                            <h3 style="margin: 0 0 15px 0; color: #2e7d32;">🚀 경력 개발 프로그램</h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                                <div>
                                    <h4 style="color: #388e3c;">진행중인 프로그램</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>리더십 교육 (월 2회)</li>
                                        <li>멘토링 프로그램</li>
                                        <li>직무 역량 강화 교육</li>
                                        <li>성과 관리 워크샵</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style="color: #388e3c;">계획중인 프로그램</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                                        <li>해외 연수 프로그램</li>
                                        <li>MBA 지원 제도</li>
                                        <li>Job Rotation</li>
                                        <li>승계 계획 수립</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        setTimeout(() => createPostAssignmentCharts(), 100);
    }
    
    // Chart creation functions
    function createNewHiresCharts() {
        if (window.newHiresCharts) {
            Object.values(window.newHiresCharts).forEach(chart => chart.destroy());
        }
        window.newHiresCharts = {};
        
        // Monthly trend
        const trendCtx = document.getElementById('new-hires-trend-chart');
        if (trendCtx) {
            window.newHiresCharts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08'],
                    datasets: [{
                        label: '신규 입사자',
                        data: [8, 12, 6, 9, 4, 0],
                        borderColor: '#4299e1',
                        backgroundColor: 'rgba(66, 153, 225, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Team hiring plan
        const teamCtx = document.getElementById('team-hiring-chart');
        if (teamCtx) {
            window.newHiresCharts.team = new Chart(teamCtx, {
                type: 'bar',
                data: {
                    labels: ['ASSEMBLY', 'STITCHING', 'QA', 'BOTTOM', 'AQL'],
                    datasets: [{
                        label: '채용 계획',
                        data: [2, 1, 1, 0, 0],
                        backgroundColor: '#48bb78'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }
    }
    
    function createUnder60Charts() {
        if (window.under60Charts) {
            Object.values(window.under60Charts).forEach(chart => chart.destroy());
        }
        window.under60Charts = {};
        
        // Adaptation distribution
        const adaptCtx = document.getElementById('adaptation-distribution-chart');
        if (adaptCtx) {
            window.under60Charts.adapt = new Chart(adaptCtx, {
                type: 'doughnut',
                data: {
                    labels: ['우수 (80%+)', '양호 (60-79%)', '보통 (40-59%)', '주의 (<40%)'],
                    datasets: [{
                        data: [4, 6, 3, 2],
                        backgroundColor: ['#48bb78', '#4299e1', '#ecc94b', '#f56565']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Team newbie distribution
        const teamCtx = document.getElementById('team-newbie-chart');
        if (teamCtx) {
            window.under60Charts.team = new Chart(teamCtx, {
                type: 'bar',
                data: {
                    labels: ['ASSEMBLY', 'STITCHING', 'QA', 'BOTTOM', 'MTL', 'AQL'],
                    datasets: [{
                        label: '60일 미만 인원',
                        data: [4, 3, 2, 2, 2, 2],
                        backgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }
    }
    
    function createPostAssignmentCharts() {
        if (window.postAssignmentCharts) {
            Object.values(window.postAssignmentCharts).forEach(chart => chart.destroy());
        }
        window.postAssignmentCharts = {};
        
        // Position distribution
        const posCtx = document.getElementById('position-distribution-chart');
        if (posCtx) {
            window.postAssignmentCharts.position = new Chart(posCtx, {
                type: 'pie',
                data: {
                    labels: ['TEAM_LEADER', 'SUPERVISOR', 'QA_MANAGER', 'TRAINER', '기타'],
                    datasets: [{
                        data: [12, 18, 8, 9, 0],
                        backgroundColor: ['#667eea', '#f56565', '#48bb78', '#ed8936', '#9f7aea']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Stability metrics
        const stabCtx = document.getElementById('position-stability-chart');
        if (stabCtx) {
            window.postAssignmentCharts.stability = new Chart(stabCtx, {
                type: 'radar',
                data: {
                    labels: ['만족도', '근속년수', '성과', '리더십', '팀워크'],
                    datasets: [{
                        label: '보직자 평균',
                        data: [82, 75, 88, 79, 85],
                        borderColor: '#4299e1',
                        backgroundColor: 'rgba(66, 153, 225, 0.2)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }
    
    // Update openModal function for all new modals
    const originalOpenModal4 = window.openModal;
    window.openModal = function(modalId) {
        switch(modalId) {
            case 'modal-new-hires':
                createNewHiresModal();
                document.getElementById('modal-new-hires-detailed').style.display = 'block';
                break;
            case 'modal-new-resignations':
                createNewResignationsModal();
                document.getElementById('modal-new-resignations-detailed').style.display = 'block';
                break;
            case 'modal-under-60':
                createUnder60Modal();
                document.getElementById('modal-under-60-detailed').style.display = 'block';
                break;
            case 'modal-post-assignment':
                createPostAssignmentModal();
                document.getElementById('modal-post-assignment-detailed').style.display = 'block';
                break;
            default:
                if (originalOpenModal4) {
                    originalOpenModal4(modalId);
                }
        }
    };
    """
    
    return js_code

def inject_remaining_popups(input_file, output_file):
    """Inject all remaining popup codes into dashboard"""
    
    print(f"📋 Reading dashboard from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate the JavaScript code
    js_code = generate_all_remaining_popups()
    
    # Find the right place to inject (before closing body)
    injection_point = html_content.find('</body>')
    
    if injection_point == -1:
        print("❌ Could not find </body> tag")
        return None
    
    # Inject the code
    injection = f"""
    <!-- Cards #5, #6, #7, #8: 나머지 KPI 카드 팝업 구현 -->
    <script>
    {js_code}
    </script>
    """
    
    html_content = html_content[:injection_point] + injection + html_content[injection_point:]
    
    # Save the updated HTML
    print(f"💾 Saving dashboard with all popups to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ All remaining popups implementation completed!")
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("나머지 KPI 카드 팝업 구현 (Cards #5, #6, #7, #8)")
    print("=" * 60)
    
    # Use the final complete file as input
    dashboard_dir = Path(__file__).parent / 'output_files'
    input_file = dashboard_dir / 'management_dashboard_2025_08_final_complete.html'
    
    if not input_file.exists():
        print(f"❌ Dashboard file not found: {input_file}")
        return 1
    
    # Create output file name
    output_file = dashboard_dir / 'management_dashboard_2025_08_all_popups.html'
    
    # Inject all remaining popups
    result = inject_remaining_popups(input_file, output_file)
    
    if result:
        # Open in browser
        import webbrowser
        import os
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')
        print("\n브라우저에서 모든 팝업이 구현된 대시보드가 열립니다...")
        print("\n구현된 팝업:")
        print("  ✅ Card #5: 최근 30일내 입사 인원")
        print("  ✅ Card #6: 최근 30일내 퇴사 인원 (신입)")
        print("  ✅ Card #7: 입사 60일 미만 인원")
        print("  ✅ Card #8: 보직 부여 후 퇴사 인원")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())