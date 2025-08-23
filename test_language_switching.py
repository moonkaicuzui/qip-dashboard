#!/usr/bin/env python3
"""
Language Switching Test Checklist for QIP Dashboard
Author: Claude
Date: 2025-01-21
"""

print("""
================================================
QIP 대시보드 언어 전환 테스트 체크리스트
================================================

📋 테스트 준비:
1. dashboard_version4.html 파일을 브라우저에서 열기
2. 개발자 도구 콘솔 열기 (F12)

================================================
✅ MAIN UI 테스트
================================================

[ ] 1. 언어 선택 드롭다운
    - 한국어 선택 → 모든 메인 UI가 한국어로 변경
    - English 선택 → 모든 메인 UI가 영어로 변경  
    - Tiếng Việt 선택 → 모든 메인 UI가 베트남어로 변경

[ ] 2. 요약 탭 (Summary Tab)
    - Type별 현황 테이블 헤더 번역 확인
    - 단위 표시 확인 (명 / people / người)
    - 상세 보기 버튼 텍스트 확인

[ ] 3. 직급별 상세 탭 (Position Detail Tab)
    - 테이블 헤더 번역 확인
    - 각 Type별 테이블 타이틀 확인
    - 데이터가 올바르게 표시되는지 확인 (월 변수 치환)

[ ] 4. 개인별 상세 탭 (Individual Detail Tab)
    - 필터 드롭다운 "모든 직급" 텍스트 확인
    - "필터 초기화" 버튼 텍스트 확인
    - 테이블 헤더 번역 확인

================================================
✅ POSITION DETAIL POPUP 테스트
================================================

[ ] 5. 직급별 상세 팝업 창 열기
    - 요약 탭에서 "상세 보기" 버튼 클릭

[ ] 6. 팝업 창 차트 번역 확인
    - 도넛 차트 레전드: "지급" / "Paid" / "Được trả"
    - 도넛 차트 중앙 텍스트: "지급률" / "Payment Rate" / "Tỷ lệ thanh toán"
    - 막대 차트 라벨: "충족률 (%)" / "Fulfillment Rate (%)" / "Tỉ lệ hoàn thành (%)"

[ ] 7. 팝업 창 조건 테이블 확인
    - 조건 그룹 타이틀:
      * "출근 조건 (3가지)" / "Attendance Conditions (3 items)" / "Điều kiện đi làm (3 mục)"
      * "AQL 조건 (4가지)" / "AQL Conditions (4 items)" / "Điều kiện AQL (4 mục)"
      * "5PRS 조건 (2가지)" / "5PRS Conditions (2 items)" / "Điều kiện 5PRS (2 mục)"
    - 테이블 헤더:
      * "조건" / "Condition" / "Điều kiện"
      * "평가 대상" / "Evaluation Target" / "Đối tượng đánh giá"
      * "충족" / "Fulfilled" / "Đạt"
      * "미충족" / "Not Fulfilled" / "Không đạt"
      * "충족률" / "Fulfillment Rate" / "Tỉ lệ hoàn thành"

[ ] 8. 팝업 창 직원별 상세 테이블 확인
    - 섹션 타이틀: "직원별 상세 현황" / "Employee Detail Status" / "Tình trạng chi tiết nhân viên"
    - 필터 버튼:
      * "지급자만" / "Paid Only" / "Chỉ người được trả"
      * "미지급자만" / "Unpaid Only" / "Chỉ người chưa được trả"
      * "전체" / "View All" / "Xem tất cả"
    - 테이블 헤더 번역 확인

[ ] 9. 팝업 창 통계 섹션 확인
    - "인원 현황" / "Employee Status" / "Tình trạng nhân viên"
    - "지급률" / "Payment Rate" / "Tỷ lệ thanh toán"
    - "평균 충족률" / "Average Fulfillment Rate" / "Tỷ lệ hoàn thành trung bình"

================================================
✅ EMPLOYEE DETAIL POPUP 테스트
================================================

[ ] 10. 개인별 상세 팝업 창 열기
    - 직원 행 클릭

[ ] 11. 팝업 창 기본 정보 섹션 확인
    - 테이블 라벨 번역 확인
    - 계산 기준 값 번역 확인

[ ] 12. 팝업 창 조건 체크 섹션 확인
    - 조건명 번역 확인
    - Pass/Fail 상태 번역 확인

================================================
📊 테스트 결과 요약
================================================

총 테스트 항목: 12개
통과: ___ 개
실패: ___ 개
성공률: ____%

================================================
🐛 발견된 이슈:
================================================

1. _________________________________
2. _________________________________
3. _________________________________

================================================
✨ 개선 확인 사항:
================================================

✅ 완료된 개선 사항:
- Position Detail 팝업 차트 레이블 동적 번역
- Position Detail 팝업 도넛 차트 중앙 텍스트 번역
- Position Detail 팝업 차트 레전드 번역
- Position Detail 팝업 조건 테이블 헤더 번역
- Position Detail 팝업 조건 그룹 타이틀 번역
- Position Detail 탭 데이터 표시 문제 해결 ({month} 변수 치환)
- Individual Detail 탭 필터 버튼 번역
- Individual Detail 탭 테이블 헤더 번역

✅ 추가 개선 사항:
- 베트남어 번역 객체에 누락된 키 추가
- 영어 번역 객체에 누락된 키 추가
- 모든 하드코딩된 한국어 텍스트를 동적 변수로 변경

================================================
""")

# 브라우저에서 대시보드 열기
import webbrowser
import os

dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트8_구글 연동 완료_by Macbook air copy/output_files/dashboard_version4.html"
if os.path.exists(dashboard_path):
    print(f"🌐 브라우저에서 대시보드 열기: {dashboard_path}")
    webbrowser.open(f"file://{dashboard_path}")
else:
    print("⚠️ dashboard_version4.html 파일을 찾을 수 없습니다.")