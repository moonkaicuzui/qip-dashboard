#!/usr/bin/env python3
"""
Translation system update script
Adds all missing translations for validation tab, modals, and hardcoded text
"""

import json
import os

def update_translations():
    """Update dashboard_translations.json with missing translations"""

    # Load existing translations
    translations_path = 'config_files/dashboard_translations.json'
    with open(translations_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Add missing modal translations
    if 'modals' not in translations:
        translations['modals'] = {}

    # Area AQL modal translations
    translations['modals']['areaAQL'] = {
        'title': {
            'ko': '구역별 AQL 상태 및 조건 7번/8번 분석',
            'en': 'Area AQL Status and Conditions 7/8 Analysis',
            'vi': 'Trạng thái AQL theo khu vực và phân tích điều kiện 7/8'
        },
        'condition7': {
            'ko': '조건 7번: 팀/구역 AQL 3개월 연속 실패',
            'en': 'Condition 7: Team/Area AQL 3-month consecutive failure',
            'vi': 'Điều kiện 7: Thất bại AQL khu vực/nhóm liên tiếp 3 tháng'
        },
        'condition8': {
            'ko': '조건 8번: 구역 Reject Rate 3% 초과',
            'en': 'Condition 8: Area Reject Rate exceeds 3%',
            'vi': 'Điều kiện 8: Tỷ lệ từ chối khu vực vượt quá 3%'
        },
        'areaStatistics': {
            'ko': '구역별 Reject Rate 통계',
            'en': 'Area Reject Rate Statistics',
            'vi': 'Thống kê tỷ lệ từ chối theo khu vực'
        },
        'employeeDetails': {
            'ko': '조건 미충족 직원 상세',
            'en': 'Employees Not Meeting Conditions',
            'vi': 'Chi tiết nhân viên không đạt điều kiện'
        },
        'area': {
            'ko': '구역',
            'en': 'Area',
            'vi': 'Khu vực'
        },
        'totalEmployees': {
            'ko': '전체 인원',
            'en': 'Total Employees',
            'vi': 'Tổng nhân viên'
        },
        'cond7Fail': {
            'ko': '조건7 미충족',
            'en': 'Cond.7 Fail',
            'vi': 'ĐK7 không đạt'
        },
        'cond8Fail': {
            'ko': '조건8 미충족',
            'en': 'Cond.8 Fail',
            'vi': 'ĐK8 không đạt'
        },
        'totalAQL': {
            'ko': '총 AQL 건수',
            'en': 'Total AQL',
            'vi': 'Tổng AQL'
        },
        'pass': {
            'ko': 'PASS',
            'en': 'PASS',
            'vi': 'ĐẠT'
        },
        'fail': {
            'ko': 'FAIL',
            'en': 'FAIL',
            'vi': 'THẤT BẠI'
        },
        'rejectRate': {
            'ko': 'Reject Rate',
            'en': 'Reject Rate',
            'vi': 'Tỷ lệ từ chối'
        }
    }

    # 5PRS modal translations
    translations['modals']['fprs'] = {
        'lowPassRateTitle': {
            'ko': '5PRS 통과율 95% 미만 직원 상세',
            'en': '5PRS Pass Rate Below 95% Employee Details',
            'vi': 'Chi tiết nhân viên có tỷ lệ đạt 5PRS dưới 95%'
        },
        'lowInspectionTitle': {
            'ko': '5PRS 검증 수량 100개 미만 직원 상세',
            'en': '5PRS Inspection Below 100 Pairs Employee Details',
            'vi': 'Chi tiết nhân viên kiểm tra 5PRS dưới 100 đôi'
        },
        'positionHierarchy': {
            'ko': '직책 (1단계 > 2단계 > 3단계)',
            'en': 'Position (Level 1 > 2 > 3)',
            'vi': 'Chức vụ (Cấp 1 > 2 > 3)'
        },
        'totalTests': {
            'ko': '총 검증',
            'en': 'Total Tests',
            'vi': 'Tổng kiểm tra'
        },
        'passCount': {
            'ko': 'PASS',
            'en': 'PASS',
            'vi': 'ĐẠT'
        },
        'passRate': {
            'ko': '통과율',
            'en': 'Pass Rate',
            'vi': 'Tỷ lệ đạt'
        },
        'inspectionQty': {
            'ko': '검증 수량',
            'en': 'Inspection Qty',
            'vi': 'Số lượng kiểm tra'
        },
        'conditionMet': {
            'ko': '조건 충족',
            'en': 'Condition Met',
            'vi': 'Đạt điều kiện'
        },
        'conditionNotMet': {
            'ko': '미충족',
            'en': 'Not Met',
            'vi': 'Không đạt'
        },
        'met': {
            'ko': '충족',
            'en': 'Met',
            'vi': 'Đạt'
        }
    }

    # Common table headers
    translations['common'] = translations.get('common', {})
    translations['common']['tableHeaders'] = {
        'employeeNo': {
            'ko': '사번',
            'en': 'Emp No',
            'vi': 'Mã NV'
        },
        'name': {
            'ko': '이름',
            'en': 'Name',
            'vi': 'Tên'
        },
        'position': {
            'ko': '직책',
            'en': 'Position',
            'vi': 'Chức vụ'
        },
        'conditionExplanation': {
            'ko': '조건 설명',
            'en': 'Condition Description',
            'vi': 'Mô tả điều kiện'
        },
        'conditionStatus': {
            'ko': '조건 충족',
            'en': 'Condition Status',
            'vi': 'Trạng thái điều kiện'
        }
    }

    # Validation tab KPI cards
    if 'validationTab' not in translations:
        translations['validationTab'] = {}

    translations['validationTab']['kpiCards'] = {
        'totalWorkingDays': {
            'title': {
                'ko': '총 근무일수',
                'en': 'Total Working Days',
                'vi': 'Tổng ngày làm việc'
            },
            'unit': {
                'ko': '일',
                'en': 'days',
                'vi': 'ngày'
            }
        },
        'unauthorizedAbsence': {
            'title': {
                'ko': '무단결근 3일 이상',
                'en': 'Unauthorized Absence ≥3 Days',
                'vi': 'Vắng không phép ≥3 ngày'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'lowAttendance': {
            'title': {
                'ko': '출근율 88% 미만',
                'en': 'Attendance Rate <88%',
                'vi': 'Tỷ lệ chấm công <88%'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'minWorkingDays': {
            'title': {
                'ko': '최소 근무일 미충족',
                'en': 'Min Working Days Not Met',
                'vi': 'Không đạt ngày làm việc tối thiểu'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'aqlConsecutiveFail': {
            'title': {
                'ko': 'AQL 3개월 연속 실패',
                'en': 'AQL 3-Month Consecutive Fail',
                'vi': 'AQL thất bại 3 tháng liên tiếp'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'lowPassRate': {
            'title': {
                'ko': '5PRS 통과율 95% 미만',
                'en': '5PRS Pass Rate <95%',
                'vi': 'Tỷ lệ đạt 5PRS <95%'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'lowInspectionQty': {
            'title': {
                'ko': '5PRS 검증 100개 미만',
                'en': '5PRS Inspection <100 Pairs',
                'vi': 'Kiểm tra 5PRS <100 đôi'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        },
        'areaRejectRate': {
            'title': {
                'ko': '구역 AQL Reject 3% 이상',
                'en': 'Area AQL Reject >3%',
                'vi': 'Tỷ lệ từ chối AQL khu vực >3%'
            },
            'unit': {
                'ko': '명',
                'en': 'people',
                'vi': 'người'
            }
        }
    }

    # Condition explanations
    translations['conditions'] = translations.get('conditions', {})
    translations['conditions']['descriptions'] = {
        'teamAreaAQL': {
            'ko': '팀/구역 AQL',
            'en': 'Team/Area AQL',
            'vi': 'AQL nhóm/khu vực'
        },
        'areaRejectRate': {
            'ko': '담당구역 AQL Reject율',
            'en': 'Area AQL Reject Rate',
            'vi': 'Tỷ lệ từ chối AQL khu vực'
        },
        'teamAreaAQLDetail': {
            'ko': '관리하는 팀/구역에서 3개월 연속 실패자가 없어야 합니다',
            'en': 'No 3-month consecutive failures in managed team/area',
            'vi': 'Không có thất bại 3 tháng liên tiếp trong nhóm/khu vực quản lý'
        },
        'areaRejectDetail': {
            'ko': '담당 구역의 AQL 리젝률이 3% 미만이어야 합니다',
            'en': 'Area AQL reject rate must be below 3%',
            'vi': 'Tỷ lệ từ chối AQL khu vực phải dưới 3%'
        }
    }

    # FAQ and help text
    translations['help'] = translations.get('help', {})
    translations['help']['messages'] = {
        'conditionNotMet': {
            'ko': '조건 미충족',
            'en': 'Condition Not Met',
            'vi': 'Không đạt điều kiện'
        },
        'allConditionsMet': {
            'ko': '모든 조건 충족',
            'en': 'All Conditions Met',
            'vi': 'Đạt tất cả điều kiện'
        },
        'conditionStatus': {
            'ko': '조건 충족 현황',
            'en': 'Condition Status',
            'vi': 'Trạng thái điều kiện'
        },
        'result': {
            'ko': '결과',
            'en': 'Result',
            'vi': 'Kết quả'
        },
        'responsibleArea': {
            'ko': '담당 구역',
            'en': 'Responsible Area',
            'vi': 'Khu vực phụ trách'
        }
    }

    # Save updated translations
    with open(translations_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print("✅ Translation file updated successfully")
    print(f"📁 Updated: {translations_path}")

    # Show summary of additions
    print("\n📋 Added translations for:")
    print("  - Area AQL modal (conditions 7 & 8)")
    print("  - 5PRS modals (pass rate & inspection qty)")
    print("  - Common table headers")
    print("  - Validation tab KPI cards")
    print("  - Condition descriptions")
    print("  - Help messages")

if __name__ == "__main__":
    update_translations()