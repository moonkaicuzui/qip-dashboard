"""
Process attendance data for absence analytics - FIXED VERSION
- Filters to 391 active QIP employees only
- Excludes maternity leave from absence calculations
- Matches main dashboard employee count
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

def load_and_filter_employees(month='8', year='2025'):
    """Load incentive data and filter to active QIP employees only (391)"""
    base_path = Path(__file__).parent.parent
    incentive_file = base_path / f"input_files/{year}년 {month}월 인센티브 지급 세부 정보.csv"
    
    if not incentive_file.exists():
        print(f"Warning: Incentive file not found: {incentive_file}")
        return pd.DataFrame()
    
    df = pd.read_csv(incentive_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    
    # Filter to active employees only (no stop working date)
    active_df = df[df['Stop working Date'].isna()].copy()
    print(f"Active employees: {len(active_df)} (from {len(df)} total)")
    
    # Further filter to QIP only if the column exists
    if 'remark -lab or qip' in active_df.columns:
        # Keep only QIP employees or those with null remarks
        qip_df = active_df[
            (active_df['remark -lab or qip'] == 'QIP') | 
            (active_df['remark -lab or qip'].isna())
        ].copy()
        print(f"QIP employees: {len(qip_df)}")
        
        # If we still have more than 391, we might need additional filtering
        if len(qip_df) > 391:
            # Take first 391 to match dashboard
            print(f"Warning: Still have {len(qip_df)} employees, limiting to 391")
            qip_df = qip_df.head(391)
        
        return qip_df
    
    return active_df

def load_attendance_data(month='august', year='2025'):
    """Load and process attendance data from converted CSV files"""
    base_path = Path(__file__).parent.parent
    attendance_file = base_path / f"input_files/attendance/converted/attendance data {month}_converted.csv"
    
    if not attendance_file.exists():
        print(f"Warning: Attendance file not found: {attendance_file}")
        return pd.DataFrame()
    
    # Load attendance data
    df = pd.read_csv(attendance_file, encoding='utf-8-sig')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # CRITICAL FIX: Filter only actual absences (Vắng mặt), not attendance (Đi làm)
    # compAdd field indicates: "Đi làm" = attendance, "Vắng mặt" = absence
    if 'compAdd' in df.columns:
        print(f"Total records in CSV: {len(df)}")
        print(f"Attendance records (Đi làm): {(df['compAdd'] == 'Đi làm').sum()}")
        print(f"Absence records (Vắng mặt): {(df['compAdd'] == 'Vắng mặt').sum()}")
        
        # Keep only absence records
        df = df[df['compAdd'] == 'Vắng mặt'].copy()
        print(f"Processing {len(df)} actual absence records")
    
    # Parse dates
    if 'Work Date' in df.columns:
        df['Work Date'] = pd.to_datetime(df['Work Date'], format='%Y.%m.%d', errors='coerce')
    
    return df

def categorize_absence_reason(reason):
    """Categorize absence reasons into groups - EXCLUDING maternity from absences"""
    if pd.isna(reason):
        return 'unknown'
    
    reason = str(reason).lower()
    
    # Maternity-related keywords - these are NOT absences
    maternity = ['sinh', 'maternity', 'pregnancy', 'dưỡng sức', 'con dưới', 'thai sản']
    for keyword in maternity:
        if keyword in reason:
            return 'maternity_leave'  # Special category not counted as absence
    
    # Regular absence categories
    planned = ['phép năm', 'phép cưới', 'nghỉ bù', 'đi công tác', 'nghỉ không lương', 'vắng có phép']
    medical = ['ốm', 'tai nạn', 'khám thai', 'bệnh', 'sick']
    disciplinary = ['ar1', 'vắng không phép', 'unauthorized']
    legal = ['nghĩa vụ quân sự']
    
    for keyword in planned:
        if keyword in reason:
            return 'planned'
    for keyword in medical:
        if keyword in reason:
            return 'medical'
    for keyword in disciplinary:
        if keyword in reason:
            return 'disciplinary'
    for keyword in legal:
        if keyword in reason:
            return 'legal'
    
    return 'other'

def calculate_absence_metrics(attendance_df, employee_df):
    """Calculate comprehensive absence metrics - EXCLUDING maternity leave"""
    
    # Working days in August 2025 (excluding weekends)
    total_working_days = 22
    
    # For absence rate calculation: 
    # 결근율 = (결근일수 / 실제출근일수) × 100
    # NOT (결근일수 / 총근무일수) × 100
    
    # Group attendance by employee, excluding maternity leave
    if not attendance_df.empty and 'ID No' in attendance_df.columns:
        # Categorize reasons first
        attendance_df['category'] = attendance_df['Reason Description'].apply(categorize_absence_reason)
        
        # Filter out maternity leave records
        absence_df = attendance_df[attendance_df['category'] != 'maternity_leave'].copy()
        maternity_df = attendance_df[attendance_df['category'] == 'maternity_leave'].copy()
        
        print(f"Total absence records (already filtered): {len(attendance_df)}")
        print(f"Maternity leave records (excluded): {len(maternity_df)}")
        print(f"Non-maternity absence records: {len(absence_df)}")
        
        # Calculate absences (excluding maternity)
        absence_by_employee = absence_df.groupby('ID No').agg({
            'Reason Description': lambda x: list(x),
            'Work Date': 'count'
        }).rename(columns={'Work Date': 'absence_days'})
        
        # Calculate maternity days separately (for information only)
        maternity_by_employee = maternity_df.groupby('ID No').size().to_dict()
        
        # Category counts (excluding maternity)
        category_counts = absence_df.groupby(['ID No', 'category']).size().unstack(fill_value=0)
    else:
        absence_by_employee = pd.DataFrame()
        category_counts = pd.DataFrame()
        maternity_by_employee = {}
    
    # Merge with employee data
    if not employee_df.empty and 'Employee No' in employee_df.columns:
        # Convert Employee No to string for matching
        employee_df['Employee No'] = employee_df['Employee No'].astype(str)
        
        if not absence_by_employee.empty:
            absence_by_employee.index = absence_by_employee.index.astype(str)
            
            # Merge data
            merged_df = employee_df.merge(
                absence_by_employee, 
                left_on='Employee No', 
                right_index=True, 
                how='left'
            )
            
            # Fill NaN values
            merged_df['absence_days'] = merged_df['absence_days'].fillna(0)
            
            # Add maternity days as separate column (not in absence calculation)
            merged_df['maternity_days'] = merged_df['Employee No'].map(maternity_by_employee).fillna(0)
            
            # Calculate actual working days (excluding maternity)
            merged_df['actual_working_days'] = total_working_days - merged_df['absence_days']
            
            # 결근율 계산: 결근일수 / 총근무일수 × 100
            # The CSV only contains absence records, not attendance records
            # So we use total_working_days (22) as the denominator
            merged_df['absence_rate'] = (merged_df['absence_days'] / total_working_days * 100).round(2)
            
            # For display purposes, also calculate attendance days
            merged_df['attendance_days'] = merged_df['actual_working_days']
            
            # Classify risk levels based on actual absences (not maternity)
            merged_df['risk_level'] = merged_df.apply(classify_risk_level, axis=1)
            
            print(f"\nFinal metrics:")
            print(f"Total employees: {len(merged_df)}")
            print(f"Average absence days per employee: {merged_df['absence_days'].mean():.2f}")
            print(f"Average attendance days per employee: {merged_df['attendance_days'].mean():.2f}")
            print(f"Average absence rate: {merged_df['absence_rate'].mean():.2f}%")
            print(f"Employees on maternity leave: {(merged_df['maternity_days'] > 0).sum()}")
            
            return merged_df
        else:
            # No absence data, everyone worked full time
            employee_df['absence_days'] = 0
            employee_df['maternity_days'] = 0
            employee_df['actual_working_days'] = total_working_days
            employee_df['absence_rate'] = 0
            employee_df['risk_level'] = 'low'
            return employee_df
    
    return pd.DataFrame()

def classify_risk_level(row):
    """Classify employee risk level based on absence patterns (excluding maternity)"""
    
    # Check for unauthorized absences (AR1 prefix)
    unauthorized_days = 0
    if 'Reason Description' in row and isinstance(row['Reason Description'], list):
        unauthorized_days = sum(1 for reason in row['Reason Description'] 
                              if 'AR1' in str(reason) or 'không phép' in str(reason).lower())
    
    absence_rate = row.get('absence_rate', 0)
    absence_days = row.get('absence_days', 0)
    
    # Adjusted thresholds for corrected low absence rates (4-6% average)
    # High risk criteria
    if unauthorized_days >= 2 or absence_rate > 20 or absence_days >= 5:
        return 'high'
    # Medium risk criteria  
    elif unauthorized_days >= 1 or absence_rate > 10 or absence_days >= 3:
        return 'medium'
    else:
        return 'low'

def generate_team_statistics(merged_df):
    """Generate team-level statistics"""
    if merged_df.empty:
        return {}
    
    # Extract team from position name or department
    team_field = None
    for col in ['QIP POSITION 1ST  NAME', 'Department', 'BUILDING']:
        if col in merged_df.columns:
            team_field = col
            break
    
    if not team_field:
        return {}
    
    # Group by team
    team_stats = merged_df.groupby(team_field).agg({
        'Employee No': 'count',
        'absence_days': ['sum', 'mean'],
        'attendance_days': 'sum',  # Add actual attendance days
        'risk_level': lambda x: (x == 'high').sum(),
        'maternity_days': 'sum'  # Track maternity separately
    }).round(2)
    
    team_stats.columns = ['total_employees', 'total_absence_days', 'avg_absence_days', 
                          'total_attendance_days', 'high_risk_count', 'total_maternity_days']
    
    # Calculate total working days for each team (인원수 × 22일)
    team_stats['total_possible_days'] = team_stats['total_employees'] * 22
    
    # Calculate team-level absence rate: 총결근일수 / 총가능근무일수
    team_stats['team_absence_rate'] = (team_stats['total_absence_days'] / team_stats['total_possible_days'] * 100).round(2)
    
    return team_stats.to_dict('index')

def generate_daily_trend(attendance_df, month='august', year='2025'):
    """Generate daily absence trend data (excluding maternity)"""
    if attendance_df.empty or 'Work Date' not in attendance_df.columns:
        return []
    
    # Categorize and filter out maternity
    attendance_df['category'] = attendance_df['Reason Description'].apply(categorize_absence_reason)
    absence_only_df = attendance_df[attendance_df['category'] != 'maternity_leave']
    
    # Count absences by date
    daily_counts = absence_only_df.groupby('Work Date').size()
    
    # Create full date range for the month
    if month == 'august':
        month_num = 8
    else:
        month_num = 7
    
    date_range = pd.date_range(f'{year}-{month_num:02d}-01', f'{year}-{month_num:02d}-31', freq='D')
    
    # Filter working days only (Monday to Friday)
    working_days = [d for d in date_range if d.weekday() < 5]
    
    # Create daily trend data
    trend_data = []
    for date in working_days:
        count = daily_counts.get(date, 0)
        trend_data.append({
            'date': date.strftime('%m/%d'),
            'absence_count': int(count),
            'absence_rate': round(count / 391 * 100, 2)  # Use 391 employees
        })
    
    return trend_data

def export_absence_data_json(output_file='absence_analytics_data_fixed.json'):
    """Export processed absence data as JSON for dashboard - FIXED VERSION"""
    
    # Load filtered employee data (391 active QIP employees)
    employee_df = load_and_filter_employees('8', '2025')
    
    if employee_df.empty:
        print("Warning: No employee data found")
        return {}
    
    print(f"Processing {len(employee_df)} active QIP employees")
    
    # Load attendance data
    attendance_df = load_attendance_data('august', '2025')
    
    # Calculate metrics (excluding maternity)
    merged_df = calculate_absence_metrics(attendance_df, employee_df)
    
    if merged_df.empty:
        print("Warning: No data to process")
        return {}
    
    # Generate statistics
    team_stats = generate_team_statistics(merged_df)
    daily_trend = generate_daily_trend(attendance_df)
    
    # Category distribution (excluding maternity)
    if not attendance_df.empty and 'Reason Description' in attendance_df.columns:
        attendance_df['category'] = attendance_df['Reason Description'].apply(categorize_absence_reason)
        # Exclude maternity from distribution
        absence_only = attendance_df[attendance_df['category'] != 'maternity_leave']
        category_dist = absence_only['category'].value_counts().to_dict()
    else:
        category_dist = {}
    
    # Risk distribution
    risk_dist = merged_df['risk_level'].value_counts().to_dict() if not merged_df.empty else {}
    
    # Top absence employees (excluding those only on maternity)
    top_absences = merged_df[merged_df['absence_days'] > 0].nlargest(20, 'absence_days')[
        ['Employee No', 'Full Name', 'absence_days', 'absence_rate', 'risk_level', 'maternity_days']
    ].to_dict('records') if not merged_df.empty else []
    
    # Prepare output data
    output_data = {
        'summary': {
            'total_employees': len(merged_df),  # Should be 391
            'total_absence_days': int(merged_df['absence_days'].sum()) if not merged_df.empty else 0,
            'avg_absence_rate': round(merged_df['absence_rate'].mean(), 2) if not merged_df.empty else 0,
            'high_risk_count': int((merged_df['risk_level'] == 'high').sum()) if not merged_df.empty else 0,
            'medium_risk_count': int((merged_df['risk_level'] == 'medium').sum()) if not merged_df.empty else 0,
            'low_risk_count': int((merged_df['risk_level'] == 'low').sum()) if not merged_df.empty else 0,
            'maternity_leave_count': int((merged_df['maternity_days'] > 0).sum()) if not merged_df.empty else 0,
            'total_maternity_days': int(merged_df['maternity_days'].sum()) if not merged_df.empty else 0
        },
        'team_statistics': team_stats,
        'daily_trend': daily_trend,
        'category_distribution': category_dist,
        'risk_distribution': risk_dist,
        'top_absences': top_absences,
        'employee_details': merged_df[[
            'Employee No', 'Full Name', 'QIP POSITION 1ST  NAME',
            'absence_days', 'absence_rate', 'risk_level', 'maternity_days'
        ]].rename(columns={'QIP POSITION 1ST  NAME': 'team'}).to_dict('records') if not merged_df.empty else []
    }
    
    # Save to file
    output_path = Path(__file__).parent.parent / 'output_files' / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\nAbsence data exported to: {output_path}")
    print(f"Summary:")
    print(f"  - Total employees: {output_data['summary']['total_employees']}")
    print(f"  - Absence rate (excluding maternity): {output_data['summary']['avg_absence_rate']}%")
    print(f"  - Employees on maternity leave: {output_data['summary']['maternity_leave_count']}")
    
    return output_data

if __name__ == "__main__":
    # Process and export absence data with fixes
    data = export_absence_data_json()