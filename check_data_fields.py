#!/usr/bin/env python3
"""
직원 데이터의 실제 필드와 값을 확인하는 스크립트
AQL과 5PRS 데이터가 실제로 있는지 검증
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def check_employee_data_fields():
    """직원 데이터 필드 확인"""

    dashboard_path = "/Users/ksmoon/Downloads/대시보드 인센티브 테스트12_9월 25일/output_files/Incentive_Dashboard_2025_09_Version_6.html"

    print("🔍 Checking actual employee data fields...\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("📄 Loading dashboard...")
        await page.goto(f"file://{dashboard_path}")
        await page.wait_for_timeout(2000)

        # JavaScript로 직원 데이터 분석
        data_analysis = await page.evaluate("""() => {
            const employees = window.employeeData;
            if (!employees || employees.length === 0) {
                return { error: "No employee data found" };
            }

            // TYPE별로 직원 분류
            const type1Employees = employees.filter(e => e.type === 'TYPE-1');
            const type2Employees = employees.filter(e => e.type === 'TYPE-2');

            // 첫 번째 TYPE-1 직원 샘플
            const type1Sample = type1Employees[0] || {};

            // 첫 번째 TYPE-2 직원 샘플
            const type2Sample = type2Employees[0] || {};

            // AQL 관련 필드 찾기
            const aqlFields = [];
            const prsFields = [];
            const allFields = Object.keys(type1Sample);

            allFields.forEach(field => {
                const fieldLower = field.toLowerCase();
                if (fieldLower.includes('aql')) {
                    aqlFields.push({
                        name: field,
                        sampleValue: type1Sample[field]
                    });
                }
                if (fieldLower.includes('5prs') || fieldLower.includes('prs') || fieldLower.includes('5pr')) {
                    prsFields.push({
                        name: field,
                        sampleValue: type1Sample[field]
                    });
                }
            });

            // 각 TYPE별 AQL/5PRS 데이터 분석
            const analyzeData = (employees, typeName) => {
                const analysis = {
                    total: employees.length,
                    aql_data: { with_value: 0, empty: 0, values: {} },
                    prs_data: { with_value: 0, empty: 0, values: {} }
                };

                employees.forEach(emp => {
                    // AQL 체크
                    const aqlValue = emp['AQL'] || emp['aql'] || emp['AQL result'] || emp['AQL결과'];
                    if (aqlValue !== undefined && aqlValue !== '' && aqlValue !== null) {
                        analysis.aql_data.with_value++;
                        analysis.aql_data.values[aqlValue] = (analysis.aql_data.values[aqlValue] || 0) + 1;
                    } else {
                        analysis.aql_data.empty++;
                    }

                    // 5PRS 체크
                    const prsValue = emp['Average 5PRS score'] || emp['5PRS score'] || emp['5prs_score'] || emp['5PRS점수'];
                    if (prsValue !== undefined && prsValue !== '' && prsValue !== null) {
                        analysis.prs_data.with_value++;
                    } else {
                        analysis.prs_data.empty++;
                    }
                });

                return analysis;
            };

            return {
                totalEmployees: employees.length,
                type1Count: type1Employees.length,
                type2Count: type2Employees.length,
                allFields: allFields,
                aqlFields: aqlFields,
                prsFields: prsFields,
                type1Sample: {
                    name: type1Sample.name,
                    position: type1Sample.position,
                    AQL: type1Sample['AQL'],
                    '5PRS': type1Sample['Average 5PRS score'],
                    attendance: type1Sample['attendance_rate_%'] || type1Sample['attendance_rate']
                },
                type2Sample: {
                    name: type2Sample.name,
                    position: type2Sample.position,
                    AQL: type2Sample['AQL'],
                    '5PRS': type2Sample['Average 5PRS score'],
                    attendance: type2Sample['attendance_rate_%'] || type2Sample['attendance_rate']
                },
                type1Analysis: analyzeData(type1Employees, 'TYPE-1'),
                type2Analysis: analyzeData(type2Employees, 'TYPE-2')
            };
        }""")

        # 결과 출력
        print("\n" + "="*60)
        print("📊 DATA STRUCTURE ANALYSIS")
        print("="*60)

        if 'error' in data_analysis:
            print(f"❌ Error: {data_analysis['error']}")
        else:
            print(f"\n📈 Employee Overview:")
            print(f"  Total employees: {data_analysis['totalEmployees']}")
            print(f"  TYPE-1: {data_analysis['type1Count']} employees")
            print(f"  TYPE-2: {data_analysis['type2Count']} employees")

            print(f"\n🔍 AQL Fields Found:")
            if data_analysis['aqlFields']:
                for field in data_analysis['aqlFields']:
                    print(f"  - {field['name']}: {field['sampleValue']}")
            else:
                print("  ❌ No AQL fields found in data")

            print(f"\n🔍 5PRS Fields Found:")
            if data_analysis['prsFields']:
                for field in data_analysis['prsFields']:
                    print(f"  - {field['name']}: {field['sampleValue']}")
            else:
                print("  ❌ No 5PRS fields found in data")

            print(f"\n📝 TYPE-1 Sample Employee:")
            sample1 = data_analysis['type1Sample']
            print(f"  Name: {sample1.get('name', 'N/A')}")
            print(f"  Position: {sample1.get('position', 'N/A')}")
            print(f"  AQL: {sample1.get('AQL', 'N/A')}")
            print(f"  5PRS: {sample1.get('5PRS', 'N/A')}")
            print(f"  Attendance: {sample1.get('attendance', 'N/A')}")

            print(f"\n📝 TYPE-2 Sample Employee:")
            sample2 = data_analysis['type2Sample']
            print(f"  Name: {sample2.get('name', 'N/A')}")
            print(f"  Position: {sample2.get('position', 'N/A')}")
            print(f"  AQL: {sample2.get('AQL', 'N/A')}")
            print(f"  5PRS: {sample2.get('5PRS', 'N/A')}")
            print(f"  Attendance: {sample2.get('attendance', 'N/A')}")

            # TYPE-1 AQL/5PRS 분석
            print(f"\n📊 TYPE-1 Data Analysis ({data_analysis['type1Count']} employees):")
            type1_analysis = data_analysis['type1Analysis']
            print(f"  AQL Data:")
            print(f"    - With value: {type1_analysis['aql_data']['with_value']}")
            print(f"    - Empty/N/A: {type1_analysis['aql_data']['empty']}")
            if type1_analysis['aql_data']['values']:
                print(f"    - Value distribution: {type1_analysis['aql_data']['values']}")
            print(f"  5PRS Data:")
            print(f"    - With value: {type1_analysis['prs_data']['with_value']}")
            print(f"    - Empty/N/A: {type1_analysis['prs_data']['empty']}")

            # TYPE-2 AQL/5PRS 분석
            print(f"\n📊 TYPE-2 Data Analysis ({data_analysis['type2Count']} employees):")
            type2_analysis = data_analysis['type2Analysis']
            print(f"  AQL Data:")
            print(f"    - With value: {type2_analysis['aql_data']['with_value']}")
            print(f"    - Empty/N/A: {type2_analysis['aql_data']['empty']}")
            if type2_analysis['aql_data']['values']:
                print(f"    - Value distribution: {type2_analysis['aql_data']['values']}")
            print(f"  5PRS Data:")
            print(f"    - With value: {type2_analysis['prs_data']['with_value']}")
            print(f"    - Empty/N/A: {type2_analysis['prs_data']['empty']}")

            # 전체 필드 목록 (일부)
            print(f"\n📋 All Available Fields (showing all {len(data_analysis['allFields'])} fields):")
            for i, field in enumerate(data_analysis['allFields']):
                print(f"    {i+1}. {field}")

            # 결론
            print("\n" + "="*60)
            print("🎯 CONCLUSION")
            print("="*60)

            # AQL 데이터 판단
            if type1_analysis['aql_data']['with_value'] > 0 or type2_analysis['aql_data']['with_value'] > 0:
                print("✅ AQL data EXISTS in the dataset")
                print(f"   TYPE-1: {type1_analysis['aql_data']['with_value']}/{type1_analysis['total']} have data")
                print(f"   TYPE-2: {type2_analysis['aql_data']['with_value']}/{type2_analysis['total']} have data")
            else:
                print("❌ AQL data is MISSING or all NULL/empty")

            # 5PRS 데이터 판단
            if type1_analysis['prs_data']['with_value'] > 0 or type2_analysis['prs_data']['with_value'] > 0:
                print("✅ 5PRS data EXISTS in the dataset")
                print(f"   TYPE-1: {type1_analysis['prs_data']['with_value']}/{type1_analysis['total']} have data")
                print(f"   TYPE-2: {type2_analysis['prs_data']['with_value']}/{type2_analysis['total']} have data")
            else:
                print("❌ 5PRS data is MISSING or all NULL/empty")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_employee_data_fields())