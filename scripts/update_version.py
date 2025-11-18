#!/usr/bin/env python3
"""
Automated Version Update Script for QIP Dashboard System

This script automatically updates version numbers across all project files.

Usage:
    python scripts/update_version.py 9.0 9.1              # Update from 9.0 to 9.1
    python scripts/update_version.py 9.0 9.1 --dry-run    # Preview changes only
    python scripts/update_version.py --rollback           # Rollback last update

Features:
    - Updates 11+ files across the project
    - Dry-run mode for safe preview
    - Automatic backup before changes
    - Rollback capability
    - Validation of all updates
    - Detailed change report

Files Updated (Tier 1 - Core):
    1. src/step1_인센티브_계산_개선버전.py (7 locations)
    2. integrated_dashboard_final.py (8 locations)
    3. action.sh (5 locations)

Files Updated (Tier 2 - Verification):
    4. scripts/verification/validate_incentive_amounts.py
    5. scripts/verification/validate_condition_evaluation.py
    6. scripts/verification/validate_dashboard_consistency.py
    7. scripts/verification/generate_simple_validation_report.py
    8. scripts/verification/analyze_october_data.py
    9. src/update_continuous_fail_column.py

Files Updated (Tier 3 - Documentation):
    10. README.md
    11. CLAUDE.md
"""

import os
import re
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict

