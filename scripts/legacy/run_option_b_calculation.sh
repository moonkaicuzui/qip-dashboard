#!/bin/bash
# Run Option B calculation and generate dashboard

echo "="
echo "🚀 Running Option B Calculation Pipeline"
echo "="

# Step 1: Run incentive calculation for September 2025
echo "[1] Running incentive calculation..."
echo "4" | python src/step1_인센티브_계산_개선버전.py

# Check if calculation was successful
if [ $? -eq 0 ]; then
    echo "✅ Incentive calculation completed"
else
    echo "❌ Incentive calculation failed"
    exit 1
fi

# Step 2: Generate dashboard
echo "[2] Generating dashboard..."
python integrated_dashboard_final.py --month 9 --year 2025

if [ $? -eq 0 ]; then
    echo "✅ Dashboard generated successfully"
else
    echo "❌ Dashboard generation failed"
    exit 1
fi

# Step 3: Verify MODEL MASTER results
echo "[3] Verifying MODEL MASTER incentives..."
python verify_option_b_results.py

echo "="
echo "✅ Option B Pipeline Complete"
echo "="