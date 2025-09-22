#!/usr/bin/env python3
"""
Add missing translations for org chart modals and validation tab
"""

import json
import os

def add_missing_translations():
    """Add all missing translations identified in the checklist"""

    # Load existing translations
    translations_path = 'config_files/dashboard_translations.json'
    with open(translations_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # 1. Fix validation tab name
    if 'tabs' in translations and 'validation' in translations['tabs']:
        translations['tabs']['validation'] = {
            'ko': '요약 및 시스템 검증',
            'en': 'Summary & System Validation',
            'vi': 'Tóm tắt & Xác thực hệ thống'
        }

    # 2. Individual details modal - performance status
    if 'individualDetails' not in translations:
        translations['individualDetails'] = {}

    translations['individualDetails']['conditionStatus'] = {
        'pass': {
            'ko': '통과',
            'en': 'Pass',
            'vi': 'Đạt'
        },
        'fail': {
            'ko': '실패',
            'en': 'Fail',
            'vi': 'Thất bại'
        }
    }

    # 3. Org Chart translations
    if 'orgChart' not in translations:
        translations['orgChart'] = {}

    # Main org chart texts
    translations['orgChart']['excludedPositionsNote'] = {
        'ko': '참고: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER 직급은 조직도에서 제외되었습니다.',
        'en': 'Note: AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER positions are excluded from the organization chart.',
        'vi': 'Lưu ý: Các vị trí AQL INSPECTOR, AUDIT & TRAINING TEAM, MODEL MASTER không được bao gồm trong sơ đồ tổ chức.'
    }

    translations['orgChart']['entireOrganization'] = {
        'ko': '전체 조직',
        'en': 'Entire Organization',
        'vi': 'Toàn bộ tổ chức'
    }

    translations['orgChart']['type1ManagerStructure'] = {
        'ko': 'TYPE-1 관리자 인센티브 구조',
        'en': 'TYPE-1 Manager Incentive Structure',
        'vi': 'Cấu trúc khuyến khích quản lý TYPE-1'
    }

    # Org Chart Modal translations
    if 'orgChartModal' not in translations:
        translations['orgChartModal'] = {}

    translations['orgChartModal']['position'] = {
        'ko': '직급',
        'en': 'Position',
        'vi': 'Chức vụ'
    }

    translations['orgChartModal']['calculationDetails'] = {
        'ko': '계산 과정 상세',
        'en': 'Calculation Details',
        'vi': 'Chi tiết tính toán'
    }

    translations['orgChartModal']['teamLineLeaderCount'] = {
        'ko': '팀 내 LINE LEADER 수',
        'en': 'Team LINE LEADER Count',
        'vi': 'Số LINE LEADER trong nhóm'
    }

    translations['orgChartModal']['lineLeadersReceiving'] = {
        'ko': '인센티브 받은 LINE LEADER',
        'en': 'LINE LEADERs Receiving Incentive',
        'vi': 'LINE LEADER nhận khuyến khích'
    }

    translations['orgChartModal']['lineLeaderAverage'] = {
        'ko': 'LINE LEADER 평균 인센티브',
        'en': 'LINE LEADER Average Incentive',
        'vi': 'Khuyến khích trung bình LINE LEADER'
    }

    translations['orgChartModal']['calculationFormula'] = {
        'ko': '계산식',
        'en': 'Calculation Formula',
        'vi': 'Công thức tính'
    }

    translations['orgChartModal']['teamLineLeaderDetails'] = {
        'ko': '팀 내 LINE LEADER 인센티브 내역 (평균 계산 대상)',
        'en': 'Team LINE LEADER Incentive Details (Average Calculation Target)',
        'vi': 'Chi tiết khuyến khích LINE LEADER trong nhóm (Mục tiêu tính trung bình)'
    }

    translations['orgChartModal']['assemblyInspectorDetails'] = {
        'ko': 'ASSEMBLY INSPECTOR 인센티브 내역 (합계 계산 대상)',
        'en': 'ASSEMBLY INSPECTOR Incentive Details (Total Calculation Target)',
        'vi': 'Chi tiết khuyến khích ASSEMBLY INSPECTOR (Mục tiêu tính tổng)'
    }

    translations['orgChartModal']['name'] = {
        'ko': '이름',
        'en': 'Name',
        'vi': 'Tên'
    }

    translations['orgChartModal']['incentive'] = {
        'ko': '인센티브',
        'en': 'Incentive',
        'vi': 'Khuyến khích'
    }

    translations['orgChartModal']['includeInAverage'] = {
        'ko': '평균 계산 포함',
        'en': 'Include in Average',
        'vi': 'Bao gồm trong trung bình'
    }

    translations['orgChartModal']['receivingStatus'] = {
        'ko': '수령 여부',
        'en': 'Receiving Status',
        'vi': 'Trạng thái nhận'
    }

    translations['orgChartModal']['total'] = {
        'ko': '합계',
        'en': 'Total',
        'vi': 'Tổng'
    }

    translations['orgChartModal']['average'] = {
        'ko': '평균',
        'en': 'Average',
        'vi': 'Trung bình'
    }

    translations['orgChartModal']['averageRecipients'] = {
        'ko': '(수령자 {recipients}명 / 전체 {total}명)',
        'en': '({recipients} recipients / {total} total)',
        'vi': '({recipients} người nhận / {total} tổng)'
    }

    translations['orgChartModal']['people'] = {
        'ko': '명',
        'en': 'people',
        'vi': 'người'
    }

    # Non-Payment Reason translations
    translations['orgChartModal']['nonPaymentReason'] = {
        'ko': 'Non-Payment Reason',
        'en': 'Non-Payment Reason',
        'vi': 'Lý do không thanh toán'
    }

    translations['orgChartModal']['nonPaymentReasons'] = {
        'actualWorkingDays0': {
            'ko': '실제 근무일 0일 (출근 조건 1번 미충족)',
            'en': '0 actual working days (Attendance condition 1 not met)',
            'vi': '0 ngày làm việc thực tế (Điều kiện chấm công 1 không đạt)'
        },
        'unauthorizedAbsence': {
            'ko': '무단결근 2일 초과 (출근 조건 2번 미충족)',
            'en': 'Unauthorized absence exceeds 2 days (Attendance condition 2 not met)',
            'vi': 'Vắng không phép quá 2 ngày (Điều kiện chấm công 2 không đạt)'
        },
        'absenceRate12': {
            'ko': '결근율 12% 초과 (출근 조건 3번 미충족)',
            'en': 'Absence rate exceeds 12% (Attendance condition 3 not met)',
            'vi': 'Tỷ lệ vắng vượt quá 12% (Điều kiện chấm công 3 không đạt)'
        },
        'minWorkingDays': {
            'ko': '최소 근무일 미달 (출근 조건 4번 미충족)',
            'en': 'Below minimum working days (Attendance condition 4 not met)',
            'vi': 'Dưới ngày làm việc tối thiểu (Điều kiện chấm công 4 không đạt)'
        },
        'teamAreaAQL': {
            'ko': '팀/구역 AQL 실패 (AQL 조건 7번 미충족)',
            'en': 'Team/Area AQL failure (AQL condition 7 not met)',
            'vi': 'Thất bại AQL nhóm/khu vực (Điều kiện AQL 7 không đạt)'
        },
        'areaRejectRate': {
            'ko': '담당구역 리젝률 3% 초과 (AQL 조건 8번 미충족)',
            'en': 'Area reject rate exceeds 3% (AQL condition 8 not met)',
            'vi': 'Tỷ lệ từ chối khu vực vượt quá 3% (Điều kiện AQL 8 không đạt)'
        },
        'fprsPassRate': {
            'ko': '5PRS 검증 부족 또는 합격률 95% 미달 (5PRS 조건 1번 미충족)',
            'en': 'Insufficient 5PRS verification or pass rate below 95% (5PRS condition 1 not met)',
            'vi': 'Xác minh 5PRS không đủ hoặc tỷ lệ đạt dưới 95% (Điều kiện 5PRS 1 không đạt)'
        },
        'fprsZeroQty': {
            'ko': '5PRS 총 검증 수량 0 (5PRS 조건 2번 미충족)',
            'en': '5PRS total verification quantity 0 (5PRS condition 2 not met)',
            'vi': 'Tổng số lượng xác minh 5PRS là 0 (Điều kiện 5PRS 2 không đạt)'
        }
    }

    # Save updated translations
    with open(translations_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print("✅ Translation file updated successfully")
    print(f"📁 Updated: {translations_path}")

    # Show summary of additions
    print("\n📋 Added translations for:")
    print("  - Validation tab name")
    print("  - Individual details modal (pass/fail status)")
    print("  - Org chart main texts (3 items)")
    print("  - Org chart modal labels (13 items)")
    print("  - Non-payment reasons (8 items)")
    print("  - Total: 27+ translation entries added")

if __name__ == "__main__":
    add_missing_translations()