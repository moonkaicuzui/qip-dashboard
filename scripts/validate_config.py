#!/usr/bin/env python3
"""
Config Validation System for QIP Dashboard

This script validates monthly configuration files to prevent runtime errors.

Usage:
    python scripts/validate_config.py november 2025      # Validate specific month
    python scripts/validate_config.py --all              # Validate all configs
    python scripts/validate_config.py --generate november 2025  # Generate config and validate

Features:
    - Required field validation
    - File path existence checks
    - Version consistency validation
    - Previous incentive file verification
    - Working days sanity checks
    - Comprehensive error reporting

Exit Codes:
    0 - All validation checks passed
    1 - Validation errors found
    2 - Config file not found
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class ConfigValidator:
    def __init__(self, month: str, year: int):
        self.month = month.lower()
        self.year = year
        self.root = Path(__file__).parent.parent
        self.config_file = self.root / f"config_files/config_{self.month}_{self.year}.json"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def load_config(self) -> Dict:
        """Load and parse config file"""
        if not self.config_file.exists():
            print(f"❌ Config file not found: {self.config_file}")
            sys.exit(2)

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            sys.exit(2)

    def validate_required_fields(self, config: Dict) -> bool:
        """Validate that all required fields exist"""
        required_fields = [
            'year',
            'month',
            'working_days',
            'previous_months',
            'file_paths',
            'output_prefix'
        ]

        missing_fields = [f for f in required_fields if f not in config]

        if missing_fields:
            self.errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            return False

        # Validate file_paths structure
        required_paths = [
            'basic_manpower',
            'attendance',
            '5prs',
            'aql_current',
            'previous_incentive'
        ]

        if 'file_paths' not in config:
            self.errors.append("Missing 'file_paths' section")
            return False

        missing_paths = [p for p in required_paths if p not in config['file_paths']]

        if missing_paths:
            self.errors.append(f"Missing file paths: {', '.join(missing_paths)}")
            return False

        return True

    def validate_basic_values(self, config: Dict) -> bool:
        """Validate basic config values"""
        all_valid = True

        # Validate year
        if config['year'] != self.year:
            self.errors.append(f"Year mismatch: Config has {config['year']}, expected {self.year}")
            all_valid = False

        # Validate month
        if config['month'] != self.month:
            self.errors.append(f"Month mismatch: Config has {config['month']}, expected {self.month}")
            all_valid = False

        # Validate working days
        working_days = config.get('working_days', 0)
        if working_days < 0 or working_days > 31:
            self.errors.append(f"Invalid working_days: {working_days} (must be 0-31)")
            all_valid = False
        elif working_days == 0:
            self.warnings.append("working_days is 0 - will be calculated from attendance data")

        return all_valid

    def validate_file_paths(self, config: Dict) -> bool:
        """Validate that all file paths exist"""
        all_valid = True
        file_paths = config.get('file_paths', {})

        for key, path in file_paths.items():
            full_path = self.root / path

            if not full_path.exists():
                # Special case: previous_incentive might be from previous run
                if key == 'previous_incentive':
                    # Check if any version of the file exists
                    pattern = path.replace('V9.1', 'V*').replace('V9.0', 'V*').replace('V8.02', 'V*')
                    possible_files = list(self.root.glob(pattern))

                    if possible_files:
                        latest_file = max(possible_files, key=lambda f: f.stat().st_mtime)
                        self.warnings.append(
                            f"Previous incentive file not found: {path}\n"
                            f"      → Latest available: {latest_file.relative_to(self.root)}"
                        )
                    else:
                        self.errors.append(f"File not found ({key}): {path}")
                        all_valid = False
                else:
                    self.errors.append(f"File not found ({key}): {path}")
                    all_valid = False
            else:
                # File exists, check if it's empty
                if full_path.stat().st_size == 0:
                    self.warnings.append(f"Empty file ({key}): {path}")
                else:
                    self.info.append(f"✓ {key}: {path} ({full_path.stat().st_size:,} bytes)")

        return all_valid

    def validate_previous_incentive(self, config: Dict) -> bool:
        """Validate previous incentive file specifics"""
        all_valid = True

        prev_incentive_path = config.get('file_paths', {}).get('previous_incentive', '')

        if not prev_incentive_path:
            self.errors.append("previous_incentive path not specified")
            return False

        # Extract version from path
        import re
        version_match = re.search(r'V(\d+\.\d+)', prev_incentive_path)

        if not version_match:
            self.errors.append(f"Previous incentive file missing version number: {prev_incentive_path}")
            all_valid = False
        else:
            version = version_match.group(1)

            # Check if using old version
            current_version = "9.0"  # Update this when version changes
            try:
                version_float = float(version)
                current_float = float(current_version)

                if version_float < current_float - 0.5:
                    self.warnings.append(
                        f"Previous incentive using old version: V{version}\n"
                        f"      → Current version: V{current_version}\n"
                        f"      → Consider updating config to use latest version"
                    )
            except ValueError:
                pass

        # Check if file is in archive (should not be)
        if 'archive' in prev_incentive_path:
            self.errors.append(
                f"Previous incentive points to archived file: {prev_incentive_path}\n"
                f"      → Should point to current file in output_files/"
            )
            all_valid = False

        return all_valid

    def validate_output_prefix(self, config: Dict) -> bool:
        """Validate output prefix format"""
        output_prefix = config.get('output_prefix', '')

        expected_prefix = f"output_QIP_incentive_{self.month}_{self.year}"

        if output_prefix != expected_prefix:
            self.warnings.append(
                f"Output prefix mismatch:\n"
                f"      Expected: {expected_prefix}\n"
                f"      Got: {output_prefix}"
            )
            return False

        return True

    def validate_previous_months(self, config: Dict) -> bool:
        """Validate previous_months list"""
        previous_months = config.get('previous_months', [])

        if not previous_months or len(previous_months) < 2:
            self.warnings.append(
                f"previous_months should contain at least 2 months, got {len(previous_months)}"
            )
            return False

        # Check if previous months are sequential
        month_order = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]

        try:
            current_idx = month_order.index(self.month)
            expected_prev = [
                month_order[(current_idx - 2) % 12],
                month_order[(current_idx - 1) % 12]
            ]

            if previous_months != expected_prev:
                self.info.append(
                    f"Note: previous_months = {previous_months}\n"
                    f"      Expected based on current month: {expected_prev}"
                )
        except ValueError:
            pass

        return True

    def validate_all(self) -> Tuple[bool, Dict]:
        """Run all validation checks"""
        print(f"🔍 Validating config: {self.month} {self.year}")
        print(f"📄 Config file: {self.config_file.relative_to(self.root)}\n")

        config = self.load_config()

        # Run all validation checks
        checks = [
            ("Required Fields", self.validate_required_fields),
            ("Basic Values", self.validate_basic_values),
            ("File Paths", self.validate_file_paths),
            ("Previous Incentive", self.validate_previous_incentive),
            ("Output Prefix", self.validate_output_prefix),
            ("Previous Months", self.validate_previous_months)
        ]

        results = {}
        for check_name, check_func in checks:
            try:
                result = check_func(config)
                results[check_name] = result
            except Exception as e:
                self.errors.append(f"{check_name} check failed: {str(e)}")
                results[check_name] = False

        # Generate report
        self.generate_report(results)

        return len(self.errors) == 0, results

    def generate_report(self, results: Dict):
        """Generate validation report"""
        print("="*70)
        print("📊 VALIDATION REPORT")
        print("="*70)

        # Check results summary
        print(f"\n✅ Validation Checks:")
        for check_name, result in results.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check_name}")

        # Errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        # Info
        if self.info:
            print(f"\nℹ️  Information:")
            for info in self.info:
                print(f"   {info}")

        print("\n" + "="*70)

        # Final verdict
        if self.errors:
            print("\n❌ Validation FAILED - Please fix errors above")
            print("   Config cannot be used for calculation")
        elif self.warnings:
            print("\n⚠️  Validation PASSED with warnings")
            print("   Config can be used but review warnings")
        else:
            print("\n✅ Validation PASSED - Config is ready to use")


def validate_all_configs(root: Path):
    """Validate all config files"""
    config_dir = root / "config_files"
    config_files = list(config_dir.glob("config_*_*.json"))

    if not config_files:
        print("❌ No config files found")
        sys.exit(1)

    print(f"🔍 Found {len(config_files)} config file(s) to validate\n")

    results = {}
    for config_file in sorted(config_files):
        # Extract month and year from filename
        import re
        match = re.match(r'config_(\w+)_(\d+)\.json', config_file.name)
        if not match:
            continue

        month, year = match.groups()
        validator = ConfigValidator(month, int(year))
        valid, check_results = validator.validate_all()
        results[f"{month}_{year}"] = valid

        print("\n")

    # Summary
    print("="*70)
    print("📊 ALL CONFIGS SUMMARY")
    print("="*70)

    for config_name, valid in results.items():
        status = "✓" if valid else "✗"
        print(f"   {status} {config_name.replace('_', ' ').title()}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n   Total: {passed}/{total} passed")

    if passed < total:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Config Validation System for QIP Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('month', nargs='?', help='Month name (e.g., november)')
    parser.add_argument('year', nargs='?', type=int, help='Year (e.g., 2025)')
    parser.add_argument('--all', action='store_true', help='Validate all config files')
    parser.add_argument('--generate', action='store_true', help='Generate config before validating')

    args = parser.parse_args()

    root = Path(__file__).parent.parent

    if args.all:
        validate_all_configs(root)
        sys.exit(0)

    if not args.month or not args.year:
        parser.print_help()
        sys.exit(1)

    # Generate config if requested
    if args.generate:
        print(f"🔧 Generating config for {args.month} {args.year}...")
        import subprocess
        result = subprocess.run(
            ['python3', 'src/step0_create_monthly_config.py', args.month, str(args.year)],
            cwd=root,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Config generation failed:\n{result.stderr}")
            sys.exit(1)
        print(f"✅ Config generated\n")

    # Validate
    validator = ConfigValidator(args.month, args.year)
    valid, results = validator.validate_all()

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
