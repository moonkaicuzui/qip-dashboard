#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
from collections import defaultdict

def build_hierarchy():
    """Build hierarchy for TYPE-1 ASSEMBLY INSPECTOR employees"""

    # Load basic manpower data
    df = pd.read_csv('input_files/basic manpower data september.csv', encoding='utf-8-sig')

    # Filter for TYPE-1 ASSEMBLY INSPECTOR only (not hardcoded - from data)
    assembly_inspectors = df[
        (df['ROLE TYPE STD'] == 'TYPE-1') &
        (df['QIP POSITION 1ST  NAME'].str.upper() == 'ASSEMBLY INSPECTOR')
    ].copy()

    print(f"Found {len(assembly_inspectors)} TYPE-1 ASSEMBLY INSPECTOR employees")

    # Create employee lookup dictionary (ID -> Name, Position)
    employee_lookup = {}
    for _, row in df.iterrows():
        emp_id = str(row['Employee No'])
        employee_lookup[emp_id] = {
            'name': row['Full Name'],
            'position': row['QIP POSITION 1ST  NAME'],
            'type': row.get('ROLE TYPE STD', ''),
            'boss_id': str(row['MST direct boss name']) if pd.notna(row['MST direct boss name']) else None,
            'boss_name': row['direct boss name'] if pd.notna(row['direct boss name']) else None
        }

    # Build hierarchy for each assembly inspector
    hierarchy = []

    for _, inspector in assembly_inspectors.iterrows():
        emp_id = str(inspector['Employee No'])
        emp_name = inspector['Full Name']

        # Build chain up to manager level
        chain = []
        current_id = emp_id
        visited = set()  # Prevent infinite loops

        while current_id and current_id in employee_lookup and current_id not in visited:
            visited.add(current_id)
            emp_info = employee_lookup[current_id]

            chain.append({
                'id': current_id,
                'name': emp_info['name'],
                'position': emp_info['position'],
                'type': emp_info['type'],
                'level': len(chain)
            })

            # Stop at manager level or if no boss
            if emp_info['position'] and 'MANAGER' in str(emp_info['position']).upper():
                if 'A.MANAGER' not in str(emp_info['position']).upper():
                    break

            current_id = emp_info['boss_id']

            # Safety check - stop after 10 levels
            if len(chain) > 10:
                break

        hierarchy.append({
            'inspector': {
                'id': emp_id,
                'name': emp_name,
                'position': 'ASSEMBLY INSPECTOR'
            },
            'chain': chain
        })

    return hierarchy, assembly_inspectors, employee_lookup

def visualize_hierarchy(hierarchy):
    """Create visual representation of hierarchy"""

    print("\n" + "="*80)
    print("TYPE-1 ASSEMBLY INSPECTOR ORGANIZATIONAL HIERARCHY")
    print("="*80)

    for item in hierarchy:
        inspector = item['inspector']
        chain = item['chain']

        print(f"\n{inspector['name']} ({inspector['id']})")
        print("  └─ ASSEMBLY INSPECTOR (TYPE-1)")

        for i, person in enumerate(chain[1:], 1):  # Skip first (self)
            indent = "  " * (i + 1)
            connector = "└─" if i == len(chain) - 1 else "├─"
            print(f"{indent}{connector} {person['name']} - {person['position']} ({person['id']})")

    print("\n" + "="*80)

def generate_org_chart_data(hierarchy, employee_lookup):
    """Generate data for D3.js organization chart"""

    # Build unique hierarchy tree
    nodes = {}
    edges = []

    # First pass: collect all unique nodes
    for item in hierarchy:
        for person in item['chain']:
            if person['id'] not in nodes:
                nodes[person['id']] = {
                    'id': person['id'],
                    'name': person['name'],
                    'position': person['position'],
                    'type': person['type']
                }

    # Second pass: build edges
    processed_edges = set()
    for item in hierarchy:
        chain = item['chain']
        for i in range(len(chain) - 1):
            child_id = chain[i]['id']
            parent_id = chain[i + 1]['id']
            edge_key = f"{child_id}-{parent_id}"

            if edge_key not in processed_edges:
                edges.append({
                    'source': parent_id,
                    'target': child_id
                })
                processed_edges.add(edge_key)

    # Convert to list format for D3.js
    org_data = []
    for node_id, node_info in nodes.items():
        parent_id = None
        for edge in edges:
            if edge['target'] == node_id:
                parent_id = edge['source']
                break

        org_data.append({
            'id': node_id,
            'name': node_info['name'],
            'position': node_info['position'],
            'type': node_info['type'],
            'parent_id': parent_id
        })

    return org_data

def main():
    print("Analyzing TYPE-1 ASSEMBLY INSPECTOR Hierarchy...")

    hierarchy, inspectors_df, employee_lookup = build_hierarchy()

    # Show summary statistics
    print(f"\nSummary:")
    print(f"- Total TYPE-1 ASSEMBLY INSPECTOR: {len(inspectors_df)}")

    # Count unique bosses
    boss_counts = inspectors_df['direct boss name'].value_counts()
    print(f"- Unique direct bosses: {len(boss_counts)}")
    print("\nTop 5 direct bosses:")
    for boss, count in boss_counts.head().items():
        print(f"  - {boss}: {count} inspectors")

    # Visualize hierarchy
    visualize_hierarchy(hierarchy)

    # Generate org chart data
    org_data = generate_org_chart_data(hierarchy, employee_lookup)

    # Save to JSON for visualization
    with open('assembly_inspector_hierarchy.json', 'w', encoding='utf-8') as f:
        json.dump(org_data, f, ensure_ascii=False, indent=2)

    print(f"\nOrganization data saved to assembly_inspector_hierarchy.json")
    print(f"Total nodes in hierarchy: {len(org_data)}")

if __name__ == "__main__":
    main()