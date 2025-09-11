#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import json
import shutil
from datetime import datetime

def load_5prs_data():
    """Load and merge all 5PRS CSV files"""
    data_frames = []
    input_dir = 'input_files'
    
    # Find all 5PRS files
    files = [f for f in os.listdir(input_dir) if '5prs' in f.lower() and f.endswith('.csv')]
    
    for file in sorted(files):
        filepath = os.path.join(input_dir, file)
        print(f"Loading: {file}")
        df = pd.read_csv(filepath)
        data_frames.append(df)
    
    # Combine all data
    all_data = pd.concat(data_frames, ignore_index=True)
    
    # Convert datetime columns to string for JSON serialization
    date_columns = ['Inspection Date', 'Date']
    for col in date_columns:
        if col in all_data.columns:
            all_data[col] = all_data[col].astype(str)
    
    # Fill NaN values with empty strings
    all_data = all_data.fillna('')
    
    return all_data, len(files)

def create_embedded_dashboard():
    """Create a standalone dashboard with embedded data using original UI"""
    
    # Load the data
    data, files_count = load_5prs_data()
    
    # Convert to JSON
    records = data.to_dict('records')
    
    # Calculate summary
    summary = {
        'total_records': len(data),
        'unique_inspectors': data['Inspector Name'].nunique() if 'Inspector Name' in data.columns else 0,
        'files_processed': files_count,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Copy the entire 5PRS DASHBOARD folder
    source_dir = '5PRS DASHBOARD'
    target_dir = '5PRS_DASHBOARD_EMBEDDED'
    
    # Remove target directory if it exists
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    # Copy the directory
    shutil.copytree(source_dir, target_dir)
    print(f"✅ Copied {source_dir} to {target_dir}")
    
    # Create a modified fileHandler.js that uses embedded data
    file_handler_content = '''// Embedded Data File Handler for 5PRS Dashboard
import { updateCharts } from './charts.js';
import { updateTables } from './tables.js';
import { updateStats } from './stats.js';
import { translations } from './config.js';

// Embedded data
const embeddedData = ''' + json.dumps(records, ensure_ascii=False) + ''';
const embeddedSummary = ''' + json.dumps(summary, ensure_ascii=False) + ''';

let allData = [];
let filteredData = [];
export let currentLanguage = 'ko';

// Export data getters
export const getAllData = () => allData;
export const getFilteredData = () => filteredData;

// Set language
export function setLanguage(lang) {
    currentLanguage = lang;
}

// Initialize file handler
export function initFileHandler() {
    console.log('Initializing embedded data handler...');
    
    // Add automatic data loading on page load
    setTimeout(() => {
        loadEmbeddedData();
    }, 500);
}

// Load embedded data
function loadEmbeddedData() {
    console.log('Loading embedded data...');
    console.log(`Total records: ${embeddedData.length}`);
    
    try {
        // Process embedded data
        allData = processData(embeddedData);
        filteredData = [...allData];
        
        console.log('Data loaded successfully:', allData.length, 'records');
        
        // Update UI
        updateUIWithData();
        
        // Show success message
        showDataLoadedMessage();
        
    } catch (error) {
        console.error('Error loading embedded data:', error);
        showError('데이터 로드 중 오류가 발생했습니다: ' + error.message);
    }
}

// Process raw data
function processData(rawData) {
    return rawData.map(row => {
        // Parse date
        let date = null;
        if (row['Inspection Date']) {
            date = new Date(row['Inspection Date']);
        } else if (row['Date']) {
            date = new Date(row['Date']);
        }
        
        // Determine pass/fail
        const rejectColumns = Object.keys(row).filter(key => 
            key.toLowerCase().includes('reject') || 
            key.toLowerCase().includes('defect') ||
            key.toLowerCase().includes('missing')
        );
        
        let isReject = false;
        let defectType = '';
        
        for (const col of rejectColumns) {
            if (row[col] && row[col] !== '' && row[col] !== '0' && row[col] !== 0) {
                isReject = true;
                defectType = col.replace('Reject', '').replace('Defect', '').replace('Missing', '').trim();
                break;
            }
        }
        
        return {
            date: date,
            dateStr: date ? date.toISOString().split('T')[0] : '',
            tqcId: row['TQC ID'] || row['Inspector ID'] || '',
            tqcName: row['TQC Name'] || row['Inspector Name'] || '',
            building: row['Building'] || '',
            line: row['Line'] || '',
            model: row['Model'] || '',
            poNo: row['PO No'] || '',
            poItem: row['PO Item'] || '',
            totalQty: 1,
            rejectQty: isReject ? 1 : 0,
            passQty: isReject ? 0 : 1,
            defectType: defectType,
            shift: row['Shift'] || determineShift(row['Time'] || ''),
            time: row['Time'] || '',
            ...row
        };
    });
}

// Determine shift from time
function determineShift(time) {
    if (!time) return 'Unknown';
    const hour = parseInt(time.split(':')[0]);
    if (hour >= 6 && hour < 14) return 'Morning';
    if (hour >= 14 && hour < 22) return 'Afternoon';
    return 'Night';
}

// Update UI with data
function updateUIWithData() {
    // Hide upload section
    const uploadSection = document.getElementById('uploadSection');
    if (uploadSection) {
        uploadSection.style.display = 'none';
    }
    
    // Show dashboard section
    const dashboardSection = document.getElementById('dashboardSection');
    if (dashboardSection) {
        dashboardSection.style.display = 'block';
    }
    
    // Update all components
    updateStats(filteredData);
    updateCharts(filteredData);
    updateTables(filteredData);
    
    // Update summary info
    if (embeddedSummary) {
        const totalValidationEl = document.getElementById('totalValidation');
        if (totalValidationEl) {
            totalValidationEl.textContent = embeddedSummary.total_records.toLocaleString();
        }
    }
}

// Show data loaded message
function showDataLoadedMessage() {
    console.log(`✅ Data loaded: ${embeddedSummary.total_records} records from ${embeddedSummary.files_processed} files`);
    
    // You can add a visual notification here if needed
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            <span>데이터 로드 완료: ${embeddedSummary.total_records.toLocaleString()}개 레코드</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Show error message
function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    const errorText = document.getElementById('errorText');
    
    if (errorContainer && errorText) {
        errorText.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        console.error(message);
    }
    
    // Also update upload section
    const uploadText = document.querySelector('.upload-text');
    const uploadSubtext = document.querySelector('.upload-subtext');
    
    if (uploadText) {
        uploadText.textContent = '데이터를 불러올 수 없습니다';
        uploadText.setAttribute('data-lang', 'loadError');
    }
    
    if (uploadSubtext) {
        uploadSubtext.textContent = message;
        uploadSubtext.style.color = '#ef4444';
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export functions that might be needed by other modules
export { loadEmbeddedData };
'''
    
    # Write the modified fileHandler.js
    file_handler_path = os.path.join(target_dir, 'js', 'fileHandler.js')
    with open(file_handler_path, 'w', encoding='utf-8') as f:
        f.write(file_handler_content)
    print(f"✅ Created embedded fileHandler.js")
    
    # Update the index.html title to indicate it's embedded version
    index_path = os.path.join(target_dir, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update title
    html_content = html_content.replace(
        '<title>5PRS Quality Dashboard</title>',
        '<title>5PRS Quality Dashboard - Embedded Data</title>'
    )
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Embedded dashboard created in: {target_dir}")
    print(f"📊 Total records embedded: {len(records)}")
    print(f"📁 Files processed: {files_count}")
    print(f"🚀 Open {target_dir}/index.html in your browser!")
    print(f"\n💡 This version uses the original UI/UX with embedded data")
    print(f"   No server required - works offline!")
    
    return target_dir

if __name__ == "__main__":
    create_embedded_dashboard()