class VersionUpdater:
    def __init__(self, old_version: str, new_version: str, dry_run: bool = False):
        self.old_version = old_version
        self.new_version = new_version
        self.dry_run = dry_run
        self.backup_dir = None
        self.changes: List[Dict] = []

        # Project root
        self.root = Path(__file__).parent.parent

        # Files to update (with expected change counts)
        self.files_to_update = {
            # Tier 1 - Core
            "src/step1_인센티브_계산_개선버전.py": {"min_changes": 7, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},
            "integrated_dashboard_final.py": {"min_changes": 8, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
                (rf"Version {re.escape(old_version)}", f"Version {new_version}"),
            ]},
            "action.sh": {"min_changes": 5, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
                (rf"Version {re.escape(old_version)}", f"Version {new_version}"),
            ]},

            # Tier 2 - Verification
            "scripts/verification/validate_incentive_amounts.py": {"min_changes": 1, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},
            "scripts/verification/validate_condition_evaluation.py": {"min_changes": 2, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},
            "scripts/verification/validate_dashboard_consistency.py": {"min_changes": 2, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
                (rf"Version_{re.escape(old_version)}", f"Version_{new_version}"),
            ]},
            "scripts/verification/generate_simple_validation_report.py": {"min_changes": 1, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},
            "scripts/verification/analyze_october_data.py": {"min_changes": 1, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},
            "src/update_continuous_fail_column.py": {"min_changes": 1, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
            ]},

            # Tier 3 - Documentation
            "README.md": {"min_changes": 3, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
                (rf"Version {re.escape(old_version)}", f"Version {new_version}"),
            ]},
            "CLAUDE.md": {"min_changes": 5, "patterns": [
                (rf"V{re.escape(old_version)}", f"V{new_version}"),
                (rf"Version {re.escape(old_version)}", f"Version {new_version}"),
            ]},
        }

    def create_backup(self):
        """Create backup directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.root / "backups" / f"version_update_{self.old_version}_to_{self.new_version}_{timestamp}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"📦 Creating backup in: {self.backup_dir}")

        for file_path in self.files_to_update.keys():
            src = self.root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"   ✓ Backed up: {file_path}")

        # Save metadata
        metadata = self.backup_dir / "metadata.txt"
        with open(metadata, 'w') as f:
            f.write(f"Backup created: {datetime.now()}\n")
            f.write(f"Old version: {self.old_version}\n")
            f.write(f"New version: {self.new_version}\n")
            f.write(f"Files backed up: {len(self.files_to_update)}\n")

        print(f"✅ Backup completed\n")

    def update_file(self, file_path: str, config: Dict) -> int:
        """Update a single file with version changes"""
        full_path = self.root / file_path

        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return 0

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        change_count = 0
        changes_detail = []

        for pattern, replacement in config['patterns']:
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, replacement, content)
                change_count += len(matches)
                changes_detail.append(f"   • Pattern '{pattern}' → '{replacement}': {len(matches)} changes")

        if change_count > 0:
            self.changes.append({
                'file': file_path,
                'count': change_count,
                'details': changes_detail,
                'expected_min': config['min_changes']
            })

            if not self.dry_run:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        return change_count

    def update_all_files(self):
        """Update all files with version changes"""
        print(f"🔄 Updating version: {self.old_version} → {self.new_version}")
        print(f"{'   (DRY RUN - No changes will be made)' if self.dry_run else ''}\n")

        if not self.dry_run:
            self.create_backup()

        total_changes = 0
        warnings = []

        for file_path, config in self.files_to_update.items():
            change_count = self.update_file(file_path, config)
            total_changes += change_count

            status = "✓" if change_count >= config['min_changes'] else "⚠️"
            print(f"{status} {file_path}: {change_count} changes")

            if change_count < config['min_changes']:
                warnings.append(f"   ⚠️  Expected at least {config['min_changes']} changes, found {change_count}")

        return total_changes, warnings

    def generate_report(self, total_changes: int, warnings: List[str]):
        """Generate detailed change report"""
        print("\n" + "="*70)
        print("📊 VERSION UPDATE REPORT")
        print("="*70)

        print(f"\n🔢 Summary:")
        print(f"   Old Version: V{self.old_version}")
        print(f"   New Version: V{self.new_version}")
        print(f"   Files Updated: {len(self.changes)}")
        print(f"   Total Changes: {total_changes}")
        print(f"   Mode: {'DRY RUN (Preview Only)' if self.dry_run else 'LIVE UPDATE'}")

        if self.changes:
            print(f"\n📝 Detailed Changes:")
            for change in self.changes:
                print(f"\n   📄 {change['file']}")
                print(f"      Total changes: {change['count']} (expected min: {change['expected_min']})")
                for detail in change['details']:
                    print(detail)

        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(warning)

        if not self.dry_run and self.backup_dir:
            print(f"\n💾 Backup Location:")
            print(f"   {self.backup_dir}")
            print(f"\n   To rollback: python scripts/update_version.py --rollback")

        print("\n" + "="*70)

        if self.dry_run:
            print("\n💡 Tip: Remove --dry-run flag to apply changes")
        else:
            print("\n✅ Version update completed successfully!")

    def validate_updates(self) -> bool:
        """Validate that all expected updates were made"""
        all_valid = True

        for change in self.changes:
            if change['count'] < change['expected_min']:
                print(f"❌ Validation failed for {change['file']}: "
                      f"Expected {change['expected_min']}, found {change['count']}")
                all_valid = False

        return all_valid


def rollback_last_update():
    """Rollback to the most recent backup"""
    backup_root = Path(__file__).parent.parent / "backups"

    if not backup_root.exists():
        print("❌ No backups found")
        return

    # Find most recent backup
    backups = sorted(backup_root.glob("version_update_*"), key=os.path.getmtime, reverse=True)

    if not backups:
        print("❌ No version update backups found")
        return

    latest_backup = backups[0]

    print(f"🔄 Rolling back from: {latest_backup.name}")

    # Read metadata
    metadata_file = latest_backup / "metadata.txt"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            print(f"\n📋 Backup Info:")
            print(f.read())

    response = input("\n⚠️  Are you sure you want to rollback? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Rollback cancelled")
        return

    # Restore files
    project_root = Path(__file__).parent.parent
    files_restored = 0

    for backup_file in latest_backup.rglob("*"):
        if backup_file.is_file() and backup_file.name != "metadata.txt":
            relative_path = backup_file.relative_to(latest_backup)
            target = project_root / relative_path

            shutil.copy2(backup_file, target)
            print(f"   ✓ Restored: {relative_path}")
            files_restored += 1

    print(f"\n✅ Rollback completed! Restored {files_restored} files")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Version Update Script for QIP Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_version.py 9.0 9.1              # Update from 9.0 to 9.1
  python scripts/update_version.py 9.0 9.1 --dry-run    # Preview changes only
  python scripts/update_version.py --rollback           # Rollback last update
        """
    )

    parser.add_argument('old_version', nargs='?', help='Current version (e.g., 9.0)')
    parser.add_argument('new_version', nargs='?', help='New version (e.g., 9.1)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying them')
    parser.add_argument('--rollback', action='store_true', help='Rollback to most recent backup')

    args = parser.parse_args()

    if args.rollback:
        rollback_last_update()
        return

    if not args.old_version or not args.new_version:
        parser.print_help()
        sys.exit(1)

    # Validate version format
    version_pattern = r'^\d+\.\d+$'
    if not re.match(version_pattern, args.old_version) or not re.match(version_pattern, args.new_version):
        print("❌ Error: Version must be in format X.Y (e.g., 9.0, 9.1)")
        sys.exit(1)

    # Run updater
    updater = VersionUpdater(args.old_version, args.new_version, args.dry_run)
    total_changes, warnings = updater.update_all_files()
    updater.generate_report(total_changes, warnings)

    # Validate if not dry run
    if not args.dry_run:
        if not updater.validate_updates():
            print("\n⚠️  Some files did not receive expected number of updates")
            print("   Please review the warnings above")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
