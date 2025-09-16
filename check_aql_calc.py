import pandas as pd

# AQL 파일 로드
aql_file = "input_files/AQL history/1.HSRG AQL REPORT-AUGUST.2025.csv"

# 헤더 찾기
with open(aql_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    header_idx = None
    for i, line in enumerate(lines):
        if 'EMPLOYEE NO' in line:
            header_idx = i
            break

if header_idx is not None:
    # 헤더 이후 데이터만 읽기
    df = pd.read_csv(aql_file, skiprows=header_idx)

    # 컬럼명 확인
    print("Columns in AQL file:")
    print(df.columns.tolist())

    # 직원 624110274의 데이터 필터링
    if 'EMPLOYEE NO' in df.columns:
        emp_df = df[df['EMPLOYEE NO'] == 624110274]
    else:
        # 컬럼명이 다를 수 있으므로 확인
        emp_col = None
        for col in df.columns:
            if 'EMPLOYEE' in col.upper():
                emp_col = col
                break
        if emp_col:
            emp_df = df[df[emp_col] == 624110274]
        else:
            print("Cannot find EMPLOYEE NO column")
            emp_df = pd.DataFrame()

    print(f"Total rows for 624110274: {len(emp_df)}")
    print(f"\nRESULT column values:")
    print(emp_df['RESULT'].value_counts())

    # FAIL 건수 세기
    fail_count = len(emp_df[emp_df['RESULT'].str.upper() == 'FAIL'])
    print(f"\nFAIL count: {fail_count}")

    # 날짜별 RESULT 확인
    print(f"\nDate and Result:")
    for _, row in emp_df.iterrows():
        print(f"  {row['DATE']}: {row['RESULT']}")
else:
    print("Header not found")