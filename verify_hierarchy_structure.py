#!/usr/bin/env python3
"""
조직도 계층 구조 시각적 검증
"""

from playwright.sync_api import sync_playwright
import time
import os
import json

dashboard_path = f"file://{os.path.abspath('output_files/Incentive_Dashboard_2025_09_Version_6.html')}"

print("🔍 조직도 계층 구조 시각적 검증\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("📂 대시보드 로딩...")
    page.goto(dashboard_path)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Org Chart 탭 클릭
    page.click("#tabOrgChart")
    time.sleep(2)

    print("\n📊 계층 구조 분석:\n")

    try:
        # 계층 구조 데이터 추출
        hierarchy_data = page.evaluate("""
            () => {
                // buildHierarchyData 함수를 직접 호출
                if (typeof buildHierarchyData === 'undefined') {
                    return { error: 'buildHierarchyData function not found' };
                }

                const hierarchyData = buildHierarchyData();
                if (!hierarchyData || hierarchyData.length === 0) {
                    return { error: 'No hierarchy data generated' };
                }

                // 재귀적으로 계층 구조 출력
                function buildTree(node, level = 0) {
                    const indent = '  '.repeat(level);
                    const result = {
                        level: level,
                        name: node.name,
                        position: node.position,
                        emp_no: node.emp_no,
                        children_count: node.children ? node.children.length : 0,
                        children: []
                    };

                    if (node.children && node.children.length > 0) {
                        result.children = node.children.map(child => buildTree(child, level + 1));
                    }

                    return result;
                }

                return {
                    root_count: hierarchyData.length,
                    tree: hierarchyData.map(root => buildTree(root))
                };
            }
        """)

        if 'error' in hierarchy_data:
            print(f"❌ {hierarchy_data['error']}")
        else:
            print(f"=== 계층 구조 트리 ===")
            print(f"Root nodes: {hierarchy_data['root_count']}개\n")

            def print_tree(node, prefix=""):
                """재귀적으로 트리 구조 출력"""
                print(f"{prefix}├─ {node['name']} ({node['position']}) [emp_no: {node['emp_no']}]")
                print(f"{prefix}│  └─ Children: {node['children_count']}명")

                for i, child in enumerate(node['children']):
                    is_last = (i == len(node['children']) - 1)
                    child_prefix = prefix + ("   " if is_last else "│  ")
                    print_tree(child, child_prefix)

            for i, root in enumerate(hierarchy_data['tree']):
                print(f"\n🌳 Root Node {i+1}:")
                print_tree(root, "")

            # 통계 정보
            def count_nodes(node):
                """전체 노드 수 계산"""
                count = 1
                for child in node.get('children', []):
                    count += count_nodes(child)
                return count

            total_nodes = sum(count_nodes(root) for root in hierarchy_data['tree'])
            print(f"\n📊 통계:")
            print(f"  - 전체 노드 수: {total_nodes}명")
            print(f"  - Root nodes: {hierarchy_data['root_count']}개")

            # 최대 깊이 계산
            def max_depth(node):
                if not node.get('children'):
                    return node['level']
                return max(max_depth(child) for child in node['children'])

            max_level = max(max_depth(root) for root in hierarchy_data['tree'])
            print(f"  - 최대 계층 깊이: {max_level + 1} 레벨")

    except Exception as e:
        print(f"❌ JavaScript 평가 오류: {e}")

    if page_errors:
        print(f"\n❌ JavaScript 오류: {len(page_errors)}개")
        for err in page_errors[:3]:
            print(f"   - {err}")
    else:
        print("\n✅ JavaScript 오류 없음")

    browser.close()

print("\n✅ 검증 완료")