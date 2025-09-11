#!/usr/bin/env python3
"""
5PRS 데이터 API 서버
input_files 폴더의 5PRS CSV 데이터를 통합하여 JSON으로 제공
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import glob
from datetime import datetime

app = Flask(__name__)
CORS(app)  # CORS 허용

def load_and_merge_5prs_data():
    """input_files 폴더의 모든 5prs 데이터를 로드하고 병합"""
    
    # 파일 경로 패턴
    file_patterns = [
        'input_files/5prs data*.csv',
        'input_files/5prs_data*.csv'
    ]
    
    all_files = []
    for pattern in file_patterns:
        all_files.extend(glob.glob(pattern))
    
    # 중복 제거
    all_files = list(set(all_files))
    
    if not all_files:
        print("No 5PRS data files found!")
        return []
    
    print(f"Found {len(all_files)} 5PRS data files")
    
    # 모든 파일을 DataFrame으로 읽기
    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            print(f"Loaded {len(df)} rows from {os.path.basename(file)}")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")
            continue
    
    if not dfs:
        return []
    
    # 모든 DataFrame 병합
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # 중복 제거
    if all(['Inspection Date' in merged_df.columns, 
            'Inspector ID' in merged_df.columns, 
            'Time' in merged_df.columns, 
            'TQC ID' in merged_df.columns]):
        merged_df = merged_df.drop_duplicates(
            subset=['Inspection Date', 'Inspector ID', 'Time', 'TQC ID'], 
            keep='first'
        )
    
    print(f"Total merged records: {len(merged_df)}")
    
    # 날짜 형식 표준화
    if 'Inspection Date' in merged_df.columns:
        # 다양한 날짜 형식 처리
        for fmt in ['%d/%m/%y', '%m/%d/%y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                merged_df['Inspection Date'] = pd.to_datetime(
                    merged_df['Inspection Date'], 
                    format=fmt, 
                    errors='coerce'
                )
                # 성공하면 문자열로 변환
                merged_df['Inspection Date'] = merged_df['Inspection Date'].dt.strftime('%Y-%m-%d')
                break
            except:
                continue
    
    # NaN 값을 빈 문자열로 변환
    merged_df = merged_df.fillna('')
    
    # DataFrame을 딕셔너리 리스트로 변환
    data = merged_df.to_dict('records')
    
    # 컬럼명 표준화 (원본 대시보드와 호환)
    standardized_data = []
    for row in data:
        new_row = {}
        
        # 컬럼 매핑
        column_mapping = {
            'Inspection Date': 'Inspection Date',
            'Inspector ID': 'Inspector ID',
            'Inspector Name': 'Inspector Name',
            'Time': 'Time',
            'Building': 'Building',
            'Line': 'Line',
            'PO No': 'PO No',
            'PO Item': 'PO Item',
            'Model': 'Model',
            'TQC ID': 'TQC ID',
            'TQC Name': 'TQC Name',
            'Valiation Qty': 'Validation Qty',  # 오타 수정
            'Pass Qty': 'Pass Qty',
            'Reject Qty': 'Reject Qty',
            'Error': 'Error'
        }
        
        for original, standard in column_mapping.items():
            if original in row:
                value = row[original]
                # 숫자형 데이터 처리
                if standard in ['Validation Qty', 'Pass Qty', 'Reject Qty']:
                    try:
                        new_row[standard] = int(float(value)) if value != '' else 0
                    except:
                        new_row[standard] = 0
                else:
                    new_row[standard] = str(value) if value != '' else ''
            else:
                # 기본값 설정
                if standard in ['Validation Qty', 'Pass Qty', 'Reject Qty']:
                    new_row[standard] = 0
                else:
                    new_row[standard] = ''
        
        standardized_data.append(new_row)
    
    return standardized_data

@app.route('/api/5prs-data')
def get_5prs_data():
    """5PRS 데이터를 JSON으로 반환"""
    try:
        data = load_and_merge_5prs_data()
        
        # 데이터 요약 정보 추가
        summary = {
            'total_records': len(data),
            'last_updated': datetime.now().isoformat(),
            'status': 'success'
        }
        
        return jsonify({
            'data': data,
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health')
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# 원본 대시보드 파일 서빙
@app.route('/')
def serve_dashboard():
    """수정된 대시보드 제공"""
    return send_from_directory('5PRS DASHBOARD', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """정적 파일 제공"""
    return send_from_directory('5PRS DASHBOARD', path)

if __name__ == '__main__':
    print("=" * 60)
    print("5PRS Data API Server")
    print("=" * 60)
    print("Server running at: http://localhost:5001")
    print("API Endpoint: http://localhost:5001/api/5prs-data")
    print("Dashboard: http://localhost:5001/")
    print("=" * 60)
    
    # 초기 데이터 로드 테스트
    test_data = load_and_merge_5prs_data()
    print(f"Initial data loaded: {len(test_data)} records")
    
    app.run(debug=True, port=5001, host='0.0.0.0')