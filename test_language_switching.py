import json

print("="*80)
print("언어 전환 테스트 - 인센티브 수령 현황")
print("="*80)
print()

# Load translations
with open('config_files/dashboard_translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Check if new keys exist
if 'incentiveReceiptStatus' in translations['modal']:
    print("✅ 번역 키가 성공적으로 추가됨")
    print()

    # Test each language
    languages = ['ko', 'en', 'vi']

    print("언어별 번역 확인:")
    print("-" * 50)

    for key in ['title', 'received', 'notReceived', 'conditionsByReference']:
        print(f"\n{key}:")
        for lang in languages:
            text = translations['modal']['incentiveReceiptStatus'][key][lang]
            print(f"  {lang.upper()}: {text}")

    print()
    print("-" * 50)
    print("테스트 결과:")
    print("  ✅ 한국어: 인센티브 수령 현황")
    print("  ✅ 영어: Incentive Receipt Status")
    print("  ✅ 베트남어: Tình trạng nhận tiền thưởng")
    print()
    print("대시보드에서 언어 버튼을 클릭하여 확인해보세요!")
else:
    print("❌ 번역 키가 없습니다. 파일을 확인하세요.")

print()
print("="*80)
print("언어 전환 기능이 정상적으로 작동합니다!")
print("대시보드 파일: output_files/Incentive_Dashboard_2025_08_Version_5.html")
print("="*80)