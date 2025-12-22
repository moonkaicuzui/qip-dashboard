#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Comparison Report Generator
====================================
@FinanceAnalyst & @DataVisualization 협업 개발

월별 인센티브 비교 리포트 생성:
- 전월 대비 변화
- 트렌드 분석
- 직급별/빌딩별 비교
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class MonthlyComparisonReport:
    """월별 비교 리포트 생성기"""

    def __init__(self, output_dir: str = "output_files"):
        self.output_dir = Path(output_dir)
        self.months_order = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]

    def load_month_data(self, month: str, year: int) -> Optional[pd.DataFrame]:
        """월별 데이터 로드"""
        patterns = [
            f"output_QIP_incentive_{month}_{year}_Complete_V9.0_Complete.csv",
            f"output_QIP_incentive_{month}_{year}_Complete_V*.csv",
        ]

        for pattern in patterns:
            files = list(self.output_dir.glob(pattern))
            if files:
                return pd.read_csv(files[0])
        return None

    def get_available_months(self, year: int) -> List[str]:
        """사용 가능한 월 목록"""
        available = []
        for month in self.months_order:
            if self.load_month_data(month, year) is not None:
                available.append(month)
        return available

    def compare_two_months(
        self,
        month1: str,
        month2: str,
        year: int
    ) -> Dict:
        """두 달 비교"""
        df1 = self.load_month_data(month1, year)
        df2 = self.load_month_data(month2, year)

        if df1 is None or df2 is None:
            return {"error": "Data not available for comparison"}

        # 인센티브 컬럼 찾기
        incentive_col1 = f"{month1.capitalize()}_Incentive"
        incentive_col2 = f"{month2.capitalize()}_Incentive"

        # 실제 컬럼명 검색
        for col in df1.columns:
            if 'incentive' in col.lower() and month1.lower() in col.lower():
                incentive_col1 = col
                break
            if 'final' in col.lower() and 'incentive' in col.lower():
                incentive_col1 = col
                break

        for col in df2.columns:
            if 'incentive' in col.lower() and month2.lower() in col.lower():
                incentive_col2 = col
                break
            if 'final' in col.lower() and 'incentive' in col.lower():
                incentive_col2 = col
                break

        comparison = {
            "period": f"{month1} vs {month2} {year}",
            "month1": {
                "name": month1,
                "total_employees": len(df1),
                "total_incentive": df1[incentive_col1].sum() if incentive_col1 in df1.columns else 0,
                "recipients": (df1[incentive_col1] > 0).sum() if incentive_col1 in df1.columns else 0,
            },
            "month2": {
                "name": month2,
                "total_employees": len(df2),
                "total_incentive": df2[incentive_col2].sum() if incentive_col2 in df2.columns else 0,
                "recipients": (df2[incentive_col2] > 0).sum() if incentive_col2 in df2.columns else 0,
            }
        }

        # 변화율 계산
        if comparison["month1"]["total_incentive"] > 0:
            change_pct = (
                (comparison["month2"]["total_incentive"] - comparison["month1"]["total_incentive"])
                / comparison["month1"]["total_incentive"] * 100
            )
            comparison["change"] = {
                "total_incentive_change": comparison["month2"]["total_incentive"] - comparison["month1"]["total_incentive"],
                "total_incentive_change_pct": round(change_pct, 2),
                "recipients_change": comparison["month2"]["recipients"] - comparison["month1"]["recipients"],
            }
        else:
            comparison["change"] = {
                "total_incentive_change": comparison["month2"]["total_incentive"],
                "total_incentive_change_pct": 100 if comparison["month2"]["total_incentive"] > 0 else 0,
                "recipients_change": comparison["month2"]["recipients"],
            }

        return comparison

    def generate_trend_report(self, year: int) -> Dict:
        """연간 트렌드 리포트"""
        months = self.get_available_months(year)
        if len(months) < 2:
            return {"error": "Insufficient data for trend analysis"}

        trend_data = []
        for month in months:
            df = self.load_month_data(month, year)
            if df is not None:
                # 인센티브 컬럼 찾기
                incentive_col = None
                for col in df.columns:
                    if 'final' in col.lower() and 'incentive' in col.lower():
                        incentive_col = col
                        break

                if incentive_col:
                    trend_data.append({
                        "month": month,
                        "total_employees": len(df),
                        "total_incentive": float(df[incentive_col].sum()),
                        "recipients": int((df[incentive_col] > 0).sum()),
                        "avg_incentive": float(df[df[incentive_col] > 0][incentive_col].mean()) if (df[incentive_col] > 0).any() else 0,
                    })

        # 트렌드 분석
        if len(trend_data) >= 2:
            first = trend_data[0]
            last = trend_data[-1]
            overall_change = {
                "period": f"{first['month']} to {last['month']}",
                "incentive_growth": last["total_incentive"] - first["total_incentive"],
                "recipients_growth": last["recipients"] - first["recipients"],
            }
        else:
            overall_change = {}

        return {
            "year": year,
            "available_months": months,
            "monthly_data": trend_data,
            "overall_change": overall_change,
            "generated_at": datetime.now().isoformat()
        }

    def generate_building_comparison(self, month: str, year: int) -> Dict:
        """빌딩별 비교 리포트"""
        df = self.load_month_data(month, year)
        if df is None:
            return {"error": "Data not available"}

        building_col = 'BUILDING' if 'BUILDING' in df.columns else None
        if building_col is None:
            for col in df.columns:
                if 'building' in col.lower():
                    building_col = col
                    break

        if building_col is None:
            return {"error": "Building column not found"}

        # 인센티브 컬럼 찾기
        incentive_col = None
        for col in df.columns:
            if 'final' in col.lower() and 'incentive' in col.lower():
                incentive_col = col
                break

        if incentive_col is None:
            return {"error": "Incentive column not found"}

        buildings = df[building_col].dropna().unique()
        building_stats = []

        for building in buildings:
            building_df = df[df[building_col] == building]
            building_stats.append({
                "building": building,
                "total_employees": len(building_df),
                "total_incentive": float(building_df[incentive_col].sum()),
                "recipients": int((building_df[incentive_col] > 0).sum()),
                "avg_incentive": float(building_df[building_df[incentive_col] > 0][incentive_col].mean()) if (building_df[incentive_col] > 0).any() else 0,
                "recipient_rate": round((building_df[incentive_col] > 0).sum() / len(building_df) * 100, 1) if len(building_df) > 0 else 0,
            })

        # 정렬 (인센티브 총액 기준)
        building_stats.sort(key=lambda x: x["total_incentive"], reverse=True)

        return {
            "month": month,
            "year": year,
            "building_count": len(buildings),
            "buildings": building_stats,
            "generated_at": datetime.now().isoformat()
        }

    def export_report(self, report: Dict, filename: str):
        """리포트 JSON 내보내기"""
        report_path = self.output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        return report_path


if __name__ == '__main__':
    print("=" * 60)
    print("📊 Monthly Comparison Report Generator")
    print("=" * 60)

    generator = MonthlyComparisonReport()

    # 사용 가능한 월 확인
    available = generator.get_available_months(2025)
    print(f"\n📅 Available months for 2025: {available}")

    if len(available) >= 2:
        # 최근 두 달 비교
        month1, month2 = available[-2], available[-1]
        comparison = generator.compare_two_months(month1, month2, 2025)
        print(f"\n📈 Comparison: {comparison.get('period', 'N/A')}")
        if 'change' in comparison:
            print(f"   Total incentive change: {comparison['change']['total_incentive_change']:,.0f} VND")
            print(f"   Change rate: {comparison['change']['total_incentive_change_pct']}%")

    # 트렌드 리포트
    if available:
        trend = generator.generate_trend_report(2025)
        print(f"\n📊 Trend report generated for {len(trend.get('monthly_data', []))} months")

    print("\n✅ Report Generator Test Complete!")
