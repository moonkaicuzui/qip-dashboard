#!/usr/bin/env python3
"""
Comprehensive test to verify ASSEMBLY team count consistency across all dashboard components.
This ensures the fix for position mapping conflicts is working correctly.
"""

import json
import re
from pathlib import Path
import sys

def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {filepath}: {e}")
        return None

def extract_assembly_counts_from_html(html_file):
    """Extract all ASSEMBLY team counts from the HTML dashboard."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assembly_counts = {}
        
        # Extract from JavaScript data structures
        # 1. teamStats data
        team_stats_match = re.search(r'const teamStats = ({.*?});', content, re.DOTALL)
        if team_stats_match:
            try:
                # Clean JavaScript object to make it JSON-compatible
                js_obj = team_stats_match.group(1)
                js_obj = re.sub(r'(\w+):', r'"\1":', js_obj)  # Add quotes to keys
                js_obj = js_obj.replace("'", '"')  # Single to double quotes
                team_stats = json.loads(js_obj)
                
                if 'ASSEMBLY' in team_stats:
                    assembly_counts['teamStats'] = team_stats['ASSEMBLY'].get('total', 'N/A')
            except:
                pass
        
        # 2. monthlyTrendData
        monthly_match = re.search(r"monthlyTrendData:\s*\[([^\]]+)\]", content, re.DOTALL)
        if monthly_match:
            # Look for ASSEMBLY in the data array
            assembly_match = re.search(r"'ASSEMBLY',\s*(\d+)", monthly_match.group(1))
            if assembly_match:
                assembly_counts['monthlyTrend'] = int(assembly_match.group(1))
        
        # 3. weeklyTrendData - Week 4
        weekly_match = re.search(r"weeklyTrendData:\s*{[^}]*Week4:\s*\[([^\]]+)\]", content, re.DOTALL)
        if weekly_match:
            assembly_match = re.search(r"'ASSEMBLY',\s*(\d+)", weekly_match.group(1))
            if assembly_match:
                assembly_counts['weeklyTrendWeek4'] = int(assembly_match.group(1))
        
        # 4. Role distribution data in donut chart
        role_data_match = re.search(r"const roleData = ({.*?});", content, re.DOTALL)
        if role_data_match:
            try:
                js_obj = role_data_match.group(1)
                # Extract ASSEMBLY role counts
                assembly_role_match = re.search(r"ASSEMBLY:\s*{([^}]+)}", js_obj)
                if assembly_role_match:
                    role_text = assembly_role_match.group(1)
                    # Sum up all role counts
                    role_counts = re.findall(r":\s*(\d+)", role_text)
                    if role_counts:
                        total = sum(int(count) for count in role_counts)
                        assembly_counts['roleDistributionSum'] = total
            except:
                pass
        
        # 5. Table footer total
        table_total_match = re.search(r"<tr[^>]*>.*?<td[^>]*>Total</td>.*?<td[^>]*>(\d+)</td>", content, re.DOTALL)
        if table_total_match:
            # Need to find ASSEMBLY table specifically
            assembly_table_match = re.search(
                r"ASSEMBLY.*?<tbody[^>]*>(.*?)</tbody>.*?<tr[^>]*>.*?Total.*?<td[^>]*>(\d+)</td>",
                content, re.DOTALL
            )
            if assembly_table_match:
                assembly_counts['tableTotal'] = int(assembly_table_match.group(2))
        
        # 6. Multi-level donut comparison text
        comparison_match = re.search(r"7월:\s*(\d+)명\s*→\s*8월:\s*(\d+)명", content)
        if comparison_match:
            assembly_counts['donutComparison'] = {
                'july': int(comparison_match.group(1)),
                'august': int(comparison_match.group(2))
            }
        
        return assembly_counts
        
    except FileNotFoundError:
        print(f"❌ HTML file not found: {html_file}")
        return {}
    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return {}

def main():
    """Main verification function."""
    print("=" * 70)
    print("ASSEMBLY Team Count Consistency Verification")
    print("=" * 70)
    
    # Expected correct count after fix
    EXPECTED_COUNT = 109
    
    # 1. Check metadata JSON
    print("\n📊 Checking HR Metadata JSON...")
    metadata_file = 'output_files/hr_metadata_2025.json'
    metadata = load_json_file(metadata_file)
    
    metadata_count = None
    if metadata:
        current_month = metadata.get('current_month', {})
        assembly_data = current_month.get('by_team', {}).get('ASSEMBLY', {})
        metadata_count = assembly_data.get('total', 'N/A')
        print(f"  Metadata JSON count: {metadata_count}")
        
        # Also check team_stats
        team_stats = metadata.get('team_stats', {}).get('2025_08', {}).get('ASSEMBLY', {})
        team_stats_count = team_stats.get('total', 'N/A')
        print(f"  Team stats count: {team_stats_count}")
    
    # 2. Check HTML dashboard
    print("\n🌐 Checking HTML Dashboard...")
    html_file = 'output_files/management_dashboard_2025_08.html'
    html_counts = extract_assembly_counts_from_html(html_file)
    
    if html_counts:
        for component, count in html_counts.items():
            print(f"  {component}: {count}")
    
    # 3. Verify consistency
    print("\n✅ Verification Results:")
    print("-" * 50)
    
    all_counts = []
    issues = []
    
    # Collect all counts
    if metadata_count and metadata_count != 'N/A':
        all_counts.append(('Metadata JSON', metadata_count))
    if team_stats_count and team_stats_count != 'N/A':
        all_counts.append(('Team Stats JSON', team_stats_count))
    
    for component, count in html_counts.items():
        if isinstance(count, dict):
            for sub_key, sub_count in count.items():
                all_counts.append((f'{component}.{sub_key}', sub_count))
        else:
            all_counts.append((component, count))
    
    # Check consistency
    consistent = True
    for name, count in all_counts:
        if count != EXPECTED_COUNT:
            consistent = False
            issues.append(f"  ❌ {name}: {count} (expected {EXPECTED_COUNT})")
        else:
            print(f"  ✅ {name}: {count} (correct)")
    
    if issues:
        print("\n⚠️ Inconsistencies Found:")
        for issue in issues:
            print(issue)
    
    # 4. Summary
    print("\n" + "=" * 70)
    if consistent and all_counts:
        print("✅ SUCCESS: All ASSEMBLY counts are consistent at 109 members!")
        print("The position mapping conflict fix is working correctly.")
        return 0
    elif not all_counts:
        print("⚠️ WARNING: Could not extract counts. Please regenerate the dashboard.")
        return 1
    else:
        print("❌ FAILURE: Inconsistent counts detected. Further investigation needed.")
        unique_counts = set(count for _, count in all_counts if count != 'N/A')
        print(f"Found counts: {sorted(unique_counts)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())