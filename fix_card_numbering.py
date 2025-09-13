#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix duplicate card #6 numbering issue in management dashboard
Changes the numbering from 1,2,3,4,5,6,6,7,8,9 to 1,2,3,4,5,6,7,8,9,10
"""

import re
from pathlib import Path

def fix_card_numbering(input_file, output_file):
    """Fix the duplicate card #6 numbering issue"""
    
    print(f"📋 Reading dashboard from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find and fix the card numbering
    # The cards are in order, so we need to renumber from the second #6 onwards
    
    # Strategy: Find all card-number divs and renumber them correctly
    card_pattern = r'<div class="card-number">(\d+)</div>'
    
    # Find all matches
    matches = list(re.finditer(card_pattern, html_content))
    print(f"🔍 Found {len(matches)} KPI cards")
    
    # Create a mapping of what needs to be changed
    # Cards are: 1,2,3,4,5,6,6,7,8,9 -> should be 1,2,3,4,5,6,7,8,9,10
    replacements = []
    card_count = 0
    seen_six = False
    
    for match in matches:
        card_count += 1
        current_num = match.group(1)
        
        if current_num == '6':
            if not seen_six:
                # First #6 stays as #6
                seen_six = True
                new_num = '6'
            else:
                # Second #6 becomes #7
                new_num = '7'
                replacements.append((match.start(), match.end(), f'<div class="card-number">{new_num}</div>'))
        elif seen_six and current_num == '6':
            # This is the second #6
            new_num = '7'
            replacements.append((match.start(), match.end(), f'<div class="card-number">{new_num}</div>'))
        elif current_num == '7' and seen_six:
            # Original #7 becomes #8
            new_num = '8'
            replacements.append((match.start(), match.end(), f'<div class="card-number">{new_num}</div>'))
        elif current_num == '8' and seen_six:
            # Original #8 becomes #9
            new_num = '9'
            replacements.append((match.start(), match.end(), f'<div class="card-number">{new_num}</div>'))
        elif current_num == '9' and seen_six:
            # Original #9 becomes #10
            new_num = '10'
            replacements.append((match.start(), match.end(), f'<div class="card-number">{new_num}</div>'))
    
    # Apply replacements in reverse order to maintain positions
    for start, end, new_text in reversed(replacements):
        html_content = html_content[:start] + new_text + html_content[end:]
    
    # Also update modal IDs to match if needed
    # The modal IDs are already unique, so we don't need to change them
    # But let's add comments to make it clear which card triggers which modal
    
    # Add a comment before each card for clarity
    card_info = [
        ('modal-total-employees', 'Card #1: 총인원 정보'),
        ('showErrorDetails', 'Card #2: 데이터 오류 인원'),
        ('modal-absence', 'Card #3: 결근자 정보/결근율'),
        ('modal-resignation', 'Card #4: 퇴사율'),
        ('modal-new-hires', 'Card #5: 최근 30일내 입사 인원'),
        ('modal-new-resignations', 'Card #6: 최근 30일내 퇴사 인원'),
        ('modal-under-60', 'Card #7: 입사 60일 미만 인원'),
        ('modal-post-assignment', 'Card #8: 보직 부여 후 퇴사 인원'),
        ('modal-full-attendance', 'Card #9: 만근자'),
        ('modal-long-term', 'Card #10: 장기근속자')
    ]
    
    # Add HTML comments before each card
    for modal_id, comment in card_info:
        if 'showErrorDetails' in modal_id:
            pattern = r'(<div class="hr-card" onclick="showErrorDetails\(\)")'
        else:
            pattern = f'(<div class="hr-card" onclick="openModal\(\'{modal_id}\'\)")'
        
        replacement = f'<!-- {comment} -->\n            \\1'
        html_content = re.sub(pattern, replacement, html_content)
    
    # Save the fixed HTML
    print(f"💾 Saving fixed dashboard to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Card numbering fixed successfully!")
    print("\n📊 Card Numbering Changes:")
    print("   Before: 1, 2, 3, 4, 5, 6, 6, 7, 8, 9")
    print("   After:  1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
    
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("KPI 카드 번호 중복 수정")
    print("=" * 60)
    
    # Find the most recent dashboard file
    dashboard_dir = Path(__file__).parent / 'output_files'
    input_file = dashboard_dir / 'management_dashboard_2025_08.html'
    
    if not input_file.exists():
        print(f"❌ Dashboard file not found: {input_file}")
        return 1
    
    # Create output file name
    output_file = dashboard_dir / 'management_dashboard_2025_08_fixed_numbering.html'
    
    # Fix the numbering
    fix_card_numbering(input_file, output_file)
    
    # Open in browser
    import webbrowser
    import os
    full_path = os.path.abspath(output_file)
    webbrowser.open(f'file://{full_path}')
    print("\n브라우저에서 수정된 대시보드가 열립니다...")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())