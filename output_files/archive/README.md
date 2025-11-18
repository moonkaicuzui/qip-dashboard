# Archive Folder - Version History

This folder contains archived versions of incentive calculation output files.

## Archive Policy

- **Current Files**: Parent directory contains ONLY the latest version for each month
- **Archived Files**: This directory contains all previous versions for historical reference
- **Retention**: Files are kept indefinitely for audit and rollback purposes

## Current Active Versions (Parent Directory)

| Month | Version | File Size | Purpose |
|-------|---------|-----------|---------|
| September 2025 | V9.0 | 253K | Latest calculation with correct logic |
| October 2025 | V9.1 | 249K | Uses October_Incentive column from Excel |
| November 2025 | V9.0 | 287K | Current month calculation |

## Version History

### V9.1 (2025-11-18)
- **Critical Fix**: Previous_Incentive column uses October_Incentive from Excel source
- **Applied To**: October 2025
- **Files**: Generated from `2025 october completed final incentive amount data.xlsx`

### V9.0 (2025-11-18)
- **Feature**: Red theme implementation
- **Feature**: TYPE-2 GROUP LEADER calculation logic change (LINE LEADER avg × 2)
- **Applied To**: September, October, November 2025

### V8.02 (2025-11-10)
- **Feature**: Enhanced dashboard functionality
- **Bug**: Previous_Incentive used Source_Final_Incentive (incorrect backup value)
- **Status**: Superseded by V9.1

### V8.01 (2025-10-11)
- **Initial**: First stable version with complete 10-condition system
- **Status**: Superseded by V8.02

## File Naming Convention

```
output_QIP_incentive_{month}_{year}_Complete_V{major}.{minor}_Complete.csv
```

Example: `output_QIP_incentive_october_2025_Complete_V9.1_Complete.csv`

## Restoration Instructions

If you need to restore an archived version:

1. Identify the target version from this directory
2. Copy (DO NOT MOVE) the file to parent directory
3. Update corresponding config file: `config_files/config_{month}_{year}.json`
4. Regenerate downstream data if necessary

## Backup Files

Backup files with timestamps (e.g., `*.backup_YYYYMMDD_HHMMSS.csv`) are temporary snapshots created during development. These can be safely deleted after 30 days.

---

**Last Updated**: 2025-11-18
**Maintained By**: QIP Dashboard System
