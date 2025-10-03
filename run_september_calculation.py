#!/usr/bin/env python
"""
Wrapper script to run September 2025 incentive calculation programmatically
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, 'src')

# Import the calculation module
from step1_인센티브_계산_개선버전 import ConfigManager, CompleteDataLoader, CompleteQIPCalculator

def main():
    # Load September config
    config_path = 'config_files/config_september_2025.json'
    print(f'📂 Loading configuration: {config_path}')
    print()

    config = ConfigManager.load_config(config_path)

    print(f'✅ Configuration loaded successfully')
    print(f'   Year: {config.year}')
    print(f'   Month: {config.month.name}')
    print(f'   Working days: {config.working_days}')
    print(f'   Previous months: {[m.name for m in config.previous_months]}')
    print()

    # Verify previous incentive file
    prev_file = config.file_paths.get('previous_incentive')
    if prev_file and os.path.exists(prev_file):
        print(f'✅ Previous incentive file found: {prev_file}')

        # Verify it has correct data
        import pandas as pd
        df = pd.read_csv(prev_file)
        assembly = df[df['QIP POSITION 1ST  NAME'] == 'ASSEMBLY INSPECTOR']
        incentive_col = None
        for col in df.columns:
            if 'august' in col.lower() and 'incentive' in col.lower():
                incentive_col = col
                break

        if incentive_col:
            with_incentive = assembly[assembly[incentive_col] > 0]
            print(f'   ASSEMBLY INSPECTOR with incentive: {len(with_incentive)}')
            print(f'   Total amount: {with_incentive[incentive_col].sum():,.0f} VND')
            print(f'   Amount range: {with_incentive[incentive_col].min():,.0f} - {with_incentive[incentive_col].max():,.0f} VND')
    else:
        print(f'❌ ERROR: Previous incentive file not found: {prev_file}')
        return 1

    print()
    print('=' * 70)
    print('🚀 Starting QIP Incentive Calculation')
    print('=' * 70)
    print()

    # Create data loader and load data
    data_loader = CompleteDataLoader(config)
    data = data_loader.load_all_files()

    # Create calculator with loaded data and config (correct parameter order!)
    calculator = CompleteQIPCalculator(data, config)

    # Run calculation steps
    print('📊 Calculating all incentives...')
    calculator.calculate_all_incentives()

    print('📊 Generating summary...')
    calculator.generate_summary()

    print('💾 Saving results...')
    if calculator.save_results():
        print()
        print('=' * 70)
        print(f'🎉 {config.get_month_str("korean")} incentive calculation completed successfully!')
        print('=' * 70)
    else:
        print('❌ Failed to save results!')
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
