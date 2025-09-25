#!/bin/bash
# Run integrated dashboard with Excel export functionality

echo "================================================"
echo "QIP 인센티브 대시보드 생성 (Excel Export 포함)"
echo "================================================"
echo ""

# Get month and year from arguments or use defaults
MONTH=${1:-august}
YEAR=${2:-2025}

echo "📅 기간: $YEAR년 $MONTH"
echo ""

# Run the integrated dashboard with Excel export
python integrated_dashboard_with_excel.py --month "$MONTH" --year "$YEAR"

echo ""
echo "================================================"
echo "✅ 완료! 생성된 파일:"
echo "  📊 Dashboard: output_files/dashboard_${YEAR}_${MONTH}.html"
echo "  📁 Excel: output_files/Incentive_Report_${YEAR}_*.xlsx"
echo "================================================"