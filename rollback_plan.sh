#!/bin/bash

# Version 6 → Version 5 Rollback Script
# 비상 시 Version 5로 즉시 복구

echo "🔄 Version 6 → Version 5 롤백 시작"
echo "=================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 현재 날짜/시간
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 파일 경로
V5_FILE="output_files/Incentive_Dashboard_2025_09_Version_5.html"
V6_FILE="output_files/Incentive_Dashboard_2025_09_Version_6.html"
CURRENT_FILE="output_files/Incentive_Dashboard_Current.html"
BACKUP_DIR="output_files/backup"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}1. 현재 상태 확인${NC}"
if [ -f "$V6_FILE" ]; then
    echo "   ✅ Version 6 파일 존재"
    V6_SIZE=$(ls -lh "$V6_FILE" | awk '{print $5}')
    echo "   📊 Version 6 크기: $V6_SIZE"
else
    echo -e "   ${RED}❌ Version 6 파일 없음${NC}"
fi

if [ -f "$V5_FILE" ]; then
    echo "   ✅ Version 5 파일 존재"
    V5_SIZE=$(ls -lh "$V5_FILE" | awk '{print $5}')
    echo "   📊 Version 5 크기: $V5_SIZE"
else
    echo -e "   ${RED}❌ Version 5 파일 없음 - 롤백 불가!${NC}"
    exit 1
fi

echo -e "\n${YELLOW}2. Version 6 백업${NC}"
if [ -f "$V6_FILE" ]; then
    cp "$V6_FILE" "$BACKUP_DIR/Version_6_rollback_$TIMESTAMP.html"
    echo "   ✅ Version 6 백업 완료: $BACKUP_DIR/Version_6_rollback_$TIMESTAMP.html"
fi

echo -e "\n${YELLOW}3. Version 5로 롤백${NC}"
echo -n "   정말로 Version 5로 롤백하시겠습니까? (y/N): "
read -r CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    # Version 5를 현재 버전으로 복사
    cp "$V5_FILE" "$CURRENT_FILE"
    echo -e "   ${GREEN}✅ Version 5로 롤백 완료${NC}"
    
    # 심볼릭 링크 업데이트 (선택사항)
    if [ -L "output_files/Incentive_Dashboard_Latest.html" ]; then
        rm "output_files/Incentive_Dashboard_Latest.html"
    fi
    ln -s "$(basename "$V5_FILE")" "output_files/Incentive_Dashboard_Latest.html"
    
    echo -e "\n${GREEN}🎉 롤백 완료!${NC}"
    echo "=================================="
    echo "현재 사용 중인 버전: Version 5"
    echo "백업된 Version 6: $BACKUP_DIR/Version_6_rollback_$TIMESTAMP.html"
    
    # 롤백 로그 기록
    echo "[$(date)] Rollback from Version 6 to Version 5" >> rollback.log
    
    # 브라우저에서 확인 옵션
    echo -e "\n브라우저에서 확인하시겠습니까? (y/N): "
    read -r OPEN_BROWSER
    if [ "$OPEN_BROWSER" = "y" ] || [ "$OPEN_BROWSER" = "Y" ]; then
        open "$CURRENT_FILE"
    fi
else
    echo -e "   ${YELLOW}⚠️ 롤백 취소됨${NC}"
fi

echo -e "\n📝 롤백 이력:"
tail -5 rollback.log 2>/dev/null || echo "   (이력 없음)"
