#!/usr/bin/env python3
"""
Generate Self-Contained HTML for All Available Dashboards
==========================================================
This script finds all dashboard HTML files and generates
self-contained versions for each one.

Used by GitHub Actions to keep SelfContained HTML in sync
with web dashboards on every 30-minute update.
"""

import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from create_self_contained_html import create_self_contained_html


def find_dashboard_files(docs_dir: Path) -> list:
    """Find all web dashboard HTML files (excluding SelfContained versions)."""
    pattern = re.compile(r'Incentive_Dashboard_(\d{4})_(\d{2})_Version_[\d.]+\.html$')

    dashboard_files = []
    for html_file in docs_dir.glob('*.html'):
        # Skip SelfContained versions
        if 'SelfContained' in html_file.name:
            continue

        match = pattern.match(html_file.name)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            dashboard_files.append({
                'path': html_file,
                'year': year,
                'month': month,
                'name': html_file.name
            })

    return sorted(dashboard_files, key=lambda x: (x['year'], x['month']))


def generate_selfcontained(dashboard_info: dict) -> bool:
    """Generate SelfContained HTML for a single dashboard."""
    input_path = dashboard_info['path']
    output_name = input_path.stem + '_SelfContained.html'
    output_path = input_path.parent / output_name

    try:
        print(f"\n{'='*60}")
        print(f"📦 Generating: {output_name}")
        print(f"{'='*60}")

        create_self_contained_html(str(input_path), str(output_path))
        return True
    except Exception as e:
        print(f"❌ Error generating {output_name}: {e}")
        return False


def main():
    """Main function to generate all SelfContained HTML files."""
    print("="*60)
    print("🔄 Generate All SelfContained HTML Files")
    print("="*60)

    # Find docs directory
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print(f"❌ Error: docs directory not found")
        return 1

    # Check if CDN libraries exist
    lib_dir = Path('static/cdn_libraries')
    required_libs = [
        'bootstrap.min.css',
        'bootstrap.bundle.min.js',
        'fontawesome.min.css',
        'chart.min.js',
        'd3.v7.min.js'
    ]

    missing_libs = []
    for lib in required_libs:
        if not (lib_dir / lib).exists():
            missing_libs.append(lib)

    if missing_libs:
        print(f"❌ Error: Missing CDN libraries: {missing_libs}")
        print(f"   Please ensure static/cdn_libraries/ contains all required files.")
        return 1

    print(f"✅ CDN libraries found: {len(required_libs)} files")

    # Find all dashboard files
    dashboards = find_dashboard_files(docs_dir)

    if not dashboards:
        print(f"⚠️ No dashboard HTML files found in {docs_dir}")
        return 0

    print(f"\n📋 Found {len(dashboards)} dashboard(s) to process:")
    for d in dashboards:
        print(f"   - {d['year']}/{d['month']:02d}: {d['name']}")

    # Generate SelfContained for each dashboard
    success_count = 0
    fail_count = 0

    for dashboard in dashboards:
        if generate_selfcontained(dashboard):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {fail_count}")
    print(f"   📁 Total: {success_count + fail_count}")

    if fail_count > 0:
        print(f"\n⚠️ Some SelfContained files failed to generate!")
        return 1

    print(f"\n✅ All SelfContained HTML files generated successfully!")
    return 0


if __name__ == '__main__':
    exit(main())
