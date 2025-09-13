#!/usr/bin/env python3
"""
5PRS API 테스트 스크립트
"""

import requests
import json
import sys

def test_api():
    """API 서버 테스트"""
    base_url = "http://localhost:5000"
    
    # 1. Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check 성공:", response.json())
        else:
            print("❌ Health check 실패:", response.status_code)
    except Exception as e:
        print(f"❌ Health check 에러: {e}")
        return False
    
    # 2. API 데이터 가져오기
    try:
        response = requests.get(f"{base_url}/api/5prs-data?month=august&year=2025")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 데이터 성공:")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Records: {len(data.get('data', []))}")
            if data.get('metadata'):
                print(f"   - Source: {data['metadata'].get('source')}")
            
            # 데이터 샘플 출력
            if data.get('data') and len(data['data']) > 0:
                print("\n📊 데이터 샘플 (첫 3개 레코드):")
                for i, record in enumerate(data['data'][:3], 1):
                    print(f"\n   레코드 {i}:")
                    print(f"   - Inspector: {record.get('Inspector Name', 'N/A')}")
                    print(f"   - Building: {record.get('Building', 'N/A')}")
                    print(f"   - Pass Qty: {record.get('Pass Qty', 0)}")
                    print(f"   - Reject Qty: {record.get('Reject Qty', 0)}")
        else:
            print("❌ API 데이터 실패:", response.status_code)
            print("Response:", response.text[:500])
    except Exception as e:
        print(f"❌ API 데이터 에러: {e}")
        return False
    
    # 3. Dashboard 페이지 접근
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("\n✅ Dashboard 페이지 접근 성공")
            print(f"   - HTML 크기: {len(response.text)} bytes")
            if '<title>' in response.text:
                title_start = response.text.find('<title>') + 7
                title_end = response.text.find('</title>')
                title = response.text[title_start:title_end]
                print(f"   - Title: {title}")
        else:
            print("❌ Dashboard 페이지 실패:", response.status_code)
    except Exception as e:
        print(f"❌ Dashboard 페이지 에러: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 5PRS API 서버 테스트 시작...\n")
    success = test_api()
    if success:
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)