"""
Absence Analytics Language Configuration
다국어 지원을 위한 언어 설정 파일
Currently: Korean only, prepared for English and Vietnamese
"""

# Language configuration
LANGUAGES = {
    'ko': {
        # Modal Header
        'modal_title': '결근 현황 상세 분석',
        'close_button': '×',
        
        # Tab Names
        'tab_summary': '📊 요약',
        'tab_detailed': '📈 상세분석',
        'tab_team': '👥 팀별',
        'tab_individual': '👤 개인별',
        
        # Summary Tab - KPI Cards
        'kpi_total_employees': '전체 직원 수',
        'kpi_total_employees_desc': '활성 QIP 직원',
        'kpi_absence_rate': '8월 결근율',
        'kpi_absence_rate_desc': '출산휴가 제외',
        'kpi_high_risk': '고위험 인원',
        'kpi_high_risk_desc': '즉시 조치 필요',
        
        # Summary Tab - Charts
        'chart_risk_distribution': '위험도 분포',
        'chart_absence_category': '결근 사유 분포 (출산휴가 제외)',
        
        # Summary Tab - Statistics
        'stats_title': '📊 주요 지표',
        'stats_total_absence_days': '총 결근일수',
        'stats_avg_absence_days': '평균 결근일수',
        'stats_maternity_count': '출산휴가 인원',
        'stats_maternity_days': '출산휴가 일수',
        'stats_maternity_note': '(결근율 계산에서 제외)',
        
        # Detailed Analysis Tab
        'detailed_title': '📊 결근 상세 분석',
        'detailed_charts': {
            'monthly_trend': '월별 결근율 추이',
            'weekly_pattern': '요일별 결근 패턴',
            'daily_trend': '일별 결근 추이 (8월)',
            'team_comparison': '팀별 결근율 비교',
            'reason_analysis': '결근 사유 분석',
            'risk_trend': '위험도 추이',
            'absence_distribution': '결근일수 분포',
            'unauthorized_analysis': '무단결근 분석',
            'department_heatmap': '부서별 결근 히트맵',
            'recovery_pattern': '복귀 패턴 분석',
            'prediction': '결근 예측 모델',
            'cost_impact': '비용 영향 분석'
        },
        
        # Team Tab
        'team_title': '👥 팀별 결근 현황',
        'team_table_headers': {
            'team_name': '팀명',
            'employee_count': '인원',
            'total_working_days': '총 근무일수',
            'total_absence_days': '총 결근일수',
            'absence_rate': '결근율',
            'high_risk_count': '고위험',
            'action': '상세'
        },
        'team_total_row': '총합',
        'team_detail_button': '상세',
        
        # Team Detail Popup
        'team_popup_title': '팀 상세 정보',
        'team_popup_kpi': {
            'total_members': '팀원 수',
            'avg_absence': '평균 결근일수',
            'team_absence_rate': '팀 결근율',
            'high_risk': '고위험 인원'
        },
        'team_popup_chart_title': '월별 결근 추이',
        'team_popup_members_title': '팀원 목록',
        'team_popup_member_columns': {
            'name': '이름',
            'absence_days': '결근일수',
            'absence_rate': '결근율',
            'risk_level': '위험도'
        },
        'team_popup_reasons_title': '결근 사유 분포',
        
        # Individual Tab
        'individual_title': '👤 개인별 결근 현황',
        'individual_search': '직원 검색...',
        'individual_table_headers': {
            'employee_no': '사번',
            'name': '이름',
            'team': '팀',
            'absence_days': '결근일수',
            'absence_rate': '결근율',
            'risk_level': '위험도',
            'action': '상세'
        },
        'individual_detail_button': '상세',
        
        # Individual Detail Popup
        'individual_popup_title': '개인 결근 상세',
        'individual_popup_info': {
            'employee_no': '사번',
            'name': '이름',
            'team': '팀',
            'position': '직위'
        },
        'individual_popup_stats': {
            'total_absence': '총 결근일수',
            'absence_rate': '결근율',
            'risk_level': '위험도',
            'last_absence': '최근 결근일'
        },
        'individual_popup_history_title': '결근 이력',
        'individual_popup_trend_title': '월별 결근 추이',
        
        # Risk Levels
        'risk_levels': {
            'high': '고위험',
            'medium': '중위험',
            'low': '저위험'
        },
        
        # Absence Categories
        'absence_categories': {
            'planned': '계획된 휴가',
            'medical': '병가',
            'disciplinary': '무단결근',
            'legal': '법적 의무',
            'maternity_leave': '출산/육아휴가',
            'other': '기타'
        },
        
        # Common Terms
        'common': {
            'days': '일',
            'people': '명',
            'percent': '%',
            'month': '월',
            'year': '년',
            'loading': '로딩 중...',
            'no_data': '데이터 없음',
            'error': '오류 발생',
            'close': '닫기',
            'export': '내보내기',
            'print': '인쇄'
        }
    },
    # Prepared for future languages
    'en': {},  # English - To be added
    'vi': {}   # Vietnamese - To be added
}

def get_text(lang='ko', key_path=''):
    """
    Get translated text for the given key path
    
    Args:
        lang: Language code ('ko', 'en', 'vi')
        key_path: Dot-separated path to the text key (e.g., 'modal_title' or 'team_table_headers.team_name')
    
    Returns:
        Translated text or key if not found
    """
    if lang not in LANGUAGES:
        lang = 'ko'  # Default to Korean
    
    keys = key_path.split('.')
    value = LANGUAGES[lang]
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return key_path  # Return key if translation not found

def get_language_json(lang='ko'):
    """
    Get the entire language dictionary as JSON-compatible dict
    
    Args:
        lang: Language code ('ko', 'en', 'vi')
    
    Returns:
        Dictionary with all translations for the language
    """
    if lang not in LANGUAGES:
        lang = 'ko'
    
    return LANGUAGES[lang]