#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import json
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

def create_standalone_html():
    """Create a standalone HTML file with embedded data"""
    
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
    
    # Create the HTML
    html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5PRS Quality Dashboard - Standalone</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .label {
            color: #999;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            color: #333;
            font-size: 2em;
            font-weight: bold;
        }
        
        .stat-card.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .stat-card.primary .label {
            color: rgba(255,255,255,0.8);
        }
        
        .stat-card.primary .value {
            color: white;
        }
        
        .data-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .data-section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .data-table th {
            background: #f8f9fa;
            color: #333;
            font-weight: 600;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #dee2e6;
        }
        
        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .search-box {
            margin-bottom: 20px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 50px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .info-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }
        
        .loading-message {
            display: none;
        }
        
        .pagination {
            margin-top: 20px;
            text-align: center;
        }
        
        .pagination button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .pagination button:hover {
            background: #764ba2;
        }
        
        .pagination button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .pagination span {
            margin: 0 10px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>5PRS Quality Dashboard</h1>
            <div class="subtitle">
                실시간 품질 데이터 분석
                <span class="info-badge">데이터 로드 완료</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="label">총 검사 기록</div>
                <div class="value" id="totalRecords">0</div>
            </div>
            <div class="stat-card">
                <div class="label">검사원 수</div>
                <div class="value" id="totalInspectors">0</div>
            </div>
            <div class="stat-card">
                <div class="label">처리된 파일</div>
                <div class="value" id="filesProcessed">0</div>
            </div>
            <div class="stat-card">
                <div class="label">마지막 업데이트</div>
                <div class="value" id="lastUpdate" style="font-size: 1.2em;">-</div>
            </div>
        </div>
        
        <div class="data-section">
            <h2>검사 데이터</h2>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="검색... (이름, 모델, 건물 등)">
            </div>
            <div id="tableContainer">
                <table class="data-table" id="dataTable">
                    <thead>
                        <tr id="tableHeader"></tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
            <div class="pagination">
                <button id="prevBtn" onclick="prevPage()">이전</button>
                <span id="pageInfo">1 / 1</span>
                <button id="nextBtn" onclick="nextPage()">다음</button>
            </div>
        </div>
    </div>
    
    <script>
        // Embedded data
        const embeddedData = ''' + json.dumps(records, ensure_ascii=False) + ''';
        const summary = ''' + json.dumps(summary, ensure_ascii=False) + ''';
        
        // Global variables
        let currentPage = 1;
        const rowsPerPage = 20;
        let filteredData = [...embeddedData];
        
        // Initialize dashboard
        function initDashboard() {
            // Update summary statistics
            document.getElementById('totalRecords').textContent = summary.total_records.toLocaleString();
            document.getElementById('totalInspectors').textContent = summary.unique_inspectors.toLocaleString();
            document.getElementById('filesProcessed').textContent = summary.files_processed;
            document.getElementById('lastUpdate').textContent = summary.last_update;
            
            // Create table headers
            if (embeddedData.length > 0) {
                const headers = Object.keys(embeddedData[0]).slice(0, 10); // Show first 10 columns
                const headerRow = document.getElementById('tableHeader');
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
            }
            
            // Display data
            displayData();
            
            // Setup search
            document.getElementById('searchInput').addEventListener('input', handleSearch);
        }
        
        function displayData() {
            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';
            
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const pageData = filteredData.slice(start, end);
            
            if (pageData.length === 0) {
                const tr = document.createElement('tr');
                const td = document.createElement('td');
                td.colSpan = 10;
                td.style.textAlign = 'center';
                td.style.padding = '20px';
                td.textContent = '데이터가 없습니다';
                tr.appendChild(td);
                tableBody.appendChild(tr);
                return;
            }
            
            const headers = Object.keys(embeddedData[0]).slice(0, 10);
            
            pageData.forEach(row => {
                const tr = document.createElement('tr');
                headers.forEach(header => {
                    const td = document.createElement('td');
                    const value = row[header] || '';
                    td.textContent = value.toString().substring(0, 50);
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });
            
            // Update pagination
            const totalPages = Math.ceil(filteredData.length / rowsPerPage);
            document.getElementById('pageInfo').textContent = `${currentPage} / ${totalPages}`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages;
        }
        
        function handleSearch(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm === '') {
                filteredData = [...embeddedData];
            } else {
                filteredData = embeddedData.filter(row => {
                    return Object.values(row).some(value => 
                        value && value.toString().toLowerCase().includes(searchTerm)
                    );
                });
            }
            
            currentPage = 1;
            displayData();
        }
        
        function nextPage() {
            const totalPages = Math.ceil(filteredData.length / rowsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                displayData();
            }
        }
        
        function prevPage() {
            if (currentPage > 1) {
                currentPage--;
                displayData();
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>'''
    
    # Write the HTML file
    output_file = '5PRS_Dashboard_Standalone.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Standalone dashboard created: {output_file}")
    print(f"📊 Total records embedded: {len(records)}")
    print(f"📁 Files processed: {files_count}")
    print(f"🚀 Open the file directly in your browser - no server needed!")
    
    return output_file

if __name__ == "__main__":
    create_standalone_html()