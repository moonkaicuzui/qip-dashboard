#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internationalization (i18n) Checker
====================================
@LocalizationExpert & @QAEngineer 협업 개발

다국어 번역 완성도 검사:
- 미번역 텍스트 탐지
- 번역 키 일관성 확인
- 누락된 언어 식별
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


class I18nChecker:
    """다국어 번역 검사기"""

    SUPPORTED_LANGUAGES = ['ko', 'en', 'vi']
    DEFAULT_LANGUAGE = 'ko'

    def __init__(self, translations_path: str = "config_files/dashboard_translations.json"):
        self.translations_path = Path(translations_path)
        self.translations = self._load_translations()
        self.issues: List[Dict] = []

    def _load_translations(self) -> Dict:
        """번역 파일 로드"""
        if self.translations_path.exists():
            with open(self.translations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_all_keys(self, data: Dict, prefix: str = "") -> Set[str]:
        """모든 번역 키 추출"""
        keys = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                # 언어 키인지 확인
                if set(value.keys()) & set(self.SUPPORTED_LANGUAGES):
                    keys.add(full_key)
                else:
                    keys.update(self._get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        return keys

    def _get_translation(self, key: str, lang: str) -> str:
        """특정 키의 번역 조회"""
        parts = key.split('.')
        current = self.translations

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return ""

        if isinstance(current, dict) and lang in current:
            return current[lang]
        return ""

    def check_missing_translations(self) -> List[Dict]:
        """누락된 번역 탐지"""
        missing = []
        all_keys = self._get_all_keys(self.translations)

        for key in all_keys:
            for lang in self.SUPPORTED_LANGUAGES:
                translation = self._get_translation(key, lang)
                if not translation:
                    missing.append({
                        "type": "missing_translation",
                        "key": key,
                        "language": lang,
                        "severity": "high" if lang == self.DEFAULT_LANGUAGE else "medium"
                    })

        return missing

    def check_placeholder_consistency(self) -> List[Dict]:
        """플레이스홀더 일관성 검사"""
        inconsistencies = []
        all_keys = self._get_all_keys(self.translations)

        placeholder_pattern = re.compile(r'\{[^}]+\}')

        for key in all_keys:
            placeholders_by_lang = {}

            for lang in self.SUPPORTED_LANGUAGES:
                translation = self._get_translation(key, lang)
                if translation and isinstance(translation, str):
                    placeholders = set(placeholder_pattern.findall(translation))
                    placeholders_by_lang[lang] = placeholders

            # 언어 간 플레이스홀더 비교
            if len(placeholders_by_lang) > 1:
                all_placeholders = list(placeholders_by_lang.values())
                if len(set(map(frozenset, all_placeholders))) > 1:
                    inconsistencies.append({
                        "type": "placeholder_mismatch",
                        "key": key,
                        "placeholders": {
                            lang: list(phs) for lang, phs in placeholders_by_lang.items()
                        },
                        "severity": "high"
                    })

        return inconsistencies

    def check_empty_translations(self) -> List[Dict]:
        """빈 번역 탐지"""
        empty = []
        all_keys = self._get_all_keys(self.translations)

        for key in all_keys:
            for lang in self.SUPPORTED_LANGUAGES:
                translation = self._get_translation(key, lang)
                if translation is not None and isinstance(translation, str) and translation.strip() == "":
                    empty.append({
                        "type": "empty_translation",
                        "key": key,
                        "language": lang,
                        "severity": "medium"
                    })

        return empty

    def check_hardcoded_text_in_html(self, html_path: str) -> List[Dict]:
        """HTML에서 하드코딩된 텍스트 탐지"""
        hardcoded = []
        html_file = Path(html_path)

        if not html_file.exists():
            return hardcoded

        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 한글 텍스트 탐지 (data-i18n 속성 없는 경우)
        korean_pattern = re.compile(r'>([^<]*[\uac00-\ud7a3]+[^<]*)<', re.MULTILINE)

        for match in korean_pattern.finditer(content):
            text = match.group(1).strip()
            if text and len(text) > 2:
                # data-i18n 속성 확인
                start = max(0, match.start() - 200)
                context = content[start:match.start()]
                if 'data-i18n' not in context and 'data-lang' not in context:
                    hardcoded.append({
                        "type": "hardcoded_text",
                        "text": text[:50] + ("..." if len(text) > 50 else ""),
                        "position": match.start(),
                        "severity": "low"
                    })

        return hardcoded[:20]  # 상위 20개만

    def get_translation_coverage(self) -> Dict:
        """언어별 번역 커버리지"""
        all_keys = self._get_all_keys(self.translations)
        total_keys = len(all_keys)

        coverage = {}
        for lang in self.SUPPORTED_LANGUAGES:
            translated = 0
            for key in all_keys:
                translation = self._get_translation(key, lang)
                if translation and isinstance(translation, str) and translation.strip():
                    translated += 1
            coverage[lang] = {
                "translated": translated,
                "total": total_keys,
                "percentage": round(translated / total_keys * 100, 1) if total_keys > 0 else 0
            }

        return coverage

    def run_full_check(self, html_path: str = None) -> Dict:
        """전체 검사 실행"""
        self.issues = []

        # 누락된 번역
        missing = self.check_missing_translations()
        self.issues.extend(missing)

        # 빈 번역
        empty = self.check_empty_translations()
        self.issues.extend(empty)

        # 플레이스홀더 불일치
        inconsistencies = self.check_placeholder_consistency()
        self.issues.extend(inconsistencies)

        # HTML 하드코딩 (선택적)
        hardcoded = []
        if html_path:
            hardcoded = self.check_hardcoded_text_in_html(html_path)
            self.issues.extend(hardcoded)

        # 커버리지
        coverage = self.get_translation_coverage()

        # 심각도별 카운트
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            severity_counts[issue["severity"]] += 1

        return {
            "total_issues": len(self.issues),
            "by_severity": severity_counts,
            "by_type": {
                "missing_translation": len(missing),
                "empty_translation": len(empty),
                "placeholder_mismatch": len(inconsistencies),
                "hardcoded_text": len(hardcoded),
            },
            "coverage": coverage,
            "issues": self.issues[:50],  # 상위 50개
            "checked_at": datetime.now().isoformat()
        }

    def suggest_translations(self, key: str, source_lang: str = 'ko') -> Dict:
        """번역 제안 (소스 언어 기반)"""
        source_text = self._get_translation(key, source_lang)
        if not source_text:
            return {"error": "Source translation not found"}

        suggestions = {
            "key": key,
            "source": {
                "language": source_lang,
                "text": source_text
            },
            "missing_languages": []
        }

        for lang in self.SUPPORTED_LANGUAGES:
            if lang != source_lang:
                translation = self._get_translation(key, lang)
                if not translation:
                    suggestions["missing_languages"].append({
                        "language": lang,
                        "suggestion": f"[{lang.upper()}] {source_text}"  # 플레이스홀더
                    })

        return suggestions


if __name__ == '__main__':
    print("=" * 60)
    print("🌍 i18n Checker")
    print("=" * 60)

    checker = I18nChecker()

    # 커버리지 확인
    coverage = checker.get_translation_coverage()
    print(f"\n📊 Translation Coverage:")
    for lang, stats in coverage.items():
        print(f"   {lang.upper()}: {stats['percentage']}% ({stats['translated']}/{stats['total']})")

    # 전체 검사
    results = checker.run_full_check()
    print(f"\n🔍 Check Results:")
    print(f"   Total issues: {results['total_issues']}")
    print(f"   By severity: {results['by_severity']}")
    print(f"   By type: {results['by_type']}")

    # 상위 이슈
    if results['issues']:
        print(f"\n⚠️ Top issues:")
        for issue in results['issues'][:5]:
            print(f"   [{issue['severity']}] {issue['type']}: {issue.get('key', issue.get('text', ''))[:40]}")

    print("\n✅ i18n Check Complete!")
