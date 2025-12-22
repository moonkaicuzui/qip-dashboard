#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Dashboard Optimizer
========================
@FrontendArchitect & @PerformanceEngineer 협업 개발

대시보드 HTML 파일 최적화:
1. JavaScript minification (공백/주석 제거)
2. CSS minification
3. 불필요한 공백 제거
4. Gzip 압축 가능 크기 측정

사용법:
    python scripts/optimize_html.py [--input FILE] [--output FILE]
    python scripts/optimize_html.py --all  # 모든 대시보드 최적화
"""

import re
import os
import sys
import argparse
import gzip
from pathlib import Path
from typing import Tuple, Optional


def minify_javascript(js_code: str) -> str:
    """
    JavaScript 코드 minification (기본)

    - 단일 행 주석 제거
    - 불필요한 공백 제거
    - 빈 줄 제거

    Note: 복잡한 minification은 외부 도구(terser) 권장
    """
    lines = []
    in_multiline_comment = False

    for line in js_code.split('\n'):
        # 멀티라인 주석 처리
        if in_multiline_comment:
            if '*/' in line:
                in_multiline_comment = False
                line = line[line.index('*/') + 2:]
            else:
                continue

        if '/*' in line:
            if '*/' in line:
                # 같은 줄에서 시작과 끝
                line = re.sub(r'/\*.*?\*/', '', line)
            else:
                in_multiline_comment = True
                line = line[:line.index('/*')]

        # 문자열 내부가 아닌 단일 행 주석 제거 (간단한 버전)
        # 주의: 문자열 내 '//' 오탐 가능성 있음
        if '//' in line and not re.search(r'["\'].*//.*["\']', line):
            # URL 형태 (http://, https://) 보존
            if not re.search(r'https?://', line):
                comment_idx = line.index('//')
                # 문자열 내부가 아닌지 확인 (간단한 휴리스틱)
                quote_count = line[:comment_idx].count('"') + line[:comment_idx].count("'")
                if quote_count % 2 == 0:  # 짝수면 문자열 외부
                    line = line[:comment_idx]

        # 앞뒤 공백 제거
        line = line.strip()

        # 빈 줄 건너뛰기
        if line:
            lines.append(line)

    # 여러 공백을 하나로
    result = '\n'.join(lines)
    result = re.sub(r'  +', ' ', result)

    return result


def minify_css(css_code: str) -> str:
    """
    CSS 코드 minification

    - 주석 제거
    - 불필요한 공백 제거
    """
    # 주석 제거
    css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)

    # 줄바꿈을 공백으로
    css_code = css_code.replace('\n', ' ')

    # 여러 공백을 하나로
    css_code = re.sub(r'\s+', ' ', css_code)

    # 특수 문자 주변 공백 제거
    css_code = re.sub(r'\s*([{};:,])\s*', r'\1', css_code)

    return css_code.strip()


def optimize_html(html_content: str, verbose: bool = False) -> Tuple[str, dict]:
    """
    HTML 전체 최적화

    Returns:
        (최적화된 HTML, 통계 dict)
    """
    original_size = len(html_content.encode('utf-8'))
    stats = {
        'original_size': original_size,
        'js_blocks': 0,
        'css_blocks': 0,
    }

    # JavaScript 블록 최적화
    def optimize_js_block(match):
        stats['js_blocks'] += 1
        script_tag = match.group(1)
        js_code = match.group(2)
        end_tag = match.group(3)

        # 외부 스크립트는 건너뛰기
        if 'src=' in script_tag:
            return match.group(0)

        minified = minify_javascript(js_code)
        if verbose:
            orig_len = len(js_code)
            new_len = len(minified)
            savings = (1 - new_len / orig_len) * 100 if orig_len > 0 else 0
            print(f"  JS block {stats['js_blocks']}: {orig_len:,} → {new_len:,} ({savings:.1f}% 절감)")

        return f"{script_tag}\n{minified}\n{end_tag}"

    html_content = re.sub(
        r'(<script[^>]*>)(.*?)(</script>)',
        optimize_js_block,
        html_content,
        flags=re.DOTALL
    )

    # CSS 블록 최적화
    def optimize_css_block(match):
        stats['css_blocks'] += 1
        style_tag = match.group(1)
        css_code = match.group(2)
        end_tag = match.group(3)

        minified = minify_css(css_code)
        if verbose:
            orig_len = len(css_code)
            new_len = len(minified)
            savings = (1 - new_len / orig_len) * 100 if orig_len > 0 else 0
            print(f"  CSS block {stats['css_blocks']}: {orig_len:,} → {new_len:,} ({savings:.1f}% 절감)")

        return f"{style_tag}{minified}{end_tag}"

    html_content = re.sub(
        r'(<style[^>]*>)(.*?)(</style>)',
        optimize_css_block,
        html_content,
        flags=re.DOTALL
    )

    # HTML 공백 최적화 (태그 사이 불필요한 공백)
    html_content = re.sub(r'>\s+<', '>\n<', html_content)

    # 빈 줄 제거
    html_content = re.sub(r'\n\s*\n', '\n', html_content)

    optimized_size = len(html_content.encode('utf-8'))
    stats['optimized_size'] = optimized_size
    stats['savings_bytes'] = original_size - optimized_size
    stats['savings_pct'] = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0

    # Gzip 압축 크기 측정
    gzipped = gzip.compress(html_content.encode('utf-8'))
    stats['gzip_size'] = len(gzipped)
    stats['gzip_pct'] = (1 - len(gzipped) / original_size) * 100 if original_size > 0 else 0

    return html_content, stats


def optimize_file(input_path: str, output_path: str = None, verbose: bool = True) -> dict:
    """
    단일 파일 최적화

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로 (None이면 덮어쓰기)
        verbose: 상세 출력

    Returns:
        최적화 통계
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"📦 최적화: {Path(input_path).name}")
        print(f"{'='*60}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    optimized, stats = optimize_html(content, verbose=verbose)

    output = output_path or input_path
    with open(output, 'w', encoding='utf-8') as f:
        f.write(optimized)

    if verbose:
        print(f"\n📊 결과:")
        print(f"   원본: {stats['original_size']:,} bytes ({stats['original_size']/1024/1024:.2f} MB)")
        print(f"   최적화: {stats['optimized_size']:,} bytes ({stats['optimized_size']/1024/1024:.2f} MB)")
        print(f"   절감: {stats['savings_bytes']:,} bytes ({stats['savings_pct']:.1f}%)")
        print(f"   Gzip: {stats['gzip_size']:,} bytes ({stats['gzip_pct']:.1f}% 압축)")

    return stats


def optimize_all_dashboards(docs_dir: str = 'docs', verbose: bool = True) -> dict:
    """
    모든 대시보드 파일 최적화

    Args:
        docs_dir: docs 디렉토리 경로
        verbose: 상세 출력

    Returns:
        전체 통계
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"❌ 디렉토리 없음: {docs_dir}")
        return {}

    # 대시보드 파일 찾기
    pattern = re.compile(r'Incentive_Dashboard_\d{4}_\d{2}_Version_[\d.]+\.html$')
    dashboard_files = [f for f in docs_path.glob('*.html')
                       if pattern.match(f.name) and 'SelfContained' not in f.name]

    if not dashboard_files:
        print("⚠️ 대시보드 파일을 찾을 수 없습니다")
        return {}

    print(f"🔍 {len(dashboard_files)}개 대시보드 파일 발견")

    total_stats = {
        'files': 0,
        'original_total': 0,
        'optimized_total': 0,
        'savings_total': 0,
    }

    for file_path in sorted(dashboard_files):
        stats = optimize_file(str(file_path), verbose=verbose)
        total_stats['files'] += 1
        total_stats['original_total'] += stats['original_size']
        total_stats['optimized_total'] += stats['optimized_size']
        total_stats['savings_total'] += stats['savings_bytes']

    # 전체 요약
    print(f"\n{'='*60}")
    print("📊 전체 요약")
    print(f"{'='*60}")
    print(f"   파일 수: {total_stats['files']}")
    print(f"   원본 총합: {total_stats['original_total']:,} bytes ({total_stats['original_total']/1024/1024:.2f} MB)")
    print(f"   최적화 총합: {total_stats['optimized_total']:,} bytes ({total_stats['optimized_total']/1024/1024:.2f} MB)")
    savings_pct = (1 - total_stats['optimized_total'] / total_stats['original_total']) * 100 if total_stats['original_total'] > 0 else 0
    print(f"   총 절감: {total_stats['savings_total']:,} bytes ({savings_pct:.1f}%)")

    return total_stats


def main():
    parser = argparse.ArgumentParser(description='HTML Dashboard Optimizer')
    parser.add_argument('--input', '-i', help='입력 파일')
    parser.add_argument('--output', '-o', help='출력 파일 (기본: 덮어쓰기)')
    parser.add_argument('--all', '-a', action='store_true', help='모든 대시보드 최적화')
    parser.add_argument('--quiet', '-q', action='store_true', help='간략한 출력')
    args = parser.parse_args()

    if args.all:
        optimize_all_dashboards(verbose=not args.quiet)
    elif args.input:
        optimize_file(args.input, args.output, verbose=not args.quiet)
    else:
        parser.print_help()
        print("\n예시:")
        print("  python scripts/optimize_html.py --all")
        print("  python scripts/optimize_html.py -i docs/dashboard.html")


if __name__ == '__main__':
    main()
