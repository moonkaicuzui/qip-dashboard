#!/bin/bash
# cleanup_complete.sh - 전체 프로젝트 정리 스크립트 (Streamlit 포함)

echo "🗑️ 전체 프로젝트 정리를 시작합니다..."
echo ""

# 현재 상태 출력
echo "📊 정리 전 상태:"
du -sh . 2>/dev/null | awk '{print "   전체 크기: " $1}'
find . -type f | wc -l | awk '{print "   전체 파일: " $1 "개"}'
echo ""

# 백업 먼저 생성
echo "📦 현재 상태 백업 중..."
cd ..
tar -czf "dashboard_backup_$(date +%Y%m%d_%H%M%S).tar.gz" "Dashboard  Incentive Version 8_2_모바일에서도 볼수 있도록 테스트" 2>/dev/null
cd "Dashboard  Incentive Version 8_2_모바일에서도 볼수 있도록 테스트"
echo "   ✅ 백업 완료: ../dashboard_backup_*.tar.gz"
echo ""

# 1단계: 루트 백업 파일 삭제
echo "1️⃣  루트 백업 파일 삭제 중..."
rm -f integrated_dashboard_final.py.backup \
   integrated_dashboard_final.py.backup_20251003_130719 \
   integrated_dashboard_final_backup_20251105_153046.py \
   integrated_dashboard_final_fixed.py \
   integrated_dashboard_final_fixed_v2.py \
   integrated_dashboard_final_translation_fixed.py 2>/dev/null
echo "   ✅ 6개 백업 파일 삭제 (약 3.4MB)"

# 2단계: 테스트/디버깅 파일 삭제
echo "2️⃣  테스트/디버깅 파일 삭제 중..."
rm -f test_building_modal.js test_main_script.js test_interim_report.py \
   check_improvements.js check_js_syntax.js check_type_display.py \
   verify_building_modal.js verify_dynamic_text.js verify_final_modal.js \
   verify_language_consistency.py get_detailed_error.js 2>/dev/null
echo "   ✅ 11개 테스트 파일 삭제 (약 650KB)"

# 3단계: 수정 스크립트 삭제
echo "3️⃣  수정 스크립트 삭제 중..."
rm -f fix_language_translation.py fix_language_translation_v2.py \
   fix_type_table_auto_load.py fix_type_table_syntax.py 2>/dev/null
echo "   ✅ 4개 수정 스크립트 삭제 (약 26KB)"

# 4단계: 구버전 대시보드 삭제
echo "4️⃣  구버전 대시보드 삭제 중..."
rm -f docs/Incentive_Dashboard_2025_07_Version_8.02.html \
   docs/Incentive_Dashboard_2025_08_Version_8.02.html \
   docs/Incentive_Dashboard_2025_09_Version_8.02.html \
   docs/Incentive_Dashboard_2025_10_Version_8.02.html 2>/dev/null
echo "   ✅ 4개 구버전 대시보드 삭제 (약 17MB)"

# 5단계: 중복 설정 파일 삭제
echo "5️⃣  중복 설정 파일 삭제 중..."
rm -f config_november_2025.json config_october_2025.json config_september_2025.json 2>/dev/null
echo "   ✅ 3개 중복 설정 파일 삭제 (약 1.7KB)"

# 6단계: Streamlit/Flask 실험 폴더 삭제
echo "6️⃣  Streamlit/Flask 실험 폴더 삭제 중..."
rm -rf webapp/ 2>/dev/null
echo "   ✅ webapp/ 폴더 삭제 (약 144KB)"

# 7단계: 백업 폴더 삭제
echo "7️⃣  오래된 백업 폴더 삭제 중..."
rm -rf backup/ 2>/dev/null
echo "   ✅ backup/ 폴더 삭제 (약 4.7MB)"

# 8단계: 테스트 폴더들 삭제
echo "8️⃣  테스트 폴더들 삭제 중..."
rm -rf tests/ test_results/ error_review/ 2>/dev/null
echo "   ✅ tests/, test_results/, error_review/ 폴더 삭제 (약 76KB)"

# 9단계: 초기 설정 폴더 삭제
echo "9️⃣  초기 설정 폴더 삭제 중..."
rm -rf setup/ 2>/dev/null
echo "   ✅ setup/ 폴더 삭제 (약 8KB)"

# 10단계: 빈 폴더 삭제
echo "🔟 빈 폴더 삭제 중..."
rm -rf utilities/ screenshots/ 2>/dev/null
echo "   ✅ utilities/, screenshots/ 폴더 삭제"

# 11단계: 모바일 뷰어 실험 파일 삭제
echo "1️⃣1️⃣ 모바일 뷰어 실험 파일 삭제 중..."
rm -f mobile_viewer.py QIP_대시보드_바로가기.html 간단한_모바일_뷰어.py 2>/dev/null
echo "   ✅ 3개 모바일 뷰어 파일 삭제 (약 23KB)"

# 12단계: 한글 가이드 문서 아카이브
echo "1️⃣2️⃣ 한글 가이드 문서 아카이브 중..."
mkdir -p docs/archive 2>/dev/null
mv *가이드*.md docs/archive/ 2>/dev/null
mv *REPORT*.md dashboard_improvements.md docs/archive/ 2>/dev/null
echo "   ✅ 가이드 및 리포트 문서를 docs/archive/로 이동"

echo ""
echo "✅ 정리 완료!"
echo ""

# 정리 후 상태 출력
echo "📊 정리 후 상태:"
du -sh . 2>/dev/null | awk '{print "   전체 크기: " $1}'
find . -type f | wc -l | awk '{print "   전체 파일: " $1 "개"}'
echo ""

echo "💾 절약된 공간: 약 27MB"
echo "🗂️  삭제된 항목:"
echo "   - 루트 백업 파일 6개"
echo "   - 테스트/디버깅 파일 11개"
echo "   - 수정 스크립트 4개"
echo "   - 구버전 대시보드 4개"
echo "   - webapp/ 폴더 (Streamlit/Flask 실험)"
echo "   - backup/ 폴더"
echo "   - tests/, test_results/, error_review/ 폴더"
echo "   - setup/, utilities/, screenshots/ 폴더"
echo "   - 모바일 뷰어 파일 3개"
echo "   - 중복 설정 파일 3개"
echo ""
echo "📁 보존된 중요 폴더:"
echo "   - src/ (계산 엔진)"
echo "   - scripts/ (유틸리티)"
echo "   - config_files/ (설정)"
echo "   - input_files/ (입력 데이터)"
echo "   - output_files/ (출력 데이터)"
echo "   - docs/ (웹 호스팅)"
echo "   - dashboard_v2/ (모듈러 대시보드)"
echo ""
echo "🎉 프로젝트가 깔끔하게 정리되었습니다!"
