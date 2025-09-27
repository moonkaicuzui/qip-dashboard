#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard V2 - Main Entry Point
Generates the incentive dashboard using the modular architecture
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from dashboard_v2.modules.data_processor import DataProcessor
from dashboard_v2.modules.template_renderer import TemplateRenderer
from dashboard_v2.modules.complete_renderer import CompleteRenderer


def generate_dashboard(month, year, output_path=None):
    """
    Generate the incentive dashboard

    Args:
        month: Month name (e.g., 'september')
        year: Year (e.g., 2025)
        output_path: Optional custom output path

    Returns:
        Path to the generated dashboard file
    """
    print(f"\n{'='*60}")
    print(f"  Dashboard V2 Generator")
    print(f"  Month: {month.capitalize()} {year}")
    print(f"{'='*60}\n")

    try:
        # Initialize data processor
        print("📊 Initializing data processor...")
        processor = DataProcessor(month, year)

        # Load configurations
        print("⚙️ Loading configurations...")
        processor.load_configurations()
        print("  ✅ Configurations loaded successfully")

        # Load and process data
        print("\n📁 Loading data...")
        processor.load_data()
        print(f"  ✅ Loaded {len(processor.df)} employees")

        # Export data for rendering
        print("\n🔄 Processing data for dashboard...")
        data = processor.export_to_json()
        print(f"  ✅ Processed data for {len(data['employees'])} employees")

        # Display statistics
        print("\n📈 Statistics:")
        print(f"  • Total Employees: {data['stats']['totalEmployees']}")
        print(f"  • Paid Employees: {data['stats']['paidEmployees']}")
        print(f"  • Payment Rate: {data['stats']['paymentRate']:.1f}%")
        print(f"  • Total Amount: {data['stats']['totalAmount']:,.0f} VND")

        # Use CompleteRenderer instead of TemplateRenderer for Version 6
        print("\n🎨 Using CompleteRenderer for Version 6...")
        renderer = CompleteRenderer()

        # Determine output path
        if not output_path:
            month_num = str(processor._get_month_number(month)).zfill(2)
            output_path = f"output_files/Incentive_Dashboard_{year}_{month_num}_Version_6.html"

        # Render dashboard using CompleteRenderer
        print(f"\n📝 Rendering dashboard with CompleteRenderer...")
        renderer.save_dashboard(month, year, output_path)

        # Report file size
        file_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n✅ Dashboard generated successfully!")
        print(f"  📁 File: {output_path}")
        print(f"  📊 Size: {file_size:.2f} MB")

        return output_path

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Make sure you've run the incentive calculation first:")
        print(f"  python src/step1_인센티브_계산_개선버전.py --config config_files/config_{month}_{year}.json")
        return None

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point with CLI support"""
    parser = argparse.ArgumentParser(
        description='Generate Incentive Dashboard V2'
    )
    parser.add_argument(
        '--month',
        type=str,
        default='september',
        help='Month name (e.g., september)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2025,
        help='Year (e.g., 2025)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Custom output path for the dashboard'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open the dashboard in browser after generation'
    )

    args = parser.parse_args()

    # Generate dashboard
    output_path = generate_dashboard(args.month, args.year, args.output)

    if output_path and args.open:
        import webbrowser
        import os
        file_url = f"file://{os.path.abspath(output_path)}"
        print(f"\n🌐 Opening dashboard in browser...")
        webbrowser.open(file_url)

    return 0 if output_path else 1


if __name__ == "__main__":
    exit(main())