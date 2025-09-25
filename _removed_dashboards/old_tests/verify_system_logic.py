"""
시스템의 실제 Total Working Days 계산 로직 검증
THỊ MINH PHƯỢNG 케이스 분석
"""

import pandas as pd

def calculate_system_working_days(start_date, end_date):
    """시스템이 사용하는 실제 근무가능일 계산 로직"""
    working_days_possible = 0
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 월-금 (0-4)
            working_days_possible += 1
        current_date += pd.Timedelta(days=1)
    
    return working_days_possible

def analyze_thi_minh_phuong():
    """THỊ MINH PHƯỢNG 케이스 분석"""
    print("=" * 60)
    print("시스템 로직을 사용한 THỊ MINH PHƯỢNG 분석")
    print("=" * 60)
    
    # 직원 데이터
    employee_id = "620080271"
    employee_name = "THỊ MINH PHƯỢNG"
    entrance_date = pd.to_datetime("2020-08-25")
    stop_date = pd.to_datetime("2025-08-15")
    
    # 2025년 8월 계산 기간
    calc_month_start = pd.Timestamp(2025, 8, 1)
    calc_month_end = pd.Timestamp(2025, 8, 31)
    
    # 실제 데이터
    actual_total_days = 11.0  # CSV에서 확인된 값
    actual_working_days = 12.0  # CSV에서 확인된 값
    
    print(f"\n📋 직원 정보:")
    print(f"  ID: {employee_id}")
    print(f"  이름: {employee_name}")
    print(f"  입사일: {entrance_date.date()}")
    print(f"  퇴사일: {stop_date.date()}")
    
    print(f"\n📅 2025년 8월 분석:")
    print(f"  계산 월: {calc_month_start.date()} ~ {calc_month_end.date()}")
    print(f"  실제 근무 기간: {calc_month_start.date()} ~ {stop_date.date()}")
    
    # 시스템 로직으로 근무가능일 계산
    system_calculated_days = calculate_system_working_days(calc_month_start, stop_date)
    
    print(f"\n💼 시스템 로직 계산 결과:")
    print(f"  시스템 계산 근무가능일: {system_calculated_days}일")
    print(f"  CSV의 Total Working Days: {actual_total_days}일")
    print(f"  CSV의 Actual Working Days: {actual_working_days}일")
    
    # 일별 상세 내역
    print(f"\n📆 일별 상세 내역 (8월 1일 ~ 15일):")
    current = calc_month_start
    working_count = 0
    weekend_count = 0
    
    while current <= stop_date:
        day_name = current.strftime("%A")
        day_name_kr = ["월", "화", "수", "목", "금", "토", "일"][current.weekday()]
        is_weekend = current.weekday() >= 5
        
        if is_weekend:
            weekend_count += 1
            status = "주말"
        else:
            working_count += 1
            status = "근무일"
        
        print(f"  {current.date()} ({day_name_kr}요일): {status}")
        current += pd.Timedelta(days=1)
    
    print(f"\n📊 계산 결과 요약:")
    print(f"  시스템 로직 근무가능일: {system_calculated_days}일")
    print(f"  - 평일: {working_count}일")
    print(f"  - 주말: {weekend_count}일")
    print(f"  CSV Total Working Days: {actual_total_days}일")
    print(f"  CSV Actual Working Days: {actual_working_days}일")
    
    print(f"\n🔍 결론:")
    if system_calculated_days == actual_total_days:
        print(f"  ✅ Total Working Days ({actual_total_days}일)는 시스템 로직과 일치합니다")
        print(f"  ❌ 하지만 Actual Working Days ({actual_working_days}일)가 Total을 초과합니다")
        print(f"     → 이것이 실제 데이터 오류입니다!")
    else:
        print(f"  ⚠️ Total Working Days 불일치:")
        print(f"     시스템 계산: {system_calculated_days}일")
        print(f"     CSV 기록: {actual_total_days}일")
        print(f"     차이: {abs(system_calculated_days - actual_total_days)}일")
    
    # 결근율 계산
    if actual_total_days > 0:
        absence_rate = ((actual_total_days - actual_working_days) / actual_total_days) * 100
        print(f"\n📈 결근율 계산:")
        print(f"  결근율 = (Total - Actual) / Total * 100")
        print(f"  결근율 = ({actual_total_days} - {actual_working_days}) / {actual_total_days} * 100")
        print(f"  결근율 = {absence_rate:.2f}%")
        
        if absence_rate < 0:
            print(f"  ⚠️ 음수 결근율은 Actual > Total을 의미합니다 (데이터 오류)")
    
    print("\n" + "=" * 60)
    print("분석 결과: CSV 데이터의 Total Working Days (11일)가 정확합니다.")
    print("문제는 Actual Working Days (12일)가 Total을 초과한다는 점입니다.")
    print("오류 감지 로직이 '15일'로 잘못 계산한 것이 문제입니다.")
    print("=" * 60)

if __name__ == "__main__":
    analyze_thi_minh_phuong()