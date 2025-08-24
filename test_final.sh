#!/bin/bash

echo "============================================================"
echo "최종 통합 테스트"
echo "============================================================"
echo ""

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 7월 파일 삭제
echo "1. 7월 파일 삭제 (테스트 준비)"
rm -f output_files/*july* 2>/dev/null
echo "   ✅ 완료"
echo ""

# 8월 계산 실행
echo "2. 8월 인센티브 계산 실행"
echo "   (7월 자동 계산 포함)"
echo "----------------------------------------"

python3 src/step1_인센티브_계산_개선버전.py --config config_files/config_august_2025.json

RESULT=$?

echo ""
echo "============================================================"
echo "테스트 결과:"
echo "============================================================"

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 성공: 8월 계산이 완료되었습니다.${NC}"
    
    # 7월 파일 확인
    if [ -f "output_files/output_QIP_incentive_july_2025_최종완성버전_v6.0_Complete.csv" ]; then
        echo -e "${GREEN}✅ 7월 파일이 자동으로 생성되었습니다.${NC}"
    else
        echo -e "${YELLOW}⚠️ 7월 CSV 파일이 생성되지 않았습니다.${NC}"
    fi
else
    echo -e "${RED}❌ 실패: 계산 중 오류가 발생했습니다.${NC}"
    echo "   종료 코드: $RESULT"
fi

echo "============================================================"