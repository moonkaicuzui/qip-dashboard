#!/usr/bin/env python3
"""
Automated Backup Cleanup Script for QIP Dashboard System

This script automatically cleans up old backup files and maintains version retention policy.

Usage:
    python scripts/cleanup_backups.py                    # Interactive cleanup
    python scripts/cleanup_backups.py --age 30           # Delete files older than 30 days
    python scripts/cleanup_backups.py --dry-run          # Preview only, no deletion
    python scripts/cleanup_backups.py --keep-latest 2    # Keep only 2 latest versions per month
    python scripts/cleanup_backups.py --auto             # Auto mode (no prompts)

Features:
    - Age-based cleanup (delete files older than N days)
    - Version retention (keep only N latest versions per month)
    - Dry-run mode for safe preview
    - Detailed deletion report
    - Integration with action.sh

Retention Policy:
    - Keep all files from current month
    - Keep latest 2 versions for past 12 months
    - Archive older versions (move to archive/)
    - Delete backup files older than 30 days
"""

import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class BackupCleaner:
    def __init__(self, dry_run: bool = False, auto: bool = False):
        self.dry_run = dry_run
        self.auto = auto
        self.root = Path(__file__).parent.parent
        self.output_dir = self.root / "output_files"
        self.archive_dir = self.output_dir / "archive"
        self.backup_patterns = [
            r".*\.backup\.csv$",
            r".*\.backup_\d{8}_\d{6}\.csv$",
            r".*_backup\.csv$",
            r".*_재계산값_backup\.csv$",
            r".*\.blue_theme_backup$",
            r".*\.color_backup$",
            r".*\.V\d+\.\d+_blue_theme_backup$"
        ]
        self.deleted_files: List[Dict] = []
        self.archived_files: List[Dict] = []
        self.total_space_freed = 0

    def find_backup_files(self, age_days: int = None) -> List[Path]:
        """Find all backup files matching patterns"""
        backup_files = []

        # Search in output_files (excluding archive)
        for pattern in self.backup_patterns:
            for file in self.output_dir.glob("**/*"):
                if file.is_file() and "archive" not in str(file):
                    if re.match(pattern, file.name):
                        backup_files.append(file)

        # Search in root directory for theme backups
        for pattern in self.backup_patterns:
            for file in self.root.glob("*"):
                if file.is_file() and re.match(pattern, file.name):
                    backup_files.append(file)

        # Filter by age if specified
        if age_days:
            cutoff_date = datetime.now() - timedelta(days=age_days)
            backup_files = [
                f for f in backup_files
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_date
            ]

        return backup_files

    def find_version_files(self) -> Dict[str, List[Tuple[Path, str]]]:
        """Find all version files grouped by month"""
        version_pattern = r"output_QIP_incentive_(\w+)_(\d+)_Complete_V(\d+\.\d+)_Complete\.csv"
        version_files = defaultdict(list)

        for file in self.output_dir.glob("*.csv"):
            if file.is_file():
                match = re.match(version_pattern, file.name)
                if match:
                    month, year, version = match.groups()
                    key = f"{month}_{year}"
                    version_files[key].append((file, version))

        # Sort by version number (descending)
        for key in version_files:
            version_files[key].sort(
                key=lambda x: tuple(map(float, x[1].split('.'))),
                reverse=True
            )

        return version_files

    def cleanup_by_age(self, age_days: int):
        """Delete backup files older than specified days"""
        print(f"🔍 Searching for backup files older than {age_days} days...")

        backup_files = self.find_backup_files(age_days)

        if not backup_files:
            print("✅ No old backup files found")
            return

        print(f"\n📋 Found {len(backup_files)} backup file(s) to delete:\n")

        for file in backup_files:
            age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
            size = file.stat().st_size
            print(f"   • {file.relative_to(self.root)}")
            print(f"     Age: {age.days} days, Size: {size:,} bytes")

        if not self.auto and not self.dry_run:
            response = input(f"\n⚠️  Delete {len(backup_files)} file(s)? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Cleanup cancelled")
                return

        # Delete files
        for file in backup_files:
            size = file.stat().st_size
            self.total_space_freed += size

            if not self.dry_run:
                file.unlink()

            self.deleted_files.append({
                'file': str(file.relative_to(self.root)),
                'size': size,
                'age_days': (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
            })

        print(f"\n✅ Deleted {len(backup_files)} backup file(s)")
        print(f"💾 Space freed: {self.total_space_freed:,} bytes ({self.total_space_freed / 1024 / 1024:.2f} MB)")

    def cleanup_by_retention(self, keep_latest: int = 2):
        """Keep only N latest versions per month, archive older ones"""
        print(f"\n🔍 Applying version retention policy (keep {keep_latest} latest per month)...")

        version_files = self.find_version_files()

        if not version_files:
            print("✅ No version files found")
            return

        # Ensure archive directory exists
        if not self.dry_run:
            self.archive_dir.mkdir(exist_ok=True)

        current_month = datetime.now().strftime("%B_%Y").lower()
        files_to_archive = []

        for month_key, files in version_files.items():
            # Skip current month
            if month_key == current_month:
                print(f"\n📅 {month_key.replace('_', ' ').title()}: Keeping all {len(files)} version(s) (current month)")
                continue

            if len(files) <= keep_latest:
                print(f"\n📅 {month_key.replace('_', ' ').title()}: Keeping all {len(files)} version(s)")
                continue

            # Keep latest N, archive the rest
            to_keep = files[:keep_latest]
            to_archive = files[keep_latest:]

            print(f"\n📅 {month_key.replace('_', ' ').title()}:")
            print(f"   ✓ Keeping {len(to_keep)} latest:")
            for file, version in to_keep:
                print(f"      • V{version}: {file.name}")

            print(f"   → Archiving {len(to_archive)} older version(s):")
            for file, version in to_archive:
                size = file.stat().st_size
                print(f"      • V{version}: {file.name} ({size:,} bytes)")
                files_to_archive.append((file, version, size))

        if not files_to_archive:
            print("\n✅ No files need archiving")
            return

        if not self.auto and not self.dry_run:
            response = input(f"\n⚠️  Archive {len(files_to_archive)} file(s)? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Archiving cancelled")
                return

        # Move files to archive
        for file, version, size in files_to_archive:
            dest = self.archive_dir / file.name

            if not self.dry_run:
                file.rename(dest)

            self.archived_files.append({
                'file': file.name,
                'version': version,
                'size': size
            })

        print(f"\n✅ Archived {len(files_to_archive)} file(s) to output_files/archive/")

    def generate_report(self):
        """Generate detailed cleanup report"""
        print("\n" + "="*70)
        print("📊 BACKUP CLEANUP REPORT")
        print("="*70)

        print(f"\n🔢 Summary:")
        print(f"   Mode: {'DRY RUN (Preview Only)' if self.dry_run else 'LIVE CLEANUP'}")
        print(f"   Deleted Files: {len(self.deleted_files)}")
        print(f"   Archived Files: {len(self.archived_files)}")
        print(f"   Total Space Freed: {self.total_space_freed:,} bytes ({self.total_space_freed / 1024 / 1024:.2f} MB)")

        if self.deleted_files:
            print(f"\n🗑️  Deleted Files ({len(self.deleted_files)}):")
            for item in self.deleted_files:
                print(f"   • {item['file']}")
                print(f"     Size: {item['size']:,} bytes, Age: {item['age_days']} days")

        if self.archived_files:
            print(f"\n📦 Archived Files ({len(self.archived_files)}):")
            for item in self.archived_files:
                print(f"   • {item['file']} (V{item['version']})")
                print(f"     Size: {item['size']:,} bytes")

        if not self.deleted_files and not self.archived_files:
            print("\n✅ No cleanup needed - all files are within retention policy")

        print("\n" + "="*70)

        if self.dry_run:
            print("\n💡 Tip: Remove --dry-run flag to apply cleanup")
        else:
            print("\n✅ Cleanup completed successfully!")

    def cleanup_docs_backups(self):
        """Clean up backup files in docs/ directory"""
        docs_dir = self.root / "docs"

        if not docs_dir.exists():
            return

        backup_files = []
        for pattern in self.backup_patterns:
            for file in docs_dir.glob("*"):
                if file.is_file() and re.match(pattern, file.name):
                    backup_files.append(file)

        if backup_files:
            print(f"\n🔍 Found {len(backup_files)} backup file(s) in docs/")

            for file in backup_files:
                size = file.stat().st_size
                print(f"   • {file.name} ({size:,} bytes)")

                if not self.dry_run and (self.auto or input(f"   Delete? (y/n): ").lower() == 'y'):
                    file.unlink()
                    self.deleted_files.append({
                        'file': f"docs/{file.name}",
                        'size': size,
                        'age_days': 0
                    })
                    self.total_space_freed += size
                    print(f"   ✓ Deleted")

    def cleanup_root_backups(self):
        """Clean up backup files in root directory"""
        backup_files = []
        for pattern in self.backup_patterns:
            for file in self.root.glob("*"):
                if file.is_file() and re.match(pattern, file.name):
                    backup_files.append(file)

        if backup_files:
            print(f"\n🔍 Found {len(backup_files)} backup file(s) in root/")

            for file in backup_files:
                size = file.stat().st_size
                print(f"   • {file.name} ({size:,} bytes)")

                if not self.dry_run and (self.auto or input(f"   Delete? (y/n): ").lower() == 'y'):
                    file.unlink()
                    self.deleted_files.append({
                        'file': file.name,
                        'size': size,
                        'age_days': 0
                    })
                    self.total_space_freed += size
                    print(f"   ✓ Deleted")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Backup Cleanup Script for QIP Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cleanup_backups.py                     # Interactive cleanup
  python scripts/cleanup_backups.py --age 30            # Delete files older than 30 days
  python scripts/cleanup_backups.py --keep-latest 2     # Keep only 2 latest versions
  python scripts/cleanup_backups.py --dry-run           # Preview changes only
  python scripts/cleanup_backups.py --auto              # Auto mode (no prompts)
        """
    )

    parser.add_argument('--age', type=int, help='Delete backup files older than N days')
    parser.add_argument('--keep-latest', type=int, default=2, help='Keep N latest versions per month (default: 2)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying them')
    parser.add_argument('--auto', action='store_true', help='Auto mode without prompts')

    args = parser.parse_args()

    cleaner = BackupCleaner(dry_run=args.dry_run, auto=args.auto)

    print("🧹 QIP Dashboard Backup Cleanup Tool")
    print("="*70)

    # Age-based cleanup
    if args.age:
        cleaner.cleanup_by_age(args.age)

    # Version retention cleanup
    cleaner.cleanup_by_retention(args.keep_latest)

    # Clean up other directories
    cleaner.cleanup_docs_backups()
    cleaner.cleanup_root_backups()

    # Generate report
    cleaner.generate_report()

    sys.exit(0)


if __name__ == "__main__":
    main()
