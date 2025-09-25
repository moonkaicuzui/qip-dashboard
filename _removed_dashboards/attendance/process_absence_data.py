"""
Process attendance data for absence analytics
Combines attendance CSV with incentive data for real absence metrics
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

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
    
    # Parse dates
    if 'Work Date' in df.columns:
        df['Work Date'] = pd.to_datetime(df['Work Date'], format='%Y.%m.%d', errors='coerce')
    
    return df

def load_incentive_data(month='8', year='2025'):
    """Load incentive data with employee information"""
    base_path = Path(__file__).parent.parent
    incentive_file = base_path / f"input_files/{year}년 {month}월 인센티브 지급 세부 정보.csv"
    
    if not incentive_file.exists():
        print(f"Warning: Incentive file not found: {incentive_file}")
        return pd.DataFrame()
    
    df = pd.read_csv(incentive_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    
    return df

def categorize_absence_reason(reason):
    """Categorize absence reasons into groups"""
    if pd.isna(reason):
        return 'unknown'
    
    reason = str(reason).lower()
    
    # Based on config_files/absence_analytics_config.json categories
    planned = ['phép năm', 'phép cưới', 'nghỉ bù', 'đi công tác', 'nghỉ không lương', 'vắng có phép']
    maternity = ['sinh thường', 'dưỡng sức', 'con dưới 3 tuổi']
    medical = ['ốm', 'tai nạn', 'khám thai']
    disciplinary = ['ar1', 'vắng không phép']
    legal = ['nghĩa vụ quân sự']
    
    for keyword in planned:
        if keyword in reason:
            return 'planned'
    for keyword in maternity:
        if keyword in reason:
            return 'maternity'
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

def calculate_absence_metrics(attendance_df, incentive_df):
    """Calculate comprehensive absence metrics"""
    
    # Working days in August 2025 (excluding weekends)
    total_working_days = 22
    
    # Group attendance by employee
    if not attendance_df.empty and 'ID No' in attendance_df.columns:
        absence_by_employee = attendance_df.groupby('ID No').agg({
            'Reason Description': lambda x: list(x),
            'Work Date': 'count'
        }).rename(columns={'Work Date': 'absence_days'})
        
        # Calculate absence reasons summary
        attendance_df['category'] = attendance_df['Reason Description'].apply(categorize_absence_reason)
        category_counts = attendance_df.groupby(['ID No', 'category']).size().unstack(fill_value=0)
    else:
        absence_by_employee = pd.DataFrame()
        category_counts = pd.DataFrame()
    
    # Merge with incentive data
    if not incentive_df.empty and 'Employee No' in incentive_df.columns:
        # Convert Employee No to string for matching
        incentive_df['Employee No'] = incentive_df['Employee No'].astype(str)
        
        if not absence_by_employee.empty:
            absence_by_employee.index = absence_by_employee.index.astype(str)
            
            # Merge data
            merged_df = incentive_df.merge(
                absence_by_employee, 
                left_on='Employee No', 
                right_index=True, 
                how='left'
            )
            
            # Fill NaN values
            merged_df['absence_days'] = merged_df['absence_days'].fillna(0)
            
            # Calculate actual working days
            merged_df['actual_working_days'] = total_working_days - merged_df['absence_days']
            merged_df['absence_rate'] = (merged_df['absence_days'] / total_working_days * 100).round(2)
            
            # Classify risk levels
            merged_df['risk_level'] = merged_df.apply(classify_risk_level, axis=1)
            
            return merged_df
        else:
            # No absence data, everyone worked full time
            incentive_df['absence_days'] = 0
            incentive_df['actual_working_days'] = total_working_days
            incentive_df['absence_rate'] = 0
            incentive_df['risk_level'] = 'low'
            return incentive_df
    
    return pd.DataFrame()

def classify_risk_level(row):
    """Classify employee risk level based on absence patterns"""
    # Based on config_files/absence_analytics_config.json risk criteria
    
    # Check for unauthorized absences (AR1 prefix)
    unauthorized_days = 0
    if 'Reason Description' in row and isinstance(row['Reason Description'], list):
        unauthorized_days = sum(1 for reason in row['Reason Description'] if 'AR1' in str(reason))
    
    absence_rate = row.get('absence_rate', 0)
    absence_days = row.get('absence_days', 0)
    
    # High risk criteria
    if unauthorized_days >= 3 or absence_rate > 20 or absence_days >= 10:
        return 'high'
    # Medium risk criteria
    elif unauthorized_days >= 1 or absence_rate > 10 or absence_days >= 5:
        return 'medium'
    else:
        return 'low'

def generate_team_statistics(merged_df):
    """Generate team-level statistics"""
    if merged_df.empty:
        return {}
    
    # Extract team from position name or department
    # Using QIP POSITION 1ST NAME or similar field
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
        'absence_rate': 'mean',
        'risk_level': lambda x: (x == 'high').sum()
    }).round(2)
    
    team_stats.columns = ['total_employees', 'total_absence_days', 'avg_absence_days', 'avg_absence_rate', 'high_risk_count']
    
    return team_stats.to_dict('index')

def generate_daily_trend(attendance_df, month='august', year='2025'):
    """Generate daily absence trend data"""
    if attendance_df.empty or 'Work Date' not in attendance_df.columns:
        return []
    
    # Count absences by date
    daily_counts = attendance_df.groupby('Work Date').size()
    
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
            'absence_rate': round(count / 2340 * 100, 2)  # Assuming ~2340 total employees
        })
    
    return trend_data

def export_absence_data_json(output_file='absence_analytics_data.json'):
    """Export processed absence data as JSON for dashboard"""
    
    # Load data
    attendance_df = load_attendance_data('august', '2025')
    incentive_df = load_incentive_data('8', '2025')
    
    # Calculate metrics
    merged_df = calculate_absence_metrics(attendance_df, incentive_df)
    
    if merged_df.empty:
        print("Warning: No data to process")
        return {}
    
    # Generate statistics
    team_stats = generate_team_statistics(merged_df)
    daily_trend = generate_daily_trend(attendance_df)
    
    # Category distribution
    if not attendance_df.empty and 'Reason Description' in attendance_df.columns:
        attendance_df['category'] = attendance_df['Reason Description'].apply(categorize_absence_reason)
        category_dist = attendance_df['category'].value_counts().to_dict()
    else:
        category_dist = {}
    
    # Risk distribution
    risk_dist = merged_df['risk_level'].value_counts().to_dict() if not merged_df.empty else {}
    
    # Top absence employees
    top_absences = merged_df.nlargest(20, 'absence_days')[
        ['Employee No', 'Full Name', 'absence_days', 'absence_rate', 'risk_level']
    ].to_dict('records') if not merged_df.empty else []
    
    # Prepare output data
    output_data = {
        'summary': {
            'total_employees': len(merged_df),
            'total_absence_days': int(merged_df['absence_days'].sum()) if not merged_df.empty else 0,
            'avg_absence_rate': round(merged_df['absence_rate'].mean(), 2) if not merged_df.empty else 0,
            'high_risk_count': int((merged_df['risk_level'] == 'high').sum()) if not merged_df.empty else 0,
            'medium_risk_count': int((merged_df['risk_level'] == 'medium').sum()) if not merged_df.empty else 0,
            'low_risk_count': int((merged_df['risk_level'] == 'low').sum()) if not merged_df.empty else 0
        },
        'team_statistics': team_stats,
        'daily_trend': daily_trend,
        'category_distribution': category_dist,
        'risk_distribution': risk_dist,
        'top_absences': top_absences,
        'employee_details': merged_df[[
            'Employee No', 'Full Name', 'absence_days', 'absence_rate', 'risk_level'
        ]].to_dict('records') if not merged_df.empty else []
    }
    
    # Save to file
    output_path = Path(__file__).parent.parent / 'output_files' / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"Absence data exported to: {output_path}")
    return output_data

if __name__ == "__main__":
    # Process and export absence data
    data = export_absence_data_json()
    
    # Print summary
    if data:
        print("\n=== Absence Analytics Summary ===")
        print(f"Total Employees: {data['summary']['total_employees']}")
        print(f"Total Absence Days: {data['summary']['total_absence_days']}")
        print(f"Average Absence Rate: {data['summary']['avg_absence_rate']}%")
        print(f"High Risk: {data['summary']['high_risk_count']}")
        print(f"Medium Risk: {data['summary']['medium_risk_count']}")
        print(f"Low Risk: {data['summary']['low_risk_count']}")